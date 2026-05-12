# SPEC.md

## Project Overview

**bib_killer** is a Python toolkit for managing BibTeX bibliography files. It provides utilities for merging, deduplicating, comparing, and synchronizing BibTeX entries across files and with the INSPIRE-HEP database.

## Directory Structure

```
bib_killer/
├── src/
│   ├── core/
│   │   └── utils.py           # Shared utilities for BibTeX processing
│   ├── commands/
│   │   ├── merge.py           # Merge multiple BibTeX files
│   │   ├── deduplicate.py     # Remove duplicates from a single file
│   │   ├── process_folder.py  # Process entire folders of BibTeX files
│   │   ├── compare.py         # Compare citation keys between files
│   │   └── find_duplicates.py # Find duplicate keys between files
│   └── inspire/
│       └── sync.py            # Sync citations with INSPIRE-HEP
├── examples/                   # Sample BibTeX files for testing
├── .venv/                      # Local Python virtual environment
├── requirements.txt            # Python dependencies
└── *.md                        # Documentation files
```

## Core Modules

### `src/core/utils.py`

Shared utility functions used across all commands:

- `sort_keys_by_year()` - Sort citation keys chronologically
- `process_bib_entries()` - Remove duplicate entries by ID
- `write_bib_file()` - Write BibTeX database to file
- `get_all_entries()` - Load entries from multiple BibTeX files

### `src/commands/`

Command-line tools for common BibTeX operations:

- **merge.py** - Merge multiple BibTeX files with deduplication
- **deduplicate.py** - Remove duplicates from a single BibTeX file
- **process_folder.py** - Process all BibTeX files in a directory
- **compare.py** - Full comparison report of citation keys between two files
- **find_duplicates.py** - Find only duplicate keys between two files

### `src/inspire/sync.py`

Advanced tool for syncing BibTeX citations with the INSPIRE-HEP database:

- Parse LaTeX `\cite{}` keys from TeX files
- Query INSPIRE for missing entries
- Auto-resolve high-confidence matches
- Deduplicate existing BibTeX by DOI/eprint/title
- Generate JSON reports for manual review

## Entry Points

All command-line tools are designed to be run directly as Python scripts:

```bash
python src/commands/merge.py file1.bib file2.bib -o merged.bib
python src/commands/process_folder.py references/ -o all_refs.bib
python src/inspire/sync.py --tex paper.tex --bib references.bib --report report.json
```

## Key Features

- **Deduplication**: Automatic detection and removal of duplicate entries
- **Citation Key Management**: Extract, sort, and compare citation keys
- **Folder Processing**: Batch process multiple BibTeX files
- **INSPIRE Integration**: Query and sync with INSPIRE-HEP database
- **UTF-8 Support**: Full Unicode support for international characters
- **Robust Error Handling**: Graceful handling of malformed entries

## Dependencies

- `bibtexparser` - BibTeX file parsing and writing
- Python 3.7+ standard library

## Design Principles

- **Modularity**: Core utilities separated from command implementations
- **Single Responsibility**: Each command does one thing well
- **Composability**: Commands can be chained in workflows
- **No External Config**: All options via command-line arguments
- **Idempotent Operations**: Safe to run multiple times
