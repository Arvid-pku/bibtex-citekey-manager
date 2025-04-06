# BibTeX Cite Key Manager

This repository contains two Python scripts designed to help manage BibTeX citation keys and ensure consistency in LaTeX documents:

*   `process_bib.py`: Processes a BibTeX file to:
    *   Identify and count duplicate citation keys.
    *   Deduplicate entries based on title similarity, keeping the most informative entry.
    *   Generate a key mapping (JSON file) to map old keys to the retained best keys.
    *   Output a processed BibTeX file (`processed.bib`) containing only unique entries.
*   `update_tex.py`: Updates a TeX file to use the consistent citation keys from the processed BibTeX file:
    *   Replaces `\supercite{old_key}` citations with `\supercite{best_key}` using the key mapping.
    *   Handles `\supercite{key1, key2, ...}` with comma-separated keys.
    *   Warns about any citation keys in the TeX file that are not found in the processed BibTeX file or key mappings.

## Usage

**Prerequisites:**

*   Python 3.x
*   Install required Python libraries:
    ```bash
    pip install bibtexparser difflib
    ```

**Step-by-step Instructions:**

1.  **Prepare your BibTeX file:**  Combine all your BibTeX files into a single file, e.g., `merged.bib`. This script is designed to handle duplicates within this merged file.
2.  **Run `process_bib.py`:**
    ```bash
    python process_bib.py
    ```
    This script will:
    *   Read `merged.bib` (you can modify `input_bib_file` variable in the script).
    *   Process the BibTeX entries, deduplicate, and generate key mappings.
    *   Save the processed BibTeX entries to `processed.bib`.
    *   Save the key mappings to `key_mapping.json`.
    *   Print key statistics and mappings to the console.
3.  **Prepare your TeX file:** Ensure your LaTeX document uses `\supercite{}` for citations and you want to update the keys in these commands.
4.  **Run `update_tex.py`:**
    ```bash
    python update_tex.py
    ```
    This script will:
    *   Read `main.tex` (you can modify `input_tex_file` variable in the script).
    *   Read `processed.bib` and `key_mapping.json` generated in the previous step.
    *   Replace `\supercite{}` keys in `main.tex` based on the key mappings.
    *   Save the updated TeX file as `main_updated.tex`.
    *   Print warnings for any citation keys in the TeX file that are not found in the BibTeX files.
5.  **Review output files:** Check `processed.bib`, `key_mapping.json`, and `main_updated.tex` to ensure the scripts worked as expected. Pay attention to any warnings printed in the console.

**File Structure:**

*   `process_bib.py`: Python script to process BibTeX files.
*   `update_tex.py`: Python script to update TeX files.
*   `merged.bib` (Input): Your merged BibTeX file (or any name you configure in `process_bib.py`).
*   `processed.bib` (Output): Processed BibTeX file with unique entries.
*   `key_mapping.json` (Output): JSON file containing key mappings from old to best keys.
*   `main.tex` (Input): Your LaTeX TeX file (or any name you configure in `update_tex.py`).
*   `main_updated.tex` (Output): Updated TeX file with consistent citation keys.

**Notes:**

*   **Title Similarity Threshold:**  The `process_bib.py` script uses a title similarity threshold of `0.8` to identify duplicate papers. You can adjust this value in the script if needed.
*   **Entry Richness:** The script determines the "best" entry based on the number of fields. You can customize the `get_entry_richness` function in `process_bib.py` for more sophisticated criteria.
*   **Backup:** Always back up your `merged.bib` and TeX files before running these scripts.
*   **Citation Command:** `update_tex.py` is designed to work with `\supercite{}` command. If you use other citation commands like `\cite`, `\citet`, `\citep`, you'll need to modify the `update_tex.py` script accordingly.
