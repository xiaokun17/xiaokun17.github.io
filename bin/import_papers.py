#!/usr/bin/env python3
"""Normalize an extracted papers archive into the site's BibTeX and PDF layout."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import unicodedata
from pathlib import Path


DUPLICATE_RECORDS = {14, 19, 20, 35, 42, 48, 49, 63}
FIELD_ORDER = [
    "title",
    "author",
    "journal",
    "year",
    "month",
    "visible",
    "preview",
    "booktitle",
    "volume",
    "number",
    "pages",
    "doi",
    "url",
    "pdf",
    "selected",
    "note",
    "publisher",
    "organization",
    "abstract",
    "keywords",
    "day",
    "language",
    "issn",
]
MINOR_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "like",
    "of",
    "on",
    "or",
    "the",
    "to",
    "toward",
    "towards",
    "using",
    "via",
    "with",
}
ACRONYMS = {
    "3d": "3D",
    "adhd": "ADHD",
    "eeg": "EEG",
    "gps": "GPs",
    "hci": "HCI",
    "ijcai": "IJCAI",
    "llm": "LLM",
    "llms": "LLMs",
    "pde": "PDE",
    "pgsr": "PGSR",
    "sph": "SPH",
    "uk": "UK",
    "unet": "U-Net",
    "vr": "VR",
    "xpbd": "XPBD",
    "xr": "XR",
}
AUTHOR_CORRECTIONS = {
    "Alshakhsi, Sameha": "AlShakhsi, Sameha",
    "Ban, Xiao-Juan": "Ban, Xiaojuan",
    "Ban, XiaoJuan": "Ban, Xiaojuan",
    "Haibo, Yang": "Yang, Haibo",
    "Liu, Si-Nuo": "Liu, Sinuo",
    "Wang, Xiao-Kun": "Wang, Xiaokun",
    "Wang, XiaoKun": "Wang, Xiaokun",
    "Ban, X": "Ban, Xiaojuan",
    "Liu, X": "Liu, Xu",
    "Wang, X": "Wang, Xiaokun",
    "Wang, L": "Wang, Lipeng",
    "Zhang, Y": "Zhang, Yalan",
    "Yalan, Z": "Zhang, Yalan",
    "Yalan, Zhang": "Zhang, Yalan",
    "Ye, Peng-Fei": "Ye, Pengfei",
    "Zhang, Ya-Lan": "Zhang, Yalan",
    "Zhang, YaLan": "Zhang, Yalan",
    "Jian, Chang": "Chang, Jian",
}
TITLE_AUTHOR_OVERRIDES = {
    "multiphaseviscoelasticnonnewtonianfluidsimulation": "Zhang, Yalan and Long, Shen and Xu, Yanrui and Wang, Xiaokun and Yao, Chao and Kosinka, Jiri and Frey, Steffen and Telea, Alexandru and Ban, Xiaojuan",
    "wholookslikemesemanticroutedimageharmonization": "Sun, Jinsheng and Yao, Chao and Wang, Xiaokun and Guo, Yu and Zhang, Yalan and Ban, Xiaojuan",
}


def unwrap(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    if len(value) >= 2 and ((value[0] == "{" and value[-1] == "}") or (value[0] == '"' and value[-1] == '"')):
        return value[1:-1].strip()
    return value


def split_fields(body: str) -> list[str]:
    fields: list[str] = []
    start = 0
    depth = 0
    quoted = False
    escaped = False
    for index, character in enumerate(body):
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == '"' and depth == 0:
            quoted = not quoted
        elif not quoted:
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
            elif character == "," and depth == 0:
                fields.append(body[start:index])
                start = index + 1
    fields.append(body[start:])
    return fields


def parse_entry(text: str) -> dict[str, object]:
    match = re.search(r"@(\w+)\s*\{\s*([^,]+),", text, re.DOTALL)
    if not match:
        raise ValueError("No BibTeX entry found")
    start = match.end()
    depth = 1
    quoted = False
    escaped = False
    end = len(text)
    for index in range(start, len(text)):
        character = text[index]
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == '"' and depth == 1:
            quoted = not quoted
        elif not quoted:
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    end = index
                    break
    values: dict[str, str] = {}
    for field in split_fields(text[start:end]):
        if "=" not in field:
            continue
        name, value = field.split("=", 1)
        values[name.strip().lower()] = unwrap(value)
    return {"type": match.group(1).lower(), "key": match.group(2).strip(), "fields": values}


def parse_entries(text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    position = 0
    while True:
        match = re.search(r"@\w+\s*\{", text[position:])
        if not match:
            break
        start = position + match.start()
        depth = 0
        quoted = False
        escaped = False
        end = len(text)
        for index in range(start, len(text)):
            character = text[index]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character == '"':
                quoted = not quoted
            elif not quoted:
                if character == "{":
                    depth += 1
                elif character == "}":
                    depth -= 1
                    if depth == 0:
                        end = index + 1
                        break
        entries.append(parse_entry(text[start:end]))
        position = end
    return entries


def normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def title_case_segment(segment: str, capitalize: bool) -> str:
    match = re.match(r"^([^A-Za-z0-9]*)(.*?)([^A-Za-z0-9]*)$", segment)
    if not match or not match.group(2):
        return segment
    prefix, word, suffix = match.groups()
    lower = word.lower()
    if lower in ACRONYMS:
        styled = ACRONYMS[lower]
    elif word == "B[a]p" or (sum(character.isupper() for character in word) > 1 and len(word) > 1):
        styled = word
    elif not capitalize and lower in MINOR_WORDS:
        styled = lower
    else:
        styled = word[:1].upper() + word[1:].lower()
    return prefix + styled + suffix


def title_case(value: str) -> str:
    tokens = value.strip().split()
    result: list[str] = []
    after_colon = True
    for index, token in enumerate(tokens):
        parts = token.split("-")
        styled_parts = []
        for part_index, part in enumerate(parts):
            capitalize = after_colon or index == 0 or index == len(tokens) - 1 or part_index > 0
            styled_parts.append(title_case_segment(part, capitalize))
            after_colon = False
        styled = "-".join(styled_parts)
        result.append(styled)
        if token.rstrip("\"')]}.,;!").endswith(":"):
            after_colon = True
    return " ".join(result)


def normalize_name_piece(value: str) -> str:
    pieces = []
    for piece in value.strip().split():
        if len(piece.rstrip(".")) == 1:
            pieces.append(piece.upper())
        elif piece.isupper():
            pieces.append(piece.capitalize())
        else:
            pieces.append(piece)
    return " ".join(pieces)


def normalize_author(value: str) -> str:
    authors = re.split(r"\s+and\s+", value.strip(), flags=re.IGNORECASE)
    normalized = []
    for author in authors:
        author = re.sub(r"\s+", " ", author.strip())
        author = AUTHOR_CORRECTIONS.get(author, author)
        if not author:
            continue
        if author.lower() == "others":
            normalized.append("others")
            continue
        if "," in author:
            last, given = (piece.strip() for piece in author.split(",", 1))
        else:
            parts = author.split()
            if len(parts) == 1:
                last, given = parts[0], ""
            else:
                last, given = parts[-1], " ".join(parts[:-1])
        last = normalize_name_piece(last)
        given = normalize_name_piece(given)
        normalized.append(f"{last}, {given}".rstrip(", "))
    return " and ".join(normalized)


def author_uses_initials(value: str) -> bool:
    """Return True when a record mostly contains initials rather than names."""
    names = re.split(r"\s+and\s+", value.strip(), flags=re.IGNORECASE)
    given_names = []
    for name in names:
        if "," in name:
            _last, given = (piece.strip() for piece in name.split(",", 1))
        else:
            parts = name.split()
            given = " ".join(parts[:-1])
        given_names.extend(piece.strip() for piece in given.split())
    return bool(given_names) and sum(len(piece.rstrip(".")) <= 2 for piece in given_names) >= max(1, len(given_names) // 2)


def normalize_ampersands(value: str) -> str:
    value = value.replace("\\&amp;", "\\&").replace("&amp;", "\\&")
    return re.sub(r"(?<!\\)&", r"\\&", value)


def normalize_pages(value: str) -> str:
    return re.sub(r"([A-Za-z]?\d+)-([A-Za-z]?\d+)", r"\1--\2", value)


def normalize_month(value: str, fallback: str) -> str:
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    value = value.strip().lower()
    if value in months:
        return months[value]
    if value.isdigit():
        return f"{int(value):02d}"
    return fallback


def safe_component(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]", "", value)


def first_author_component(author: str) -> str:
    first = re.split(r"\s+and\s+", author, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    if "," in first:
        last, given = (piece.strip() for piece in first.split(",", 1))
    else:
        parts = first.split()
        last, given = (parts[-1], " ".join(parts[:-1])) if parts else ("Unknown", "")
    return safe_component(last + given) or "UnknownAuthor"


def first_content_component(title: str) -> str:
    for raw_word in title.split():
        word = re.sub(r"[^A-Za-z0-9-]", "", raw_word)
        if word and word.lower() not in MINOR_WORDS:
            return safe_component(word)
    return "Untitled"


def citation_key(author: str, year: str, month: str, title: str, used: set[str]) -> str:
    surname = first_author_component(author)
    base = f"{year}{month}_{surname}_{first_content_component(title)}"
    base = base.replace("__", "_")
    if not year:
        base = f"publication_{surname}_{first_content_component(title)}"
    key = base
    suffix = 2
    while key in used:
        key = f"{base}_{suffix}"
        suffix += 1
    used.add(key)
    return key


def field_value(record: dict[str, str], name: str) -> str:
    return record.get(name, "").strip()


def format_entry(entry_type: str, key: str, fields: dict[str, str]) -> str:
    lines = [f"@{entry_type}{{{key},"]
    present = [name for name in FIELD_ORDER if name in fields]
    for index, name in enumerate(present):
        comma = "," if index < len(present) - 1 else ""
        lines.append(f"  {name} = {{{fields[name]}}}{comma}")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("extracted_root", type=Path)
    parser.add_argument("existing_bib", type=Path)
    parser.add_argument("output_bib", type=Path)
    parser.add_argument("output_pdf_dir", type=Path)
    args = parser.parse_args()

    bib_dir = args.extracted_root / "papers" / "Bib"
    pdf_dir = args.extracted_root / "papers" / "pdf"
    current_entries = parse_entries(args.existing_bib.read_text(encoding="utf-8"))
    current_by_title = {
        normalized_title(str(entry["fields"].get("title", ""))): entry
        for entry in current_entries
        if entry["fields"].get("title")
    }

    with (bib_dir / "manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))

    records = []
    used_keys: set[str] = set()
    copied_pdfs = 0
    args.output_pdf_dir.mkdir(parents=True, exist_ok=True)
    # Numeric-date filenames are generated by this importer. Remove stale
    # versions before rebuilding so renamed records cannot leave orphan PDFs.
    for stale_pdf in args.output_pdf_dir.glob("[0-9][0-9][0-9][0-9][0-9][0-9]_*.pdf"):
        stale_pdf.unlink()

    for row in manifest:
        number = int(row["number"])
        if number in DUPLICATE_RECORDS:
            continue
        source = parse_entry((bib_dir / row["file"]).read_text(encoding="utf-8-sig"))
        source_fields = dict(source["fields"])
        title = title_case(row["title"])
        current = current_by_title.get(normalized_title(row["title"]))
        current_fields = dict(current["fields"]) if current else {}

        source_author = source_fields.get("author", "")
        current_author = current_fields.get("author", "")
        author_source = TITLE_AUTHOR_OVERRIDES.get(normalized_title(row["title"])) or (current_author if current_author and author_uses_initials(source_author) and not author_uses_initials(current_author) else (source_author or current_author))
        author = normalize_author(author_source)
        year = field_value(source_fields, "year") or row["listed_date"][:4]
        month = normalize_month(field_value(source_fields, "month"), row["listed_date"][5:7])
        entry_type = str(source["type"])
        if entry_type == "unknown":
            entry_type = "misc"
        if entry_type in {"misc", "unpublished"} and current and str(current["type"]) not in {"misc", "unpublished"}:
            entry_type = str(current["type"])

        source_venue = field_value(source_fields, "journal") or field_value(source_fields, "booktitle")
        current_venue = field_value(current_fields, "journal") or field_value(current_fields, "booktitle")
        venue = normalize_ampersands(source_venue or current_venue)
        journal = venue if entry_type == "article" else ""

        visible = field_value(current_fields, "visible").lower()
        fields: dict[str, str] = {
            "title": title,
            "author": author,
            "journal": journal,
            "year": year,
            "month": month,
            "visible": "false" if visible == "false" else "true",
        }
        preview = field_value(current_fields, "preview")
        if preview:
            fields["preview"] = preview
        if entry_type in {"inproceedings", "incollection"} and venue:
            fields["booktitle"] = venue

        for name in ("volume", "number", "pages", "doi", "publisher", "organization", "abstract", "keywords", "day", "language", "issn"):
            value = field_value(source_fields, name) or field_value(current_fields, name)
            if value:
                fields[name] = normalize_pages(value) if name == "pages" else normalize_ampersands(value)

        researchgate_id = row.get("researchgate_id", "").strip()
        fields["url"] = field_value(source_fields, "url") or (
            f"https://www.researchgate.net/publication/{researchgate_id}" if researchgate_id else ""
        )
        if not fields["url"]:
            fields.pop("url")

        source_pdf = pdf_dir / f"{number:02d}.pdf"
        if source_pdf.exists():
            pdf_name = f"{year}{month}_{first_author_component(author)}_{first_content_component(title)}.pdf"
            target_pdf = args.output_pdf_dir / pdf_name
            if target_pdf.exists() and target_pdf.read_bytes() != source_pdf.read_bytes():
                raise FileExistsError(f"PDF filename collision: {pdf_name}")
            shutil.copy2(source_pdf, target_pdf)
            fields["pdf"] = pdf_name
            copied_pdfs += 1

        if field_value(current_fields, "selected").lower() == "true":
            fields["selected"] = "true"
        note = field_value(current_fields, "note") or field_value(source_fields, "note")
        if note:
            fields["note"] = normalize_ampersands(note)

        key = citation_key(author, year, month, title, used_keys)
        records.append((int(year), int(month), title, entry_type, key, fields))

    records.sort(key=lambda item: (-item[0], -item[1], item[2].lower()))
    sections: list[str] = []
    current_year = None
    for year, _month, _title, entry_type, key, fields in records:
        if year != current_year:
            if sections:
                sections.append("")
            sections.append(f"% {year}")
            sections.append("")
            current_year = year
        sections.append(format_entry(entry_type, key, fields))
        sections.append("")

    output = "\n".join(sections).rstrip() + "\n"
    args.output_bib.write_text(output, encoding="utf-8", newline="\n")
    print(f"Imported {len(records)} unique BibTeX records and {copied_pdfs} PDFs.")


if __name__ == "__main__":
    main()
