import argparse
import re
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data/raw/patch_notes/Diablo_IV_Patch_Notes.html"
DEFAULT_OUTPUT = REPO_ROOT / "data/interim/patch_notes/diablo_iv_patch_notes_clean.csv"


def parse_patch_notes(filepath: Path) -> pd.DataFrame:
    """Parse raw patch notes into structured change rows."""
    text = filepath.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    patch_pattern = re.compile(r"(\d+\.\d+\.\d+)\s+Build\s+#(\d+).*—(.+)")

    records = []
    current_patch = None
    current_build = None
    current_date = None
    current_section = None

    i = 0
    while i < len(lines):
        line = lines[i]
        patch_match = patch_pattern.match(line)

        if patch_match:
            current_patch = patch_match.group(1)
            current_build = patch_match.group(2)
            current_date = patch_match.group(3)
            i += 1
            continue

        if line in [
            "Bug Fixes",
            "Game Updates",
            "Balance Update",
            "Base Game",
            "Expansion",
            "Accessibility",
            "Skills",
            "Passives",
            "Items",
            "Legendary Aspects",
            "Paragon",
            "Tempering",
            "Miscellaneous",
        ]:
            current_section = line
            i += 1
            continue

        if line.startswith("Previous"):
            previous_text = line.replace("Previous:", "").strip()
            if i + 1 < len(lines) and lines[i + 1].startswith("Now"):
                now_text = lines[i + 1].replace("Now:", "").strip()
                records.append(
                    {
                        "patch": current_patch,
                        "build": current_build,
                        "date": current_date,
                        "section": current_section,
                        "change_type": "comparison",
                        "previous": previous_text,
                        "now": now_text,
                        "full_text": f"Changed from {previous_text} to {now_text}",
                    }
                )
                i += 2
                continue

        records.append(
            {
                "patch": current_patch,
                "build": current_build,
                "date": current_date,
                "section": current_section,
                "change_type": "single",
                "previous": None,
                "now": None,
                "full_text": line,
            }
        )
        i += 1

    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Diablo IV patch notes.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = parse_patch_notes(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Wrote: {args.output}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
