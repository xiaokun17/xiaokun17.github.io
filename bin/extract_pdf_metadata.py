#!/usr/bin/env python3
"""Extract abstracts and keywords from publication PDFs into papers.bib."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path

from import_papers import format_entry, parse_entries


LIGATURES = str.maketrans({
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\u00ad": "-",
    "\u00bc": "=",
})
ABSTRACT_WORD = r"(?:abstract|a[ \t]+b[ \t]+s[ \t]+t[ \t]+r[ \t]+a[ \t]+c[ \t]+t|summary)"
ARTICLE_INFO_WORD = r"a[ \t]+r[ \t]+t[ \t]+i[ \t]+c[ \t]+l[ \t]+e[ \t]+i[ \t]+n[ \t]+f[ \t]+o"
KEYWORDS_WORD = (
    r"(?:keywords?|key[ \t]+words|index[ \t]+terms|"
    r"k[ \t]+e[ \t]+y[ \t]+w[ \t]+o[ \t]+r[ \t]+d[ \t]+s)"
)
ABSTRACT_HEADING = re.compile(
    rf"(?im)^[ \t]*(?:{ARTICLE_INFO_WORD}[ \t]+)?({ABSTRACT_WORD})"
    rf"(?:[ \t]*[:.\-\u2013\u2014][ \t]*|[ \t]+|[ \t]*\n[ \t]*)"
)
KEYWORDS_HEADING = re.compile(
    rf"(?im)^[ \t]*(?:additional[ \t]+)?({KEYWORDS_WORD})"
    rf"(?:[ \t]+and[ \t]+phrases)?(?:[ \t]*[:.\-\u2013\u2014][ \t]*|[ \t]+|[ \t]*\n[ \t]*)"
)
INTRO_HEADING = re.compile(
    r"(?im)^[ \t]*(?:(?:[1I]|1\.0)[ \t]*[.|:]?[ \t]*)?(?:\|[ \t]*)?introduction[ \t]*$"
)
ABSTRACT_END_FALLBACK = re.compile(
    r"(?im)^\s*(?:ccs concepts|categories and subject descriptors|received:|copyright\b|"
    r"manuscript received|permission to make digital or hard copies|\u00a9\s*\d{4})"
)
KEYWORD_END_FALLBACK = re.compile(
    r"(?im)(?:^[ \t]*(?:ccs concepts|categories and subject descriptors|received:|copyright\b|"
    r"manuscript received|acm reference format|https?://doi\.org|\d+\s+of\s+\d+|\d+)|"
    r"^.*(?:wileyonlinelibrary\.com|\u00a9[ \t]*\d{4}).*$)"
)
SEPARATOR = re.compile(r"\s*(?:;|\||\u00b7|\u2022|\u25cf|\x01|\x02|\uff1b|\ufffd)\s*")
UNLABELED_ABSTRACT_STARTS = {
    "202512_LiRuolan_Multiphase": "Simulating the interactions between fluids and porous media has attracted",
    "202509_CaiAng_HPIPainting": "Virtual Reality (VR) painting applications allow users",
    "202504_XuYuanmu_Physics": "This paper tackles the challenges of physics-based simulation of rigid bodies",
    "202312_XuYanrui_Implicitly": "Particle-based simulations have become increasingly popular",
    "201703_WangXiaokun_Rigid": "In this paper, we propose an efficient and simple rigid-fluid coupling scheme",
}
CCS_HEADING = re.compile(r"(?im)^[ \t]*ccs concepts\s*:")
INTERRUPTED_ABSTRACT_RESUME = {
    "202512_LiRuolan_Multiphase": "simulation methods model porous media either as static grids",
    "202312_XuYanrui_Implicitly": "method effectively improves dynamic effects while reducing critical",
    "202510_LiuHongjun_Spatial": "cross-center validation scenarios. Notably, IMAC shows strong",
    "202408_ZhangYalan_RealTime": "fluid dynamics simulation field and provides a more accurate and efficient",
}
KEYWORD_OVERRIDES = {
    "202607_LiJingfeng_PGSRDR": "Reflective surface reconstruction; Planar-based Gaussian splatting; Geometric optimization; Deferred rendering",
    "202603_WangRuibin_Capability": "AI-based diagnosis; Referral letters; Data augmentation; Large language models; Clinical decision support",
    "202602_YangSijia_Simulation": "medical visualization; computer-aided diagnosis; fluid dynamics; cardiovascular diseases; blood flow characteristics",
    "202512_AlShakhsiSameha_Developing": "Attitude; Large Language Models; Scale; Generative AI; Human-AI Collaboration",
    "202512_BarajeehBasad_Workaholism": "Large language models; artificial intelligence; dependency; workaholism; working excessively; working compulsively",
    "202410_FangJunheng_Fast": "deformation simulation; dynamic PDE sweeping surface; integration of PDE-based reconstruction and XPBD",
    "202303_WangXiaokun_Implicit": "elastic simulation; fluid-solid coupling; multiple fluid interaction; particle systems; physically based animation",
    "202301_XuYanrui_Spatial": "boundary handling; computer animation; fluid simulation; spatial adaptivity",
    "202212_XuYanrui_Anisotropic": "Real-time rendering; Screen space rendering; Fluid simulation; Smoothed particle hydrodynamics",
    "202212_XuYanrui_Volume": "physical simulation; incompressible fluid; multiphase flows; smoothed particle hydrodynamics",
    "202112_SongChongming_Silicone": "Medical visualization; Rhegmatogenous retinal detachment; Silicone oil tamponade; Multiphase flows simulation",
    "201807_WangXiaokun_SmallScale": "computer animation; fluid simulation; Divergence-free SPH; surface tension",
    "201705_ZhangYalan_PredictiveCorrective": "physically-based animation; fluid simulation; non-Newtonian fluid; SPH; predictive-corrective method",
    "201609_WangXiaokun_Effective": "fluid simulation; smoothed particle hydrodynamics; surface reconstruction; anisotropic",
}


def pdf_text(pdf: Path, pages: int) -> str:
    """Use Poppler raw reading order, which is more reliable for two-column PDFs."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as handle:
        output = Path(handle.name)
    try:
        subprocess.run(
            ["pdftotext", "-f", "1", "-l", str(pages), "-raw", str(pdf), str(output)],
            check=True,
            capture_output=True,
        )
        return output.read_text(encoding="utf-8", errors="replace")
    finally:
        output.unlink(missing_ok=True)


