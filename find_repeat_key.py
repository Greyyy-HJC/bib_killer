import argparse

def find_duplicate_keys(file1, file2, output_file):
    """
    Find duplicate citation keys between two txt files containing comma-separated keys.
    
    Args:
        file1 (str): Path to first .txt file with comma-separated keys
        file2 (str): Path to second .txt file with comma-separated keys
        output_file (str): Path to output file for duplicate keys
    """
    try:
        # Read keys from both files
        with open(file1, 'r') as f:
            keys1 = set(key.strip() for key in f.read().split(','))
        
        with open(file2, 'r') as f:
            keys2 = set(key.strip() for key in f.read().split(','))
        
        # Find duplicate keys
        duplicate_keys = sorted(keys1.intersection(keys2))
        
        if not duplicate_keys:
            print("No duplicate keys found between the files.")
            return
        
        # Write duplicate keys to output file
        with open(output_file, 'w') as f:
            f.write(','.join(duplicate_keys))
        
        print(f"Found {len(duplicate_keys)} duplicate keys")
        print(f"Duplicate keys written to: {output_file}")
        
    except Exception as e:
        print(f"Error processing files: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Find duplicate citation keys between two txt files')
    parser.add_argument('file1', help='First .txt file with comma-separated keys')
    parser.add_argument('file2', help='Second .txt file with comma-separated keys')
    parser.add_argument('-o', '--output', default='duplicate_keys.txt', 
                      help='Output file for duplicate keys (default: duplicate_keys.txt)')
    
    args = parser.parse_args()
    find_duplicate_keys(args.file1, args.file2, args.output)

if __name__ == '__main__':
    main()
