# -----------------------------------------------------------
# Diablo IV Patch Notes Parser
# -----------------------------------------------------------
# This script reads the patch notes HTML file (treated as text)
# and extracts structured change records.
#
# Each row in the output represents ONE logical change.
# -----------------------------------------------------------


# ----------------------------
# Import required libraries
# ----------------------------

import re              # For pattern matching (regex)
import pandas as pd    # For creating structured data tables


# -----------------------------------------------------------
# FUNCTION: parse_patch_notes
# -----------------------------------------------------------
def parse_patch_notes(filepath):
    '''
    Reads the Diablo IV patch notes file.
    Parses patch headers, sections, and change entries.
    Merges "Previous" and "Now" lines into single comparison entries.
    Returns a clean pandas DataFrame.
    '''

    # ----------------------------
    # STEP 1: Read file
    # ----------------------------

    # Open the file and read everything as text
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split file into lines and remove empty lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # ----------------------------
    # STEP 2: Define patch header pattern
    # ----------------------------

    # This regex finds:
    # Example: 2.5.3 Build #70356 (All Platforms)—January 28, 2026
    patch_pattern = re.compile(r"(\d+\.\d+\.\d+)\s+Build\s+#(\d+).*—(.+)")

    # ----------------------------
    # STEP 3: Prepare storage
    # ----------------------------

    records = []

    # These track context while looping
    current_patch = None
    current_build = None
    current_date = None
    current_section = None
    current_entity = None

    # ----------------------------
    # STEP 4: Loop through lines
    # ----------------------------

    i = 0

    while i < len(lines):

        line = lines[i]

        # ----------------------------
        # A) Detect Patch Header
        # ----------------------------
        patch_match = patch_pattern.match(line)

        if patch_match:
            current_patch = patch_match.group(1)
            current_build = patch_match.group(2)
            current_date = patch_match.group(3)
            i += 1
            continue

        # ----------------------------
        # B) Detect Major Sections
        # ----------------------------
        if line in [
            "Bug Fixes", "Game Updates", "Balance Update",
            "Base Game", "Expansion", "Accessibility",
            "Skills", "Passives", "Items",
            "Legendary Aspects", "Paragon",
            "Tempering", "Miscellaneous"
        ]:
            current_section = line
            i += 1
            continue

        # ----------------------------
        # C) Detect "Previous" block
        # ----------------------------
        if line.startswith("Previous"):

            previous_text = line.replace("Previous:", "").strip()

            # Look ahead to see if next line is "Now"
            if i + 1 < len(lines) and lines[i + 1].startswith("Now"):

                now_text = lines[i + 1].replace("Now:", "").strip()

                # Store as ONE comparison record
                records.append({
                    "patch": current_patch,
                    "build": current_build,
                    "date": current_date,
                    "section": current_section,
                    "change_type": "comparison",
                    "previous": previous_text,
                    "now": now_text,
                    "full_text": f"Changed from {previous_text} to {now_text}"
                })

                i += 2
                continue

        # ----------------------------
        # D) All other lines are single change entries
        # ----------------------------
        records.append({
            "patch": current_patch,
            "build": current_build,
            "date": current_date,
            "section": current_section,
            "change_type": "single",
            "previous": None,
            "now": None,
            "full_text": line
        })

        i += 1

    # ----------------------------
    # STEP 5: Convert to DataFrame
    # ----------------------------
    df = pd.DataFrame(records)

    return df


# -----------------------------------------------------------
# MAIN EXECUTION BLOCK
# -----------------------------------------------------------
if __name__ == "__main__":

    # ----------------------------
    # Define input file
    # ----------------------------
    input_file = "Diablo_IV_Patch_Notes.html"

    # ----------------------------
    # Run parser
    # ----------------------------
    df = parse_patch_notes(input_file)

    # ----------------------------
    # Save output
    # ----------------------------
    df.to_csv("patch_changes_clean.csv", index=False)

    print("✅ Parsing complete.")
    print("Total records extracted:", len(df))