import argparse
from bib_utils import get_all_entries, process_bib_entries, write_bib_file

def merge_bib_files(input_files, output_file, output_keys=None):
    """
    Merge multiple .bib files and remove duplicates.
    
    Args:
        input_files (list): List of input .bib file paths
        output_file (str): Path to output .bib file
        output_keys (str, optional): Path to output keys file
    """
    # Get all entries from input files
    all_entries = get_all_entries(input_files)
    
    # Process entries to remove duplicates
    unique_entries = process_bib_entries(all_entries)
    
    # Write deduplicated bibtex
    write_bib_file(list(unique_entries.values()), output_file)
    
    # Write keys if requested
    if output_keys:
        unique_keys = sorted(unique_entries.keys())
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
