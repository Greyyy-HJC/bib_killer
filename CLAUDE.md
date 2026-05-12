# CLAUDE.md

Start here when working in this repository.

Read `AGENTS.md` first and follow it as the primary source of coding and workflow rules.

Use `SPEC.md` for the project map.
Use `PROJECT_LOG.md` for recent development history when relevant.

## Quick Context

**bib_killer** is a Python toolkit for BibTeX bibliography management. It provides command-line tools for merging, deduplicating, and comparing BibTeX files, plus integration with the INSPIRE-HEP database for automated citation management.

## Common Tasks

- **Add a new command**: Place in `src/commands/`, use existing commands as templates
- **Modify core utilities**: Edit `src/core/utils.py`, ensure backward compatibility
- **Update INSPIRE integration**: Modify `src/inspire/sync.py`, respect API rate limits
- **Fix a bug**: Check `PROJECT_LOG.md` for related history, add test case if possible

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Running Commands

All tools can be run directly:

```bash
python src/commands/merge.py --help
python src/inspire/sync.py --help
```
