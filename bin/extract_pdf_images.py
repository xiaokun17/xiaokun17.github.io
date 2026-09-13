#!/usr/bin/env python3
"""Extract embedded raster images from the site's publication PDFs.

Each image is written as ``<pdf-stem>_<number:02d>.png``.  The script uses
Poppler's pdfimages utility so images are extracted from the PDF without
rendering whole pages or changing their native pixel dimensions.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def numeric_sort(path: Path) -> tuple[int, str]:
    match = re.search(r"-(\d+)$", path.stem)
    return (int(match.group(1)) if match else 0, path.name)


def extract_one(pdf: Path, output_dir: Path, pdfimages: str) -> int:
    with tempfile.TemporaryDirectory(prefix="pdf-images-") as temp_dir:
        prefix = Path(temp_dir) / "image"
        result = subprocess.run(
            [pdfimages, "-png", str(pdf), str(prefix)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"pdfimages failed for {pdf.name}: {details}")

        extracted = sorted(Path(temp_dir).glob("image-*.png"), key=numeric_sort)
        for index, source in enumerate(extracted, start=1):
            target = output_dir / f"{pdf.stem}_{index:02d}.png"
            shutil.copy2(source, target)
        return len(extracted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--pdfimages",
        default=shutil.which("pdfimages") or "pdfimages",
        help="Path to Poppler's pdfimages executable",
    )
    args = parser.parse_args()

    if not args.pdf_dir.is_dir():
        raise SystemExit(f"PDF directory does not exist: {args.pdf_dir}")
    if shutil.which(args.pdfimages) is None and not Path(args.pdfimages).exists():
        raise SystemExit(f"pdfimages executable not found: {args.pdfimages}")

    pdfs = sorted(args.pdf_dir.glob("*.pdf"), key=lambda path: path.name.lower())
    if not pdfs:
        raise SystemExit(f"No PDF files found in {args.pdf_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    no_images: list[str] = []
    for pdf in pdfs:
        count = extract_one(pdf, args.output_dir, args.pdfimages)
        total += count
        if count == 0:
            no_images.append(pdf.name)
        print(f"{pdf.name}: {count} image(s)")

    print(f"Extracted {total} image(s) from {len(pdfs)} PDF(s) into {args.output_dir}")
    if no_images:
        print("PDFs with no embedded raster images:")
        for name in no_images:
            print(f"  {name}")


if __name__ == "__main__":
    main()
