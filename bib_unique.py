import argparse
from bib_utils import get_all_entries, process_bib_entries, write_bib_file

def process_bib_file(input_file, output_file=None):
    """
    Process a .bib file to count and deduplicate references.
    
    Args:
        input_file (str): Path to input .bib file
        output_file (str, optional): Path to output .bib file. If None, only count references.
    """
    try:
        # Get all entries from input file
        all_entries = get_all_entries([input_file])
        total_entries = len(all_entries)
        
        # Process entries to remove duplicates
        unique_entries = process_bib_entries(all_entries)
        unique_count = len(unique_entries)
        
        # Print statistics
        print(f"\nStatistics for {input_file}:")
        print(f"Total entries: {total_entries}")
        print(f"Unique entries: {unique_count}")
        print(f"Duplicate entries: {total_entries - unique_count}")
        
        # If output file is specified, write deduplicated entries
        if output_file:
            write_bib_file(list(unique_entries.values()), output_file)
            print(f"\nDeduplicated entries written to: {output_file}")
            
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Count and deduplicate references in a .bib file')
    parser.add_argument('input_file', help='Input .bib file')
    parser.add_argument('-o', '--output', help='Output .bib file (optional)')
    
    args = parser.parse_args()
    process_bib_file(args.input_file, args.output)

if __name__ == '__main__':
    main()
