# BiB Killer

A Python toolkit for managing BibTeX bibliography files. BiB Killer provides command-line tools for merging, deduplicating, comparing BibTeX files, and syncing citations with the INSPIRE-HEP database.

## Features

- **Automatic Deduplication**: Detect and remove duplicate BibTeX entries
- **Batch Processing**: Process entire folders of BibTeX files
- **Citation Key Management**: Extract, sort, and compare citation keys
- **INSPIRE Integration**: Automatically fetch citations from INSPIRE-HEP
- **UTF-8 Support**: Full Unicode support for international characters
- **Robust Error Handling**: Graceful handling of malformed entries

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bib_killer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

All tools are located in the `src/` directory and can be run directly.

### 1. Merge Multiple BibTeX Files

Merge multiple BibTeX files into a single file while removing duplicates.

```bash
python src/commands/merge.py file1.bib file2.bib [file3.bib ...] [-o OUTPUT_FILE] [-k KEYS_FILE]
```

**Options:**
- `-o, --output`: Output BibTeX file (default: `merged.bib`)
- `-k, --keys`: Optional output file for citation keys

**Example:**
```bash
python src/commands/merge.py references/*.bib -o merged.bib -k citation_keys.txt
```

### 2. Process Folder of BibTeX Files

Process all BibTeX files in a folder and merge them into a single file.

```bash
python src/commands/process_folder.py FOLDER_PATH [-o OUTPUT_FILE] [-k KEYS_FILE]
```

**Options:**
- `-o, --output`: Output BibTeX file (default: `merged.bib`)
- `-k, --keys`: Optional output file for citation keys

**Example:**
```bash
python src/commands/process_folder.py references/ -o merged.bib -k citation_keys.txt
```

### 3. Deduplicate Single BibTeX File

Process a single BibTeX file to count and remove duplicate entries.

```bash
python src/commands/deduplicate.py input.bib [-o OUTPUT_FILE]
```

**Options:**
- `-o, --output`: Optional output BibTeX file. If not specified, only statistics will be shown.

**Example:**
```bash
python src/commands/deduplicate.py references.bib -o deduplicated.bib
```

### 4. Compare Citation Keys

Compare citation keys between two text files containing comma-separated keys.

```bash
python src/commands/compare.py keys1.txt keys2.txt [-o OUTPUT_FILE]
```

**Options:**
- `-o, --output`: Output file for comparison results (default: `key_comparison.txt`)

**Example:**
```bash
# First, extract keys from two different bib files
python src/commands/process_folder.py folder1/ -k keys1.txt
python src/commands/process_folder.py folder2/ -k keys2.txt

# Then compare the key files
python src/commands/compare.py keys1.txt keys2.txt -o comparison.txt
```

The comparison results will show:
- Duplicate keys between the files
- Keys only present in the first file
- Keys only present in the second file
- Summary statistics

### 5. Find Duplicate Keys

Find only duplicate citation keys between two text files (simpler output than compare).

```bash
python src/commands/find_duplicates.py keys1.txt keys2.txt [-o OUTPUT_FILE]
```

**Options:**
- `-o, --output`: Output file for duplicate keys (default: `duplicate_keys.txt`)

### 6. Sync Citations with INSPIRE

Sync missing LaTeX cite keys from INSPIRE-HEP into a BibTeX file.

```bash
python src/inspire/sync.py --tex PAPER.tex --bib REFS.bib --report REPORT.json [OPTIONS]
```

**Options:**
- `--tex`: Path to TeX file containing `\cite{}` commands
- `--bib`: Path to target BibTeX file
- `--report`: Path to write JSON report
- `--dry-run`: Do not modify BibTeX file
- `--dedupe-bib`: Remove duplicate BibTeX entries based on DOI, eprint, or title
- `--progress-every N`: Print progress every N processed keys (default: 10)
- `--quiet`: Suppress progress logs

**Example:**
```bash
python src/inspire/sync.py \
  --tex paper/main.tex \
  --bib paper/references.bib \
  --report inspire_report.json \
  --dedupe-bib \
  --progress-every 5
```

**Workflow:**
1. Parses all `\cite*{...}` keys from the TeX file
2. Optionally deduplicates existing BibTeX entries
3. Compares cite keys against existing keys in BibTeX file
4. For missing keys, queries INSPIRE and auto-accepts high-confidence hits
5. Exports BibTeX entries and appends to BibTeX file
6. Generates JSON report with resolved and manual-review items

## Project Structure

```
bib_killer/
├── src/
│   ├── core/              # Core utilities
│   │   └── utils.py       # Shared BibTeX processing functions
│   ├── commands/          # Command-line tools
│   │   ├── merge.py       # Merge multiple files
│   │   ├── deduplicate.py # Deduplicate single file
│   │   ├── process_folder.py  # Process folder of files
│   │   ├── compare.py     # Compare citation keys
│   │   └── find_duplicates.py # Find duplicate keys
│   └── inspire/           # INSPIRE-HEP integration
│       └── sync.py        # Sync citations with INSPIRE
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── README.md             # This file
├── SPEC.md               # Technical specification
├── AGENTS.md             # Agent coding guidelines
├── CLAUDE.md             # Quick reference for AI agents
└── PROJECT_LOG.md        # Development history
```

## Development

### For Contributors

- Read `AGENTS.md` for coding conventions and workflow rules
- Read `SPEC.md` for technical architecture details
- Update `PROJECT_LOG.md` after meaningful changes
- Maintain `.venv` for isolated development environment

### Adding New Commands

1. Create a new script in `src/commands/`
2. Import utilities from `src.core.utils`
3. Use `argparse` for command-line interface
4. Update this README with usage examples
5. Update `SPEC.md` with module description

## Citation Key Format

Tools that sort citation keys expect the format: `Author:YYYY[suffix]`

Example: `Einstein:1905a`, `Feynman:1965`, `Hawking:1974`

Keys without a year are sorted last.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Follow the coding conventions in `AGENTS.md`
2. Test your changes with sample BibTeX files
3. Update documentation as needed
4. Submit a pull request with a clear description

## Support

For issues, questions, or suggestions, please open an issue on the repository.
