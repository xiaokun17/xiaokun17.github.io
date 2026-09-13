#!/usr/bin/env python3
"""Bind BibTeX publication entries to their matching preview images."""

from __future__ import annotations

import re
from pathlib import Path


ENTRY_RE = re.compile(r"(?ms)^@\w+\{.*?^\}")
KEY_RE = re.compile(r"(?m)^@\w+\{([^,]+),")
PDF_RE = re.compile(r"(?m)^  pdf\s*=\s*\{([^}\r\n]*)\}")

SELECTED = {
    "202603_ShenLong_Unified",
    "202512_LiRuolan_Multiphase",
    "202509_YeXingyu_Dynamic",
    "202503_ZhouXiangyang_Editable",
    "202312_XuYanrui_Implicitly",
}


def update_entry(entry: str, image_dir: Path) -> tuple[str, bool, bool]:
    key_match = KEY_RE.search(entry)
    if not key_match:
        raise ValueError("Could not read BibTeX key")
    key = key_match.group(1).strip()
    pdf_match = PDF_RE.search(entry)
    image_name = "loading.png"
    matched_image = False
    if pdf_match:
        candidate = Path(pdf_match.group(1).strip()).with_suffix(".png").name
        if (image_dir / candidate).is_file():
            image_name = candidate
            matched_image = True

    entry = re.sub(r"(?m)^  preview\s*=\s*\{[^}\r\n]*\},?\r?\n", "", entry)
    entry = re.sub(r"(?m)^  selected\s*=\s*\{[^}\r\n]*\},?\r?\n", "", entry)
    preview_line = f"  preview = {{{image_name}}},"
    visible_match = re.search(r"(?m)^  visible\s*=\s*\{[^}\r\n]*\},?\r?$", entry)
    if visible_match:
        end = visible_match.end()
        entry = entry[:end] + "\r\n" + preview_line + entry[end:]
    else:
        entry = re.sub(
            r"(?m)^(  month\s*=\s*\{[^}\r\n]*\},?)(\r?)$",
            r"\1\r\n  visible = {true},\r\n" + preview_line,
            entry,
            count=1,
        )

    is_selected = key in SELECTED
    if is_selected:
        entry = re.sub(
            r"(?m)^(  preview\s*=\s*\{[^}\r\n]*\},?)(\r?)$",
            r"\1\r\n  selected = {true},",
            entry,
            count=1,
        )
    return entry, matched_image, is_selected


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    bib_path = root / "_bibliography" / "papers.bib"
    image_dir = root / "assets" / "img" / "publication_preview"
    text = bib_path.read_text(encoding="utf-8")
    matches = list(ENTRY_RE.finditer(text))
    if len(matches) != 70:
        raise SystemExit(f"Expected 70 entries, found {len(matches)}")

    chunks: list[str] = []
    cursor = 0
    matched_images = 0
    selected_count = 0
    for match in matches:
        chunks.append(text[cursor : match.start()])
        entry, matched, selected = update_entry(match.group(0), image_dir)
        chunks.append(entry)
        matched_images += matched
        selected_count += selected
        cursor = match.end()
    chunks.append(text[cursor:])

    if selected_count != len(SELECTED):
        raise SystemExit(f"Expected {len(SELECTED)} selected entries, found {selected_count}")
    bib_path.write_text("".join(chunks), encoding="utf-8", newline="\n")
    print(f"Updated 70 entries: matched_images={matched_images} loading_fallbacks={70 - matched_images} selected={selected_count}")


if __name__ == "__main__":
    main()
