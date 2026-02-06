import argparse
import re

def sort_keys_by_year(keys):
    """
    Sort citation keys by year (extracted from key format: Author:YYYYsuffix).
    """
    def get_year(key):
        match = re.search(r':(\d{4})', key)
        return int(match.group(1)) if match else 9999
    
    return sorted(keys, key=get_year)

def compare_key_files(file1, file2, output_file):
    """
    Compare citation keys between two txt files containing comma-separated keys.
    
    Args:
        file1 (str): Path to first .txt file with comma-separated keys
        file2 (str): Path to second .txt file with comma-separated keys
        output_file (str): Path to output file for results
    """
    try:
        # Read keys from both files
        with open(file1, 'r') as f:
            keys1 = set(key.strip() for key in f.read().split(','))
        
        with open(file2, 'r') as f:
            keys2 = set(key.strip() for key in f.read().split(','))
        
        # Find duplicate keys
        duplicate_keys = sort_keys_by_year(keys1.intersection(keys2))
        
        # Find unique keys in each file
        only_in_file1 = sort_keys_by_year(keys1 - keys2)
        only_in_file2 = sort_keys_by_year(keys2 - keys1)
        
        # Write results to output file
        with open(output_file, 'w') as f:
            f.write("=== Duplicate Keys ===\n")
            f.write(','.join(duplicate_keys))
            f.write("\n\n=== Only in First File ===\n")
            f.write(','.join(only_in_file1))
            f.write("\n\n=== Only in Second File ===\n")
            f.write(','.join(only_in_file2))
        
        # Print summary
        print(f"\nSummary:")
        print(f"Total keys in first file: {len(keys1)}")
        print(f"Total keys in second file: {len(keys2)}")
        print(f"Duplicate keys: {len(duplicate_keys)}")
        print(f"Keys only in first file: {len(only_in_file1)}")
        print(f"Keys only in second file: {len(only_in_file2)}")
        print(f"\nDetailed results written to: {output_file}")
        
    except Exception as e:
        print(f"Error processing files: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Compare citation keys between two txt files')
    parser.add_argument('file1', help='First .txt file with comma-separated keys')
    parser.add_argument('file2', help='Second .txt file with comma-separated keys')
    parser.add_argument('-o', '--output', default='key_comparison.txt', 
                      help='Output file for results (default: key_comparison.txt)')
    
    args = parser.parse_args()
    compare_key_files(args.file1, args.file2, args.output)

if __name__ == '__main__':
    main() 