#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Text Redactor

A local utility for redacting configured text phrases from PDF files using PyMuPDF.

Use only on documents you own or are authorized to edit.
This script does not call any AI service or remote API.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF


def read_keywords(keyword_file: Path) -> list[str]:
    """Read one keyword/phrase per line from a UTF-8 text file."""
    if not keyword_file.exists():
        raise FileNotFoundError(f"Keyword file not found: {keyword_file}")

    keywords: list[str] = []
    for line in keyword_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        item = line.strip()
        if item and not item.startswith("#"):
            keywords.append(item)

    if not keywords:
        raise ValueError(f"No keywords found in: {keyword_file}")

    return keywords


def iter_pdf_files(input_path: Path) -> Iterable[Path]:
    """Yield PDF files from a single PDF path or a directory."""
    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {input_path}")
        yield input_path
        return

    if input_path.is_dir():
        yield from sorted(input_path.glob("*.pdf"))
        return

    raise FileNotFoundError(f"Input path not found: {input_path}")


def output_path_for(input_pdf: Path, input_root: Path, output_root: Path) -> Path:
    """Build output path while keeping simple folder behavior."""
    if input_root.is_file():
        if output_root.suffix.lower() == ".pdf":
            return output_root
        return output_root / input_pdf.name

    return output_root / input_pdf.name


def redact_pdf(
    input_pdf: Path,
    output_pdf: Path,
    keywords: list[str],
    *,
    padding: float = 2.0,
    dry_run: bool = False,
) -> int:
    """
    Redact all configured phrases in one PDF.

    Returns the number of matched text regions.
    """
    doc = fitz.open(input_pdf)
    match_count = 0

    try:
        for page in doc:
            for keyword in keywords:
                matches = page.search_for(keyword)
                for rect in matches:
                    expanded = fitz.Rect(
                        rect.x0 - padding,
                        rect.y0 - padding,
                        rect.x1 + padding,
                        rect.y1 + padding,
                    )
                    match_count += 1

                    if not dry_run:
                        page.add_redact_annot(expanded, fill=(1, 1, 1))

            if not dry_run:
                page.apply_redactions()

        if not dry_run:
            output_pdf.parent.mkdir(parents=True, exist_ok=True)
            doc.save(output_pdf, garbage=3, deflate=True)
    finally:
        doc.close()

    return match_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Redact configured text phrases from PDF files using PyMuPDF."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Input PDF file or directory containing PDF files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=Path,
        default=Path("cleaned_pdfs"),
        help="Output PDF file or output directory. Default: cleaned_pdfs",
    )
    parser.add_argument(
        "--keyword-file",
        "-k",
        required=True,
        type=Path,
        help="Text file containing one phrase per line.",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=2.0,
        help="Extra padding around matched text boxes. Default: 2.0",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only count matches. Do not write output PDFs.",
    )
    return parser


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = build_parser()
    args = parser.parse_args()

    input_path: Path = args.input
    output_root: Path = args.output
    keyword_file: Path = args.keyword_file

    keywords = read_keywords(keyword_file)
    pdf_files = list(iter_pdf_files(input_path))

    if not pdf_files:
        print(f"No PDF files found in: {input_path}")
        return 1

    print(f"Loaded {len(keywords)} keyword(s).")
    print(f"Found {len(pdf_files)} PDF file(s).")

    total_matches = 0

    for pdf in pdf_files:
        try:
            out_pdf = output_path_for(pdf, input_path, output_root)
            count = redact_pdf(
                pdf,
                out_pdf,
                keywords,
                padding=args.padding,
                dry_run=args.dry_run,
            )
            total_matches += count

            if args.dry_run:
                print(f"[DRY RUN] {pdf.name}: {count} match(es)")
            else:
                print(f"[OK] {pdf.name}: redacted {count} match(es) -> {out_pdf}")

        except Exception as exc:
            print(f"[ERROR] {pdf.name}: {exc}")

    print(f"Done. Total matches: {total_matches}")

    if args.dry_run:
        print("Dry run only. No files were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
