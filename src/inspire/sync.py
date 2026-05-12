#!/usr/bin/env python3
"""Sync missing LaTeX cite keys from INSPIRE into a BibTeX file.

Workflow:
1. Parse all \\cite*{...} keys from a TeX file.
2. Optionally deduplicate existing BibTeX entries by DOI, eprint, or title.
3. Compare cite keys against existing keys in a BibTeX file.
4. For missing keys, query INSPIRE and auto-accept only high-confidence hits.
5. Export BibTeX, rewrite entry key to the missing cite key, and append to BibTeX file.
6. Emit a JSON report with resolved, manual-review, and deduplication items.

Example usage:
python3 scripts/sync_inspire_citations.py \
  --tex Chapter4.tex \
  --bib Ch4.bib \
  --report /tmp/ch4_inspire_report.json \
  --progress-every 5 \
  --dedupe-bib

"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INSPIRE_API = "https://inspirehep.net/api/literature"
USER_AGENT = "sync-inspire-citations/1.0 (+local script)"


@dataclass
class Candidate:
    record_id: str
    title: str
    year: str
    texkeys: list[str]
    authors: list[str]
    source_query: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "title": self.title,
            "year": self.year,
            "texkeys": self.texkeys,
            "authors": self.authors,
            "source_query": self.source_query,
            "inspire_url": f"https://inspirehep.net/literature/{self.record_id}",
        }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_cite_keys(tex_text: str) -> set[str]:
    cite_pattern = re.compile(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]*)\}")
    keys: set[str] = set()
    for blob in cite_pattern.findall(tex_text):
        for raw in blob.split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return keys


def extract_bib_keys(bib_text: str) -> set[str]:
    entry_pattern = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)
    return {m.strip() for m in entry_pattern.findall(bib_text)}


def split_bib_entries(bib_text: str) -> list[tuple[str, str]]:
    starts = [m.start() for m in re.finditer(r"^@\w+\{", bib_text, re.MULTILINE)]
    out: list[tuple[str, str]] = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(bib_text)
        chunk = bib_text[start:end].strip()
        m = re.match(r"^@\w+\{([^,]+),", chunk)
        if m:
            out.append((m.group(1).strip(), chunk))
    return out


def normalize_title(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[{}]", "", value)
    value = re.sub(r"\\[a-zA-Z]+\s*", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_field(entry_text: str, field: str) -> str | None:
    quoted = re.search(rf"{field}\s*=\s*\"([^\"]+)\"", entry_text, re.IGNORECASE)
    if quoted:
        return quoted.group(1).strip()

    braced = re.search(rf"{field}\s*=\s*\{{([^}}]+)\}}", entry_text, re.IGNORECASE)
    if braced:
        return braced.group(1).strip()

    return None


def build_existing_index(bib_text: str) -> list[dict[str, str]]:
    index: list[dict[str, str]] = []
    for key, entry in split_bib_entries(bib_text):
        doi = (extract_field(entry, "doi") or "").lower()
        eprint = (extract_field(entry, "eprint") or "").lower()
        title = normalize_title(extract_field(entry, "title") or "")
        index.append(
            {
                "key": key,
                "doi": doi,
                "eprint": eprint,
                "title": title,
            }
        )
    return index


def find_equivalent_key(
    existing_index: list[dict[str, str]],
    *,
    doi: str = "",
    eprint: str = "",
    title: str = "",
) -> str | None:
    doi = doi.lower().strip()
    eprint = eprint.lower().strip()
    title = normalize_title(title)

    for item in existing_index:
        if doi and item["doi"] and item["doi"] == doi:
            return item["key"]
        if eprint and item["eprint"] and item["eprint"] == eprint:
            return item["key"]
        if title and item["title"] and item["title"] == title:
            return item["key"]

    return None


def make_bib_fingerprints(entry: str) -> list[tuple[str, str]]:
    doi = (extract_field(entry, "doi") or "").lower().strip()
    eprint = (extract_field(entry, "eprint") or "").lower().strip()
    title = normalize_title(extract_field(entry, "title") or "")

    fingerprints: list[tuple[str, str]] = []
    if doi:
        fingerprints.append(("doi", doi))
    if eprint:
        fingerprints.append(("eprint", eprint))
    if title:
        fingerprints.append(("title", title))

    return fingerprints


def dedupe_bib_entries(bib_text: str) -> tuple[str, list[dict[str, Any]]]:
    entries = split_bib_entries(bib_text)
    seen: dict[str, str] = {}
    duplicates: list[dict[str, Any]] = []
    keep_chunks: list[str] = []

    for key, entry in entries:
        fingerprints = make_bib_fingerprints(entry)

        duplicate_of = None
        match_basis = None
        match_value = None

        for basis, value in fingerprints:
            fp = f"{basis}:{value}"
            if fp in seen:
                duplicate_of = seen[fp]
                match_basis = basis
                match_value = value
                break

        if duplicate_of:
            duplicates.append(
                {
                    "removed_key": key,
                    "kept_key": duplicate_of,
                    "match_basis": match_basis,
                    "match_value": match_value,
                }
            )
            continue

        keep_chunks.append(entry.strip())

        for basis, value in fingerprints:
            seen[f"{basis}:{value}"] = key

    if not keep_chunks:
        return bib_text, duplicates

    return "\n\n".join(keep_chunks).strip() + "\n", duplicates


def http_get(url: str, timeout: float = 20.0, retries: int = 2) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as err:
            last_err = err
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))

    raise RuntimeError(f"HTTP request failed: {url} ({last_err})")


def inspire_query(query: str, size: int = 5) -> dict[str, Any]:
    params = urllib.parse.urlencode({"q": query, "size": str(size)})
    url = f"{INSPIRE_API}?{params}"
    raw = http_get(url)
    return json.loads(raw)


def check_inspire_connectivity() -> tuple[bool, str | None]:
    params = urllib.parse.urlencode({"q": "texkey:Ji:2013dva", "size": "1"})
    url = f"{INSPIRE_API}?{params}"

    try:
        _ = http_get(url, timeout=4.0, retries=0)
        return True, None
    except Exception as err:
        return False, str(err)


def get_hit_texkeys(hit: dict[str, Any]) -> list[str]:
    metadata = hit.get("metadata", {}) if isinstance(hit, dict) else {}
    texkeys = metadata.get("texkeys", [])
    out: list[str] = []

    for item in texkeys:
        if isinstance(item, dict):
            value = item.get("value")
            if isinstance(value, str):
                out.append(value)
        elif isinstance(item, str):
            out.append(item)

    return out


def get_hit_title(hit: dict[str, Any]) -> str:
    metadata = hit.get("metadata", {}) if isinstance(hit, dict) else {}
    titles = metadata.get("titles", [])

    if titles and isinstance(titles[0], dict):
        return str(titles[0].get("title", "")).strip()

    return ""


def get_hit_year(hit: dict[str, Any]) -> str:
    metadata = hit.get("metadata", {}) if isinstance(hit, dict) else {}

    for field in ("earliest_date", "preprint_date"):
        value = metadata.get(field)
        if isinstance(value, str) and len(value) >= 4:
            return value[:4]

    if isinstance(metadata.get("publication_info"), list):
        pub = metadata["publication_info"]
        if pub and isinstance(pub[0], dict):
            y = pub[0].get("year")
            if y is not None:
                return str(y)

    return ""


def get_hit_authors(hit: dict[str, Any]) -> list[str]:
    metadata = hit.get("metadata", {}) if isinstance(hit, dict) else {}
    authors = metadata.get("authors", [])
    names: list[str] = []

    for author in authors[:5]:
        if isinstance(author, dict):
            name = author.get("full_name")
            if isinstance(name, str):
                names.append(name)

    return names


def get_hit_id(hit: dict[str, Any]) -> str:
    metadata = hit.get("metadata", {}) if isinstance(hit, dict) else {}
    control_number = metadata.get("control_number")

    if control_number is not None:
        return str(control_number)

    recid = hit.get("id")
    if recid is not None:
        return str(recid)

    return ""


def build_candidates(hits: list[dict[str, Any]], source_query: str) -> list[Candidate]:
    candidates: list[Candidate] = []

    for hit in hits:
        record_id = get_hit_id(hit)
        if not record_id:
            continue

        candidates.append(
            Candidate(
                record_id=record_id,
                title=get_hit_title(hit),
                year=get_hit_year(hit),
                texkeys=get_hit_texkeys(hit),
                authors=get_hit_authors(hit),
                source_query=source_query,
            )
        )

    return candidates


def extract_author_year_from_key(key: str) -> tuple[str | None, str | None]:
    m = re.match(r"([A-Za-z]+):(\d{4})", key)
    if m:
        return m.group(1), m.group(2)

    return None, None


def resolve_key_strict(key: str) -> tuple[dict[str, Any] | None, list[Candidate], str | None]:
    all_candidates: list[Candidate] = []

    q1 = f'texkey:"{key}"'
    try:
        result1 = inspire_query(q1, size=5)
        hits1 = result1.get("hits", {}).get("hits", [])
    except Exception as err:
        return None, [], f"query_error: {err}"

    cands1 = build_candidates(hits1, q1)
    all_candidates.extend(cands1)

    if len(hits1) == 1:
        hit = hits1[0]
        texkeys = set(get_hit_texkeys(hit))
        if key in texkeys:
            return hit, all_candidates, None

    q2 = f'"{key}"'
    try:
        result2 = inspire_query(q2, size=5)
        hits2 = result2.get("hits", {}).get("hits", [])
    except Exception as err:
        return None, all_candidates, f"query_error: {err}"

    all_candidates.extend(build_candidates(hits2, q2))

    author, year = extract_author_year_from_key(key)
    if author and year:
        q3 = f'author:"{author}" and date:{year}'
        try:
            result3 = inspire_query(q3, size=5)
            hits3 = result3.get("hits", {}).get("hits", [])
        except Exception as err:
            return None, all_candidates, f"query_error: {err}"

        all_candidates.extend(build_candidates(hits3, q3))

    dedup: dict[str, Candidate] = {}
    for cand in all_candidates:
        dedup[cand.record_id] = cand

    return None, list(dedup.values()), "no_unique_high_confidence_match"


def fetch_bibtex_for_hit(hit: dict[str, Any]) -> str:
    record_id = get_hit_id(hit)
    if not record_id:
        raise RuntimeError("hit missing record id")

    links = hit.get("links", {}) if isinstance(hit, dict) else {}
    bibtex_url = links.get("bibtex")

    if not isinstance(bibtex_url, str) or not bibtex_url:
        bibtex_url = f"{INSPIRE_API}/{record_id}?format=bibtex"

    text = http_get(bibtex_url)

    if "@" not in text:
        raise RuntimeError(f"invalid bibtex payload for record {record_id}")

    return text.strip()


def rewrite_bibtex_key(bibtex: str, new_key: str) -> str:
    pattern = re.compile(r"^(@\w+\s*\{)\s*([^,]+)\s*,", re.MULTILINE)

    if not pattern.search(bibtex):
        raise RuntimeError("cannot locate BibTeX entry key")

    rewritten = pattern.sub(rf"\1{new_key},", bibtex, count=1)
    return rewritten.strip() + "\n"


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--tex", required=True, help="Path to TeX file.")
    parser.add_argument("--bib", required=True, help="Path to target BibTeX file.")
    parser.add_argument("--report", required=True, help="Path to write JSON report.")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify BibTeX file.")

    parser.add_argument(
        "--dedupe-bib",
        action="store_true",
        help="Remove duplicate BibTeX entries based on DOI, eprint, or normalized title.",
    )

    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Print progress every N processed keys. Default: 10.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress logs; only print final summary.",
    )

    return parser.parse_args()


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"

    return f"{s}s"


def maybe_print_progress(
    *,
    quiet: bool,
    current: int,
    total: int,
    key: str,
    resolved_count: int,
    review_count: int,
    start_time: float,
    force: bool = False,
    progress_every: int = 10,
) -> None:
    if quiet:
        return

    if not force and (progress_every <= 0 or current % progress_every != 0):
        return

    elapsed = time.time() - start_time
    avg = elapsed / current if current else 0.0
    eta = avg * (total - current)

    print(
        "[{cur}/{tot}] key={key} resolved={ok} review={review} elapsed={elapsed} eta={eta}".format(
            cur=current,
            tot=total,
            key=key,
            ok=resolved_count,
            review=review_count,
            elapsed=format_duration(elapsed),
            eta=format_duration(eta),
        ),
        flush=True,
    )


def main() -> int:
    args = parse_cli()

    tex_path = Path(args.tex)
    bib_path = Path(args.bib)
    report_path = Path(args.report)

    tex_text = read_text(tex_path)
    bib_text_original = read_text(bib_path)
    bib_text = bib_text_original

    dedup_removed: list[dict[str, Any]] = []
    if args.dedupe_bib:
        bib_text, dedup_removed = dedupe_bib_entries(bib_text)

    cite_keys = sorted(extract_cite_keys(tex_text))
    bib_keys = extract_bib_keys(bib_text)
    missing_keys = sorted(set(cite_keys) - bib_keys)

    existing_index = build_existing_index(bib_text)

    resolved_auto: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    already_present_equivalent: list[dict[str, Any]] = []
    entries_to_append: list[str] = []
    appended_keys: set[str] = set()

    start_time = time.time()
    total_missing = len(missing_keys)

    if not args.quiet:
        print(
            "Start: cite_keys={cite}, bib_before={bib}, missing={missing}, "
            "dedupe_bib={dedupe}, dedup_removed={removed}, dry_run={dry}".format(
                cite=len(cite_keys),
                bib=len(bib_keys),
                missing=total_missing,
                dedupe=args.dedupe_bib,
                removed=len(dedup_removed),
                dry=args.dry_run,
            ),
            flush=True,
        )

    network_ready, network_error = check_inspire_connectivity()

    if not network_ready:
        for i, key in enumerate(missing_keys, start=1):
            needs_review.append(
                {
                    "key": key,
                    "reason": f"network_unreachable: {network_error}",
                    "candidates": [],
                }
            )

            maybe_print_progress(
                quiet=args.quiet,
                current=i,
                total=total_missing,
                key=key,
                resolved_count=len(resolved_auto),
                review_count=len(needs_review),
                start_time=start_time,
                progress_every=args.progress_every,
            )
    else:
        for i, key in enumerate(missing_keys, start=1):
            hit, candidates, err = resolve_key_strict(key)

            if hit is None:
                needs_review.append(
                    {
                        "key": key,
                        "reason": err or "unknown_error",
                        "candidates": [c.to_dict() for c in candidates],
                    }
                )

                maybe_print_progress(
                    quiet=args.quiet,
                    current=i,
                    total=total_missing,
                    key=key,
                    resolved_count=len(resolved_auto),
                    review_count=len(needs_review),
                    start_time=start_time,
                    progress_every=args.progress_every,
                )
                continue

            try:
                bibtex_raw = fetch_bibtex_for_hit(hit)
                bibtex_new = rewrite_bibtex_key(bibtex_raw, key)
            except Exception as fetch_err:
                needs_review.append(
                    {
                        "key": key,
                        "reason": f"bibtex_fetch_error: {fetch_err}",
                        "candidates": [c.to_dict() for c in candidates],
                    }
                )

                maybe_print_progress(
                    quiet=args.quiet,
                    current=i,
                    total=total_missing,
                    key=key,
                    resolved_count=len(resolved_auto),
                    review_count=len(needs_review),
                    start_time=start_time,
                    progress_every=args.progress_every,
                )
                continue

            doi = extract_field(bibtex_new, "doi") or ""
            eprint = extract_field(bibtex_new, "eprint") or ""
            title = extract_field(bibtex_new, "title") or ""

            eq_key = find_equivalent_key(existing_index, doi=doi, eprint=eprint, title=title)
            if eq_key and eq_key != key:
                already_present_equivalent.append(
                    {
                        "requested_key": key,
                        "existing_key": eq_key,
                        "match_basis": "doi_or_eprint_or_title",
                    }
                )

            if key in bib_keys or key in appended_keys:
                continue

            entries_to_append.append(bibtex_new.strip())
            appended_keys.add(key)

            resolved_auto.append(
                {
                    "key": key,
                    "record_id": get_hit_id(hit),
                    "inspire_url": f"https://inspirehep.net/literature/{get_hit_id(hit)}",
                    "title": get_hit_title(hit),
                    "year": get_hit_year(hit),
                }
            )

            maybe_print_progress(
                quiet=args.quiet,
                current=i,
                total=total_missing,
                key=key,
                resolved_count=len(resolved_auto),
                review_count=len(needs_review),
                start_time=start_time,
                progress_every=args.progress_every,
            )

    if (
        total_missing > 0
        and not args.quiet
        and (args.progress_every <= 0 or total_missing % args.progress_every != 0)
    ):
        maybe_print_progress(
            quiet=args.quiet,
            current=total_missing,
            total=total_missing,
            key=missing_keys[-1],
            resolved_count=len(resolved_auto),
            review_count=len(needs_review),
            start_time=start_time,
            force=True,
            progress_every=args.progress_every,
        )

    if not args.dry_run:
        if args.dedupe_bib:
            bib_path.write_text(bib_text.rstrip() + "\n", encoding="utf-8")

        if entries_to_append:
            with bib_path.open("a", encoding="utf-8") as fh:
                fh.write("\n\n")
                fh.write("\n\n".join(entries_to_append))
                fh.write("\n")

    final_bib_keys = set(bib_keys) | appended_keys
    missing_after_write = sorted(set(cite_keys) - final_bib_keys)

    report = {
        "tex_file": str(tex_path),
        "bib_file": str(bib_path),
        "dry_run": bool(args.dry_run),
        "dedupe_bib": bool(args.dedupe_bib),
        "counts": {
            "cite_keys": len(cite_keys),
            "bib_keys_before": len(extract_bib_keys(bib_text_original)),
            "bib_keys_after_dedupe": len(bib_keys),
            "missing_before": len(missing_keys),
            "resolved_auto": len(resolved_auto),
            "needs_review": len(needs_review),
            "already_present_equivalent": len(already_present_equivalent),
            "dedup_removed": len(dedup_removed),
            "appended_entries": 0 if args.dry_run else len(entries_to_append),
            "missing_after_write": len(missing_after_write),
        },
        "missing_keys": missing_keys,
        "resolved_auto": resolved_auto,
        "needs_review": needs_review,
        "already_present_equivalent": already_present_equivalent,
        "dedup_removed": dedup_removed,
        "missing_after_write": missing_after_write,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    print(
        "Done: cite_keys={cite}, bib_before={bib_before}, bib_after_dedupe={bib_after}, "
        "missing_before={miss}, resolved_auto={ok}, needs_review={review}, "
        "dedup_removed={dedup}, appended={append}, missing_after={after}".format(
            cite=len(cite_keys),
            bib_before=len(extract_bib_keys(bib_text_original)),
            bib_after=len(bib_keys),
            miss=len(missing_keys),
            ok=len(resolved_auto),
            review=len(needs_review),
            dedup=len(dedup_removed),
            append=0 if args.dry_run else len(entries_to_append),
            after=len(missing_after_write),
        )
    )
    print(f"Report written to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())