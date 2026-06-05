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
