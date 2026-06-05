# PDF Text Redactor

A small local Python utility for redacting configured text phrases from PDF files using PyMuPDF.

This project is intended for documents you own or are authorized to edit. It can be useful for removing repeated visible text such as old contact information, internal labels, outdated footers, or other configured phrases.

It does **not** call any AI service or remote API.

## Features

* Redact configured text phrases from PDF files
* Process a single PDF or a folder of PDFs
* Use a keyword list from a text file
* Optional dry-run mode before writing output
* Runs locally with PyMuPDF

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Redact one PDF:

```bash
python pdf_text_redactor.py --input input.pdf --output output.pdf --keyword-file keywords.txt
```

Redact all PDFs in a folder:

```bash
python pdf_text_redactor.py --input ./pdfs --output ./cleaned --keyword-file keywords.txt
```

Preview matches without writing output:

```bash
python pdf_text_redactor.py --input input.pdf --keyword-file keywords.txt --dry-run
```

## Keyword file format

Create a plain text file such as `keywords.txt`:

```text
example phrase 1
example phrase 2
old footer text
```

Each non-empty line is treated as one phrase to search and redact.

## Notes

This tool works best when the target phrase exists as searchable PDF text.

It may not work well for:

* scanned PDFs
* image-based watermarks
* text flattened into page images
* complex transparent graphical watermarks

## Safety

Do not upload private PDFs, API keys, credentials, or generated confidential files to this repository.

Only use this tool on documents you own or are authorized to modify.

## License

MIT License
