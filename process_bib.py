import bibtexparser
from difflib import SequenceMatcher
import json

def normalize_title(title):
    """
    Normalize the title by removing curly braces, unnecessary spaces, and converting to lowercase.
    """
    title = title.replace('{', '').replace('}', '').strip().lower()
    return title

def get_entry_richness(entry):
    """
    Evaluate the richness of a BibTeX entry, simply by counting the number of fields.
    More complex criteria can be added, e.g., prioritizing the presence of certain fields.
    """
    richness = 0
    for field in entry:
        if field != 'ID' and entry[field]: # Exclude ID and empty fields
            richness += 1
    return richness

def find_best_entry(entries):
    """
    Find the most informative BibTeX entry from a set of duplicate papers.
    """
    best_entry = None
    max_richness = -1
    for entry in entries:
        richness = get_entry_richness(entry)
        if richness > max_richness:
            max_richness = richness
            best_entry = entry
    return best_entry

def process_bib_file(input_bib_file, output_bib_file="processed.bib", output_mapping_file="key_mapping.json"):
    """
    Process BibTeX file:
    1. Count key occurrences.
    2. Retain the most informative entry for each paper.
    3. Establish key mappings and save results to files.
    """
    with open(input_bib_file, 'r', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
        entries = bib_database.entries

    title_to_entries = {} # Group entries by normalized title
    key_counts = {} # Count occurrences of each key
    key_mapping = {} # Store mappings from old keys to the best key

    for entry in entries:
        key = entry['ID']
        title = entry.get('title', '') # Some entries might not have a title
        normalized_title = normalize_title(title)

        key_counts[key] = key_counts.get(key, 0) + 1 # Count key occurrences

        if normalized_title: # Group only when title exists, handle entries without titles
            if normalized_title not in title_to_entries:
                title_to_entries[normalized_title] = []
            title_to_entries[normalized_title].append(entry)


    processed_entries = [] # Store processed unique entries
    for normalized_title, entry_list in title_to_entries.items():
        if len(entry_list) > 1: # If multiple entries for the same title, consider them duplicates
            print(f"发现重复论文 (标题相似: '{normalized_title}')，共 {len(entry_list)} 个条目，keys分别为: {[e['ID'] for e in entry_list]}")
            print(f"Duplicate papers found (similar title: '{normalized_title}'), total {len(entry_list)} entries, keys are: {[e['ID'] for e in entry_list]}")

            # Further filter using title similarity to avoid unrelated entries being misjudged as duplicates
            similar_entries_group = []
            for i in range(len(entry_list)):
                is_similar_group = True
                if similar_entries_group: # If group exists, compare title similarity with the first entry in the group
                    similarity = SequenceMatcher(None, normalize_title(similar_entries_group[0].get('title', '')), normalize_title(entry_list[i].get('title', ''))).ratio()
                    if similarity < 0.8: # Set a title similarity threshold, e.g., 0.8, adjust as needed
                        is_similar_group = False
                if is_similar_group:
                    similar_entries_group.append(entry_list[i])

            if len(similar_entries_group) > 1: # Re-check the number of similar groups to ensure true duplicates
                best_entry = find_best_entry(similar_entries_group) # Find the best entry from the similar group
                processed_entries.append(best_entry)
                best_key = best_entry['ID']

                for entry in similar_entries_group: # Establish mappings for all old keys to the best key
                    old_key = entry['ID']
                    if old_key != best_key:
                        key_mapping[old_key] = best_key
                        print(f"  - Key '{old_key}' 映射到最佳Key '{best_key}'")
                        print(f"  - Key '{old_key}' mapped to best Key '{best_key}'")
            else: # If only one entry after similarity filtering, add it to processed entries, even if not truly duplicate
                processed_entries.append(similar_entries_group[0]) # Or entry_list[0] if not filtering by similarity
        else: # If only one entry for the title, directly add it to processed entries
            processed_entries.append(entry_list[0])

    unique_key_counts = {} # Count unique keys after processing (should all be 1 unless original bib file has issues)
    for entry in processed_entries:
        key = entry['ID']
        unique_key_counts[key] = unique_key_counts.get(key, 0) + 1

    print("\nKey Statistics (Before Processing):")
    for key, count in key_counts.items():
        if count > 1:
            print(f"  - Key '{key}': {count} times")

    print("\nKey Statistics (Unique Keys After Processing):")
    for key, count in unique_key_counts.items():
        if count > 1: # Theoretically, no duplicate keys after processing
            print(f"  - Key '{key}': {count} times (Warning: Duplicate keys still exist after processing)")
        # else: # Optionally output unique key statistics, comment out if not needed
        #     print(f"  - Key '{key}': {count} times")


    print("\nKey Mappings:")
    if not key_mapping:
        print("  No Key Mappings (No duplicate papers found or keys are the same)")
    else:
        for old_key, best_key in key_mapping.items():
            print(f"  - '{old_key}' -> '{best_key}'")

    # Write processed bib entries back to processed.bib
    processed_bib_database = bibtexparser.bibdatabase.BibDatabase()
    processed_bib_database.entries = processed_entries
    with open(output_bib_file, 'w', encoding='utf-8') as bibfile:
        bibtexparser.dump(processed_bib_database, bibfile)
        print(f"\nProcessed BibTeX file saved to {output_bib_file}")

    # Save key_mapping to key_mapping.json
    with open(output_mapping_file, 'w', encoding='utf-8') as mapping_file:
        json.dump(key_mapping, mapping_file, indent=4, ensure_ascii=False) # Use indent=4 and ensure_ascii=False for readable JSON
        print(f"Key mappings saved to {output_mapping_file}")


    return key_counts, key_mapping, processed_entries


if __name__ == "__main__":
    input_bib_file = "merged.bib" # Replace with your bib file path
    output_bib_file = "processed.bib" # Output bib file path
    output_mapping_file = "key_mapping.json" # Output key mapping file path
    key_counts, key_mapping, processed_entries = process_bib_file(input_bib_file, output_bib_file, output_mapping_file)

    print("\nProcessing completed. Key mappings generated and saved to JSON file, processed BibTeX file saved.")
    # You can further use the key_mapping dictionary here, e.g., in the second script to update TeX files
