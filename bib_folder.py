import argparse
import glob
import os
from bib_utils import get_all_entries, process_bib_entries, write_bib_file

def process_bib_folder(folder_path, output_file, output_keys=None):
    """
    Process all .bib files in a folder and merge them into a single file.
    
    Args:
        folder_path (str): Path to folder containing .bib files
        output_file (str): Path to output .bib file
        output_keys (str, optional): Path to output keys file
    """
    # Get all .bib files in the folder
    bib_files = glob.glob(os.path.join(folder_path, "*.bib"))
    
    if not bib_files:
        print(f"No .bib files found in {folder_path}")
        return
    
    print(f"Found {len(bib_files)} .bib files in {folder_path}")
    
    # Get all entries from input files
    all_entries = get_all_entries(bib_files)
    
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
    
    print(f"Successfully processed {len(bib_files)} files into {output_file}")
    print(f"Total unique entries: {len(unique_entries)}")

def main():
    parser = argparse.ArgumentParser(description='Process all .bib files in a folder')
    parser.add_argument('folder', help='Folder containing .bib files')
    parser.add_argument('-o', '--output', default='merged.bib', help='Output .bib file (default: merged.bib)')
    parser.add_argument('-k', '--keys', help='Output file for citation keys (optional)')
    
    args = parser.parse_args()
    process_bib_folder(args.folder, args.output, args.keys)

if __name__ == '__main__':
    main() 