import pandas as pd
from bs4 import BeautifulSoup
import re

# Load HTML file
with open("data/raw_patch_notes.html", "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "lxml")

# Container for extracted rows
rows = []

current_patch_id = None
current_patch_date = None
current_section = None

# Example: adjust these tag names after inspecting your HTML
for element in soup.find_all(["h2", "h3", "ul", "li"]):

    # PATCH HEADER (e.g., h2 with "Patch 1.1.0 – July 20, 2023")
    if element.name == "h2":
        text = element.get_text(strip=True)

        # Extract patch number
        patch_match = re.search(r"Patch\s*([\d\.]+)", text)
        date_match = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)

        if patch_match:
            current_patch_id = patch_match.group(1)

        if date_match:
            current_patch_date = pd.to_datetime(date_match.group(1))

        current_section = None

    # SECTION HEADER (e.g., "Barbarian", "General", "Bug Fixes")
    elif element.name == "h3":
        current_section = element.get_text(strip=True)

    # BULLET POINT
    elif element.name == "li":
        bullet_text = element.get_text(strip=True)

        rows.append({
            "patch_id": current_patch_id,
            "patch_date": current_patch_date,
            "section_header": current_section,
            "bullet_text": bullet_text
        })

# Create DataFrame
df = pd.DataFrame(rows)

# Drop empty rows if any
df = df.dropna(subset=["bullet_text"])

# Save CSV
df.to_csv("data/processed/patch_bullets.csv", index=False)

print("Extraction complete. Rows:", len(df))