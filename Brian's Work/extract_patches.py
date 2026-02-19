from bs4 import BeautifulSoup

with open("raw_patch_notes.html", "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "html.parser")

print("\n===== SEARCHING FOR 'Patch' IN TEXT =====\n")

matches = soup.find_all(string=lambda text: text and "Patch" in text)

for m in matches[:20]:
    print(m.strip())