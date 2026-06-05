#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Text Redactor

A small local utility for redacting configured text phrases from PDFs using PyMuPDF.
Use it only on documents you own or are authorized to edit.

It does not call any AI service or remote API.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

import fitz  # PyMuPDF


def read_keywords(values: Iterable[str], keyword_file: str | None) -> List[str]:
    keywords: List[str] = []

    for value in values:
        value = value.strip()
        if value:
            keywords.append(value)

    if keyword_file:
        path = Path(keyword_file)
        if not path.exists():
            raise FileNotFoundError(f"Keyword file not found: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                keywords.append(line)

    # Preserve order while removing duplicates.
    seen = set()
    unique: List[str] = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique.append(keyword)

    if not unique:
        raise ValueError("No keywords provided. Use --keyword or --keyword-file.")
    return unique


def redact_pdf_by_text(
    input_path: Path,
    output_path: Path,
    keywords: List[str],
    *,
    padding: float = 2.0,
    dry_run: bool = False,
) -> int:
    """Redact every occurrence of each keyword in a text-based PDF."""
    doc = fitz.open(input_path)
    redaction_count = 0

    try:
        for page in doc:
            for keyword in keywords:
                matches = page.search_for(keyword)
                for rect in matches:
                    rect.x0 -= padding
                    rect.y0 -= padding
                    rect.x1 += padding
                    rect.y1 += padding
                    redaction_count += 1
                    if not dry_run:
                        page.add_redact_annot(rect, fill=(1, 1, 1))

            if not dry_run:
                page.apply_redactions()

        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(output_path, garbage=3, deflate=True)
    finally:
        doc.close()

    return redaction_count


def iter_pdf_files(input_path: Path, recursive: bool = False) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {input_path}")
        return [input_path]

    if not input_path.is_dir():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(input_path.glob(pattern))


def build_output_path(input_pdf: Path, input_root: Path, output_dir: Path, suffix: str) -> Path:
    if input_root.is_dir():
        relative = input_pdf.relative_to(input_root)
        return output_dir / relative.with_name(relative.stem + suffix + relative.suffix)
    return output_dir / (input_pdf.stem + suffix + input_pdf.suffix)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Redact configured text phrases from local PDFs. No AI/API calls."
    )
    parser.add_argument("input", help="Input PDF file or directory containing PDFs")
    parser.add_argument("--output-dir", default="cleaned_pdfs", help="Directory for redacted PDFs")
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Text phrase to redact. Can be supplied multiple times.",
    )
    parser.add_argument("--keyword-file", help="UTF-8 text file with one phrase per line")
    parser.add_argument("--suffix", default="_redacted", help="Suffix for output filenames")
    parser.add_argument("--padding", type=float, default=2.0, help="Rectangle padding around matched text")
    parser.add_argument("--recursive", action="store_true", help="Search directories recursively")
    parser.add_argument("--dry-run", action="store_true", help="Count matches without writing output files")
    return parser.parse_args()


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    keywords = read_keywords(args.keyword, args.keyword_file)
    pdf_files = iter_pdf_files(input_path, recursive=args.recursive)

    if not pdf_files:
        print("No PDF files found.")
        return 0

    print(f"Found {len(pdf_files)} PDF file(s).")
    print(f"Keywords: {len(keywords)}")
    if args.dry_run:
        print("Dry run mode: no files will be written.")

    total = 0
    for pdf in pdf_files:
        output_path = build_output_path(pdf, input_path if input_path.is_dir() else pdf, output_dir, args.suffix)
        try:
            count = redact_pdf_by_text(
                pdf,
                output_path,
                keywords,
                padding=args.padding,
                dry_run=args.dry_run,
            )
            total += count
            if args.dry_run:
                print(f"[DRY RUN] {pdf.name}: {count} match(es)")
            else:
                print(f"[OK] {pdf.name}: redacted {count} match(es) -> {output_path}")
        except Exception as exc:
            print(f"[ERROR] {pdf.name}: {exc}")

    print(f"Done. Total redactions: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