def normalize_source(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.translate(LIGATURES))
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def decode_shifted_font(text: str) -> str:
    """Decode the custom ASCII-offset font used by one legacy IEEE PDF."""
    return "".join(
        chr(ord(character) + 29)
        if character not in " \t\r\n" and 4 <= ord(character) <= 97
        else character
        for character in text
    )


def nearest_end(text: str, start: int, patterns: list[re.Pattern[str]], limit: int) -> int:
    candidates = []
    for pattern in patterns:
        match = pattern.search(text, start)
        if match and match.start() - start <= limit:
            candidates.append(match.start())
    return min(candidates, default=min(len(text), start + limit))


def clean_prose(value: str) -> str:
    value = re.sub(
        r"(?is)(?:authors?[’'] contact information:|permission to make digital or hard copies).*?"
        r"https?\s*:\s*//doi\.org/\S+",
        " ",
        value,
    )
    value = re.sub(r"(?s)收稿日期:.*?http://cje\.ustb\.edu\.cn", " ", value)
    value = re.sub(
        r"(?<=[A-Za-z])-\s*\n\s*\*Corresponding Author\s*\n\s*(?=[a-z])",
        "",
        value,
    )
    value = re.sub(r"\b\d{3,4}\s+计算机辅助设计与图形学学报\s+第\s*\d+\s*卷\s*", " ", value)
    value = value.strip(" \n:.-\u2013\u2014")
    value = re.sub(r"(?<=[A-Za-z])-\s*\n\s*(?=[a-z])", "", value)
    value = re.sub(r"\s*\n\s*", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def extract_abstract(text: str, key: str = "") -> str:
    resume_text = INTERRUPTED_ABSTRACT_RESUME.get(key, "")
    if resume_text:
        resume = text.find(resume_text)
        if resume >= 0:
            markers = [
                position
                for position in (
                    text.rfind("∗Corresponding", 0, resume),
                    text.rfind("∗Both authors", 0, resume),
                    text.rfind("∗", 0, resume),
                    text.rfind("†Corresponding", 0, resume),
                    text.rfind("Corresponding author", 0, resume),
                    text.rfind("Email addresses:", 0, resume),
                    text.rfind("Authors’ Contact Information:", 0, resume),
                    text.rfind("Permission to make digital or hard copies", 0, resume),
                )
                if position >= 0
            ]
            if markers:
                text = text[: min(markers)] + text[resume:]
    start_text = UNLABELED_ABSTRACT_STARTS.get(key, "")
    start = text.find(start_text) if start_text else -1
    if start < 0:
        match = ABSTRACT_HEADING.search(text)
        if not match:
            return ""
        start = match.end()
    end = nearest_end(
        text,
        start,
        [KEYWORDS_HEADING, CCS_HEADING, INTRO_HEADING, ABSTRACT_END_FALLBACK],
        6500,
    )
    value = clean_prose(text[start:end])
    if len(value) < 80 or len(value) > 5500:
        return ""
    return value


def keyword_parts(value: str) -> list[str]:
    raw_value = value.strip()
    value = clean_prose(raw_value)
    value = re.sub(r"\s+(?:and\s+)?(?:1\s*[.|:]?\s*)?introduction\s*$", "", value, flags=re.I)
    if SEPARATOR.search(value):
        parts = SEPARATOR.split(value)
    elif "," not in value and len([line for line in raw_value.splitlines() if line.strip()]) > 1:
        parts = [clean_prose(line) for line in raw_value.splitlines() if line.strip()]
    else:
        parts = re.split(r"\s*,\s*", value)
    cleaned = []
    for part in parts:
        part = part.strip(" ,.;:|\u00b7\u2022")
        part = re.sub(r"\s+", " ", part)
        if 1 < len(part) <= 180 and part.lower() not in {item.lower() for item in cleaned}:
            cleaned.append(part)
    return cleaned[:15] if 2 <= len(cleaned) <= 15 else []


def extract_keywords(text: str, key: str = "") -> str:
    if key in KEYWORD_OVERRIDES:
        return KEYWORD_OVERRIDES[key]
    matches = list(KEYWORDS_HEADING.finditer(text))
    if not matches:
        return ""
    for match in matches:
        start = match.end()
        end = nearest_end(
            text,
            start,
            [ABSTRACT_HEADING, KEYWORDS_HEADING, INTRO_HEADING, KEYWORD_END_FALLBACK],
            1200,
        )
        abstract_start = UNLABELED_ABSTRACT_STARTS.get(key, "")
        if abstract_start:
            abstract_position = text.find(abstract_start, start)
            if 0 <= abstract_position < end:
                end = abstract_position
        parts = keyword_parts(text[start:end])
        if parts:
            return "; ".join(parts)
    return ""


def bib_escape(value: str) -> str:
    value = value.replace("\\&", "&")
    return re.sub(r"(?<!\\)&", r"\\&", value)


def render_bibliography(entries: list[dict[str, object]]) -> str:
    chunks = []
    current_year = None
    for entry in entries:
        fields = dict(entry["fields"])
        year = fields.get("year", "")
        if year != current_year:
            chunks.append(f"% {year}" if year else "% Undated")
            current_year = year
        chunks.append(format_entry(str(entry["type"]), str(entry["key"]), fields))
    return "\n\n".join(chunks) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bib", type=Path)
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("--pages", type=int, default=6)
    parser.add_argument("--write", action="store_true", help="Write extracted fields back to the BibTeX file")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing abstract/keywords fields")
    args = parser.parse_args()

    entries = parse_entries(args.bib.read_text(encoding="utf-8"))
    abstract_count = 0
    keyword_count = 0
    missing_pdfs = []
    incomplete = []

    for entry in entries:
        fields = dict(entry["fields"])
        pdf_name = fields.get("pdf", "")
        if not pdf_name:
            continue
        pdf = args.pdf_dir / pdf_name
        if not pdf.exists():
            missing_pdfs.append(pdf_name)
            continue
        text = pdf_text(pdf, args.pages)
        if str(entry["key"]) == "201903_LiuSinuo_ViscosityBased":
            text = decode_shifted_font(text)
        text = normalize_source(text)
        abstract = extract_abstract(text, str(entry["key"]))
        keywords = extract_keywords(text, str(entry["key"]))
        if abstract:
            abstract_count += 1
            if args.overwrite or not fields.get("abstract"):
                fields["abstract"] = bib_escape(abstract)
        if keywords:
            keyword_count += 1
            if args.overwrite or not fields.get("keywords"):
                fields["keywords"] = bib_escape(keywords)
        if not abstract or not keywords:
            incomplete.append((str(entry["key"]), bool(abstract), bool(keywords)))
        entry["fields"] = fields

    print(f"entries={len(entries)} abstracts={abstract_count} keywords={keyword_count}")
    print(f"missing_pdfs={len(missing_pdfs)} incomplete={len(incomplete)}")
    for key, has_abstract, has_keywords in incomplete:
        print(f"  {key}: abstract={'yes' if has_abstract else 'no'}, keywords={'yes' if has_keywords else 'no'}")
    if args.write:
        args.bib.write_text(render_bibliography(entries), encoding="utf-8")
        print(f"updated {args.bib}")


if __name__ == "__main__":
    main()
