import re
import bibtexparser

def sort_keys_by_year(keys):
    """
    Sort citation keys by year (extracted from key format: Author:YYYYsuffix).
    
    Args:
        keys (list or set): List/set of citation keys
        
    Returns:
        list: Sorted list of keys by year (early to late)
    """
    def get_year(key):
        match = re.search(r':(\d{4})', key)
        return int(match.group(1)) if match else 9999
    
    return sorted(keys, key=get_year)

def process_bib_entries(entries):
    """
    Process bibtex entries to remove duplicates.
    
    Args:
        entries (list): List of bibtex entries
        
    Returns:
        dict: Dictionary of unique entries with ID as key
    """
    unique_entries = {}
    for entry in entries:
        unique_entries[entry['ID']] = entry
    return unique_entries

def write_bib_file(entries, output_file):
    """
    Write bibtex entries to a file.
    
    Args:
        entries (list): List of bibtex entries
        output_file (str): Path to output file
    """
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.indent = '    '  # Set indentation
    writer.order_entries_by = ('ID',)  # Sort by ID
    
    with open(output_file, 'w', encoding='utf-8') as bibfile:
        bibfile.write(writer.write(db))

def get_all_entries(input_files):
    """
    Get all entries from multiple bib files.
    
    Args:
        input_files (list): List of input .bib file paths
        
    Returns:
        list: List of all entries from all files
    """
    all_entries = []
    for fname in input_files:
        try:
            with open(fname, encoding='utf-8') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
                all_entries.extend(bib_database.entries)
        except Exception as e:
            print(f"Error processing {fname}: {str(e)}")
    return all_entries 