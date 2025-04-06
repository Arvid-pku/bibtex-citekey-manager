import re
import bibtexparser
import json

def update_tex_file(input_tex_file, output_tex_file, key_mapping, processed_entries):
    """
    Read TeX file, replace \supercite{old_key1, old_key2, ...} with \supercite{best_key1, best_key2, ...}
    Handles comma-separated multiple keys in \supercite{}, ignoring spaces.
    If a key is not in key_mapping, check in processed_entries, warn if still not found.
    """
    unknown_keys = set() # Store keys in TeX file but not found in key_mapping or processed_entries
    processed_bib_keys = {entry['ID'] for entry in processed_entries} # Set of keys from processed_entries for quick lookup

    with open(input_tex_file, 'r', encoding='utf-8') as tex_file:
        tex_content = tex_file.read()

    def replace_key(match):
        keys_str = match.group(1) # Extract key string from \supercite{} (may contain commas and spaces)
        old_keys = [key.strip() for key in keys_str.split(',')] # Split key string by commas, remove spaces

        processed_keys = []
        for old_key in old_keys:
            if old_key in key_mapping:
                best_key = key_mapping[old_key]
                processed_keys.append(best_key) # Use best key
            elif old_key in processed_bib_keys:
                processed_keys.append(old_key) # Found in processed_entries, keep original key, no replacement
            else:
                unknown_keys.add(old_key) # Record unknown key (not in key_mapping or processed_entries)
                processed_keys.append(old_key) # Keep original key for warning output

        updated_keys_str = ', '.join(processed_keys) # Join processed keys with comma and space
        return r'\supercite{' + updated_keys_str + r'}' # Return updated \supercite{}

    # Use regex to find \supercite{key1, key2, ...} and replace
    updated_tex_content = re.sub(r'\\supercite\{([^}]+)\}', replace_key, tex_content)

    if unknown_keys:
        print("\nWarning: The following keys are referenced by \\supercite in the TeX file but not found in BibTeX file processed.bib and key mappings key_mapping.json:")
        for key in unknown_keys:
            print(f"  - '{key}'")

    with open(output_tex_file, 'w', encoding='utf-8') as tex_outfile:
        tex_outfile.write(updated_tex_content)
        print(f"\nUpdated TeX file saved to {output_tex_file}")


if __name__ == "__main__":
    input_tex_file = "main.tex" # Replace with your tex file path
    output_tex_file = "main_updated.tex" # Replace with desired output tex file path
    bib_file_path = "processed.bib" # Path to processed bib file
    mapping_file_path = "key_mapping.json" # Path to key mapping file

    # Read processed_entries from processed.bib file
    with open(bib_file_path, 'r', encoding='utf-8') as bibfile:
        bib_database = bibtexparser.load(bibfile)
        processed_entries_from_bib = bib_database.entries

    # Read key_mapping_from_bib from key_mapping.json file
    with open(mapping_file_path, 'r', encoding='utf-8') as mapping_file:
        key_mapping_from_bib = json.load(mapping_file)

    update_tex_file(input_tex_file, output_tex_file, key_mapping_from_bib, processed_entries_from_bib)

    print("\nTeX file update script completed.")
