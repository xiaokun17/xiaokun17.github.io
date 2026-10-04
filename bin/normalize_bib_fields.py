#!/usr/bin/env python3
"""Rewrite the site's BibTeX records with one complete, stable field schema."""

from pathlib import Path

from import_papers import FIELD_ORDER, format_entry, parse_entries


ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "_bibliography" / "papers.bib"


def main() -> None:
    entries = parse_entries(BIB_PATH.read_text(encoding="utf-8"))
    output: list[str] = [
        "% Set visible = {false} to hide a publication; missing values default to true.",
        "% Empty fields are retained so every record follows the same schema.",
        "",
    ]
    current_year = None
    for entry in entries:
        fields = {name: str(entry["fields"].get(name, "")).strip() for name in FIELD_ORDER}
        year = fields["year"] or "Unknown year"
        if year != current_year:
            if current_year is not None:
                output.append("")
            output.extend([f"% {year}", ""])
            current_year = year
        output.append(format_entry(str(entry["type"]), str(entry["key"]), fields))
        output.append("")

    BIB_PATH.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"Normalized {len(entries)} entries with {len(FIELD_ORDER)} fields each.")


if __name__ == "__main__":
    main()
