# PDF Text Redactor

A small local Python utility for redacting configured text phrases from PDF files using PyMuPDF.

It is designed for documents you own or are authorized to edit, such as drafts, internal handouts, exported notes, old contact sheets, or files that need text cleanup.

This tool runs locally and does **not** call any AI model or remote API.

## What it does

- Searches text-based PDFs for configured phrases.
- Applies white redaction boxes over matching text regions.
- Processes one PDF or a directory of PDFs.
- Supports dry-run mode to count matches before writing files.
- Runs locally with PyMuPDF.

## What it does not do

- It does not bypass DRM, passwords, or access controls.
- It does not reliably remove watermarks embedded as images.
- It should not be used to remove ownership marks from documents you are not allowed to modify.

## Installation

```bash
pip install -r requirements.txt
Usage

Create a keyword file:

old contact text
example footer
example repeated phrase

Preview matches without writing output:

python pdf_text_redactor.py --input input.pdf --keyword-file keywords.txt --dry-run

Redact one PDF:

python pdf_text_redactor.py --input input.pdf --output output.pdf --keyword-file keywords.txt

Redact all PDFs in a folder:

python pdf_text_redactor.py --input ./pdfs --output ./cleaned_pdfs --keyword-file keywords.txt
Keyword file format

Use one phrase per line.

Blank lines are ignored. Lines beginning with # are treated as comments.

Example:

# Old footer text
example phrase 1
example phrase 2
old contact information
Notes

This tool works best when the target phrase exists as searchable PDF text.

It may not work well for:

scanned PDFs
image-based watermarks
transparent graphical watermarks
text flattened into page images
Safety

Do not upload private PDFs, API keys, credentials, or generated confidential files to this repository.

Only use this tool on documents you own or are authorized to modify.
