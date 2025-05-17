# BiB Killer

A collection of Python tools for managing BibTeX files, including merging, deduplication, and citation key extraction.

## Requirements

- Python 3.x
- bibtexparser

Install dependencies:
```bash
pip install bibtexparser
```

## Tools

### 1. Process BibTeX Folder (`bib_folder.py`)

Processes all BibTeX files in a folder and merges them into a single file while removing duplicates.

```bash
python bib_folder.py FOLDER_PATH [-o OUTPUT_FILE] [-k KEYS_FILE]
```

Options:
- `-o, --output`: Output BibTeX file (default: merged.bib)
- `-k, --keys`: Optional output file for citation keys

Example:
```bash
python bib_folder.py references/ -o merged.bib -k citation_keys.txt
```

### 2. Merge BibTeX Files (`bib_joint.py`)

Merges multiple BibTeX files into a single file while removing duplicates.

```bash
python bib_joint.py file1.bib file2.bib [file3.bib ...] [-o OUTPUT_FILE] [-k KEYS_FILE]
```

Options:
- `-o, --output`: Output BibTeX file (default: merged.bib)
- `-k, --keys`: Optional output file for citation keys

Example:
```bash
python bib_joint.py references/*.bib -o merged.bib -k citation_keys.txt
```

### 3. Deduplicate Single BibTeX File (`bib_unique.py`)

Processes a single BibTeX file to count and remove duplicate entries.

```bash
python bib_unique.py input.bib [-o OUTPUT_FILE]
```

Options:
- `-o, --output`: Optional output BibTeX file. If not specified, only statistics will be shown.

Example:
```bash
python bib_unique.py references.bib -o deduplicated.bib
```

## Features

- Automatic duplicate detection and removal
- Citation key extraction
- Statistics on total and unique entries
- Consistent formatting of output files
- UTF-8 encoding support
- Error handling for file operations
- Support for processing entire folders of BibTeX files

## Code Structure

- `bib_utils.py`: Shared utility functions for BibTeX processing
- `bib_folder.py`: Tool for processing all BibTeX files in a folder
- `bib_joint.py`: Tool for merging multiple BibTeX files
- `bib_unique.py`: Tool for processing single BibTeX files

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 