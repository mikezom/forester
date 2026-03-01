#!/usr/bin/env python3
"""
GLM-OCR PDF Processor
=====================
Converts a PDF file to structured markdown using the GLM-OCR layout parsing API.

Usage:
    python glm_ocr.py <pdf-path> [--output <output-path>] [--page-by-page]

Environment:
    ZAI_API_KEY: Required. API key for the ZhipuAI platform.

Output:
    Writes markdown to stdout (default) or to the specified output file.
    When --page-by-page is used, processes each page separately and concatenates
    the results with page markers.
"""

import argparse
import base64
import os
import sys
import time


def get_client():
    """Initialize the ZAI client with API key from environment."""
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("Error: ZAI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key from https://open.bigmodel.cn/", file=sys.stderr)
        sys.exit(1)

    from zai import ZaiClient

    return ZaiClient(api_key=api_key)


def process_pdf(client, pdf_path):
    """Process a PDF file as a whole and return markdown."""
    with open(pdf_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode()

    data_uri = f"data:application/pdf;base64,{b64_data}"
    response = client.layout_parsing.create(model="glm-ocr", file=data_uri)
    return response.md_results


def process_pdf_page_by_page(client, pdf_path, delay=1.0):
    """Process a PDF page by page and return concatenated markdown.

    Requires PyMuPDF (fitz) for page extraction.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(
            "Error: PyMuPDF is required for page-by-page processing.",
            file=sys.stderr,
        )
        print("Install it with: pip install PyMuPDF", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    results = []

    for i, page in enumerate(doc):
        page_num = i + 1
        print(
            f"Processing page {page_num}/{total_pages}...",
            file=sys.stderr,
        )

        # Render page to PNG at 300 DPI for good OCR quality
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        b64_data = base64.b64encode(img_bytes).decode()
        data_uri = f"data:image/png;base64,{b64_data}"

        try:
            response = client.layout_parsing.create(model="glm-ocr", file=data_uri)
            md = response.md_results
            if md:
                results.append(f"<!-- Page {page_num} -->\n{md}")
            else:
                results.append(f"<!-- Page {page_num}: no content detected -->")
        except Exception as e:
            print(
                f"Warning: Failed to process page {page_num}: {e}",
                file=sys.stderr,
            )
            results.append(f"<!-- Page {page_num}: processing failed -->")

        # Rate limiting between pages
        if page_num < total_pages:
            time.sleep(delay)

    doc.close()
    return "\n\n".join(results)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to markdown using GLM-OCR"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--page-by-page",
        action="store_true",
        help="Process each page separately (requires PyMuPDF). "
        "Use this for large PDFs or when whole-PDF processing fails.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between page API calls (default: 1.0)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    client = get_client()

    if args.page_by_page:
        markdown = process_pdf_page_by_page(client, args.pdf_path, delay=args.delay)
    else:
        print("Processing PDF...", file=sys.stderr)
        markdown = process_pdf(client, args.pdf_path)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
