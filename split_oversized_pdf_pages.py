"""
PDF Overlapping Page Detector & Splitter
-----------------------------------------
For each PDF in the input folder:
  - Calculates average page height across all pages
  - Pages whose height exceeds (average * threshold) are flagged as
    "overlapping/double-scans" and saved to output/removed/
  - Remaining normal pages are saved to output/cleaned/

Usage:
    python split_oversized_pdf_pages.py --input ./pdfs --output ./output --threshold 1.5

Requirements:
    pip install pypdf
"""

import argparse
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    raise SystemExit("pypdf not found. Install it with:  pip install pypdf")


def process_pdf(pdf_path: Path, cleaned_dir: Path, removed_dir: Path, threshold: float):
    reader = PdfReader(str(pdf_path))
    pages = reader.pages

    if not pages:
        print(f"  [SKIP] No pages in {pdf_path.name}")
        return

    heights = [float(page.mediabox.height) for page in pages]
    avg_height = sum(heights) / len(heights)
    cutoff = avg_height * threshold

    normal_writer = PdfWriter()
    removed_writer = PdfWriter()
    normal_indices, removed_indices = [], []

    for i, (page, h) in enumerate(zip(pages, heights)):
        if h > cutoff:
            removed_writer.add_page(page)
            removed_indices.append(i + 1)
        else:
            normal_writer.add_page(page)
            normal_indices.append(i + 1)

    print(f"\n[{pdf_path.name}]  avg_height={avg_height:.1f}  cutoff={cutoff:.1f}")
    print(f"  Normal pages  ({len(normal_indices)}): {normal_indices}")
    print(f"  Removed pages ({len(removed_indices)}): {removed_indices}")

    if normal_writer.pages:
        out = cleaned_dir / pdf_path.name
        with open(out, "wb") as f:
            normal_writer.write(f)
        print(f"  Cleaned -> {out}")
    else:
        print(f"  WARNING: All pages removed for {pdf_path.name}")

    if removed_writer.pages:
        out = removed_dir / pdf_path.name
        with open(out, "wb") as f:
            removed_writer.write(f)
        print(f"  Removed -> {out}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect and split oversized/overlapping scanned PDF pages."
    )
    parser.add_argument("--input",     "-i", default="./pdfs",
                        help="Folder with input PDFs (default: ./pdfs)")
    parser.add_argument("--output",    "-o", default="./output",
                        help="Output root folder (default: ./output)")
    parser.add_argument("--threshold", "-t", type=float, default=1.5,
                        help="Pages taller than (avg_height * threshold) are flagged (default: 1.5)")
    args = parser.parse_args()

    input_dir   = Path(args.input)
    cleaned_dir = Path(args.output) / "cleaned"
    removed_dir = Path(args.output) / "removed"

    if not input_dir.exists():
        raise SystemExit(f"Input folder not found: {input_dir}")

    cleaned_dir.mkdir(parents=True, exist_ok=True)
    removed_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'")
        return

    print(f"Found {len(pdf_files)} PDF(s)  |  threshold = {args.threshold}x average height")

    for pdf_path in pdf_files:
        process_pdf(pdf_path, cleaned_dir, removed_dir, args.threshold)

    print(f"\nDone!\n  Cleaned PDFs -> {cleaned_dir}\n  Removed PDFs -> {removed_dir}")


if __name__ == "__main__":
    main()