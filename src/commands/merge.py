#!/usr/bin/env python3
"""Merge multiple BibTeX files and remove duplicates."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import get_all_entries, process_bib_entries, write_bib_file, sort_keys_by_year


def merge_bib_files(input_files, output_file, output_keys=None):
    """
    Merge multiple .bib files and remove duplicates.
    
    Args:
        input_files (list): List of input .bib file paths
        output_file (str): Path to output .bib file
        output_keys (str, optional): Path to output keys file
    """
    all_entries = get_all_entries(input_files)
    unique_entries = process_bib_entries(all_entries)
    write_bib_file(list(unique_entries.values()), output_file)
    
    if output_keys:
        unique_keys = sort_keys_by_year(unique_entries.keys())
        with open(output_keys, 'w') as f:
            f.write(','.join(unique_keys))
        print(f"Citation keys written to: {output_keys}")
    
    print(f"Successfully merged {len(input_files)} files into {output_file}")
    print(f"Total unique entries: {len(unique_entries)}")


def main():
    parser = argparse.ArgumentParser(description='Merge multiple .bib files and remove duplicates')
    parser.add_argument('input_files', nargs='+', help='Input .bib files')
    parser.add_argument('-o', '--output', default='merged.bib', help='Output .bib file (default: merged.bib)')
    parser.add_argument('-k', '--keys', help='Output file for citation keys (optional)')
    
    args = parser.parse_args()
    merge_bib_files(args.input_files, args.output, args.keys)


if __name__ == '__main__':
    main()
