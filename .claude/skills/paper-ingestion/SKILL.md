---
name: paper-ingestion
description: Extract and chunk a paper, book, or unstructured text (video transcript, OCR output) into structured markdown sections with metadata for the Forester knowledge-forest pipeline. Use this skill whenever the user wants to ingest a new document into the forest, add a paper or book to intermediate/, run Step 1 of the pipeline, or says things like "ingest this PDF", "add this paper", "chunk this document", or "process this transcript". Also triggers when the user drops a PDF or text file and wants it turned into sectioned markdown with a meta.json.
---

# Paper Ingestion

## Overview

This skill is Step 1 of the Paper-to-Forester pipeline. It takes a source document (PDF, raw text, transcript, or OCR output) and produces cleanly chunked markdown files plus a metadata JSON file. These outputs feed into Step 2 (Structural Analysis) downstream.

The goal is faithful extraction -- preserve the intellectual content, logical structure, and mathematical notation of the source material while organizing it into manageable, well-named sections.

## Input

One of:
- A PDF file (in the project or provided by the user)
- Raw text pasted into the conversation
- A file in any text format (transcript, OCR dump, etc.)

The user may also provide the document name to use for the output folder. If not, derive it from the title using lowercase-kebab-case (e.g., "Attention Is All You Need" becomes `attention-is-all-you-need`).

### PDF Processing Methods

There are two methods for reading PDFs. Try the built-in Read tool first; fall back to GLM-OCR when needed.

| Method | When to Use |
|--------|-------------|
| **Read tool** (default) | Standard PDFs with selectable text. Works for most academic papers and digital documents. |
| **GLM-OCR** (fallback) | Scanned PDFs, image-heavy documents, complex layouts with tables/formulas, or when the Read tool produces garbled/missing text. |

**How to tell when GLM-OCR is needed:**
- The Read tool returns mostly blank or garbled output
- The PDF is a scan (images of pages rather than embedded text)
- Tables or mathematical formulas are mangled in the Read tool output
- The user explicitly asks for OCR processing

**Using GLM-OCR:**

Run the helper script to convert the PDF to markdown first, then work from that markdown output:

```bash
# Process the whole PDF at once
python .claude/skills/paper-ingestion/glm_ocr.py path/to/document.pdf --output intermediate/<document-name>/ingestion/ocr_raw.md

# For large PDFs or when whole-PDF processing fails, use page-by-page mode (requires PyMuPDF)
python .claude/skills/paper-ingestion/glm_ocr.py path/to/document.pdf --page-by-page --output intermediate/<document-name>/ingestion/ocr_raw.md
```

The script requires the `ZAI_API_KEY` environment variable. It uses the ZhipuAI GLM-OCR model (`zai-sdk` package) and outputs structured markdown. When using `--page-by-page`, each page is rendered at 300 DPI and processed individually with a 1-second delay between API calls.

After obtaining the OCR markdown, proceed with the normal chunking process (Step 3) using the OCR output as your source text instead of the Read tool output.

## Output

All output goes into `intermediate/{document-name}/ingestion/`:

```
intermediate/{document-name}/ingestion/
  meta.json
  01_introduction.md
  02_background.md
  03_methods.md
  ...
  XX_summary.md
```

## Process

### Step 1: Read the Source

Read the source material completely. For PDFs, start with the Read tool (which supports PDF). For large PDFs, read in page ranges. For raw text, work with what's provided.

If the Read tool produces poor results for a PDF (garbled text, missing content, mangled tables/formulas, or the PDF is clearly a scan), fall back to GLM-OCR. Run `python .claude/skills/paper-ingestion/glm_ocr.py <pdf-path> --output intermediate/<document-name>/ingestion/ocr_raw.md` and use that markdown output as your source. See the "PDF Processing Methods" section above for details.

Identify:
- The document's title, authors, year, and venue/publisher
- The abstract or summary (if present)
- The logical section structure

### Step 2: Create `meta.json`

Write `intermediate/{document-name}/ingestion/meta.json` with this structure:

**Before writing meta.json, check that you have a `prefix` value.** The prefix is a 3-digit number (e.g., `006`) that uniquely identifies this document's trees in the forest. The user must provide it -- if they haven't, ask them before proceeding. Do not guess or auto-assign a prefix.

```json
{
  "title": "Full Document Title",
  "authors": ["Author One", "Author Two"],
  "year": 2024,
  "venue": "Conference, Journal, or Publisher Name",
  "abstract": "Full abstract or summary text...",
  "prefix": "006",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "source_file": "original-filename.pdf"
}
```

All fields above are required. Additional fields are allowed when the information is available:
- `"affiliation"` -- institutional affiliation of the authors
- `"doi"` -- DOI identifier (use `null` if unknown)

Do not invent information. If a field (like venue or year) is genuinely unknown, set it to `null`.

### Step 3: Create Chunked Markdown Files

Split the document into sections. Each section becomes one markdown file with a numeric prefix for ordering:

```
01_introduction.md
02_background.md
03_model-architecture.md
04_attention.md
...
11_summary.md
```

**Naming conventions:**
- Prefix with two-digit number: `01_`, `02_`, etc.
- Use lowercase with underscores for the descriptive part
- Match the document's own section names when possible (e.g., if section 4 is titled "Attention", name the file `04_attention.md`)

**Content guidelines for each file:**

1. Start with a markdown heading matching the original section title:
   ```markdown
   # 4. Attention
   ```

2. Use sub-headings (`##`, `###`) to preserve the original hierarchy.

3. Preserve mathematical notation using LaTeX syntax:
   - Inline math: `$...$`
   - Block math: `$$...$$`
   - Keep formulas exactly as they appear in the source -- do not simplify or rewrite them.

4. Preserve tables, lists, and figures descriptions.

5. End each file with a `---` separator followed by a **Key Insight** line when the section has a clear takeaway:
   ```markdown
   ---

   **Key Insight**: The central innovation is...
   ```

6. Each file should be self-contained enough to read on its own, but reference other sections naturally when the source does.

### Step 4: Verify Completeness

After creating all files, do a quick check:
- Every major section of the source is represented
- No content was silently dropped
- Mathematical formulas are intact
- The section ordering reflects the original document flow

Report the file listing to the user when done.

## Chunking Judgment Calls

The hardest part of ingestion is deciding where to split. Here are the principles:

**Respect the author's structure.** If the document has clear sections (numbered chapters, headings), follow them. A section titled "3.1 Scaled Dot-Product Attention" becomes its own file or gets grouped with sibling sections under "3. Model Architecture" -- whichever keeps chunks at a reasonable size.

**Aim for roughly 200-800 words per file.** This is a guideline, not a rule. A short conclusion can be 50 words; a dense methods section can be 1500 words. The point is to avoid both tiny fragments and monolithic walls of text.

**When a section is too large, split by subsections.** If "Chapter 3: Model Architecture" has subsections 3.1 through 3.6, and together they'd be 3000 words, split them into separate files (e.g., `03_model-architecture.md` for the overview, `04_attention.md` for the attention subsection, etc.).

**When sections are too small, merge them.** Two half-paragraph sections can share a file. Use your judgment.

**Always include a summary file as the last chunk.** If the document has a conclusion or discussion section, that becomes the final numbered file. If it doesn't, write a brief `XX_summary.md` that captures the document's main contributions in 3-5 bullet points -- this helps downstream pipeline steps.

## Handling Different Source Types

**Academic papers (PDF):** Usually well-structured with numbered sections. Follow the section numbering. Extract equations carefully. If the Read tool handles the PDF well, use it directly. If not (scanned papers, complex layouts), use GLM-OCR.

**Scanned documents / image PDFs:** Use GLM-OCR with `--page-by-page` mode. The OCR output may need some cleanup -- fix obvious artifacts but flag uncertain passages rather than guessing.

**Books / long documents:** Chapter-level chunking is appropriate. Each chapter becomes one or a few files depending on length. Include a summary chunk at the end. For scanned books, GLM-OCR page-by-page mode is recommended.

**Video transcripts / OCR output:** These are often messy. Your job is to impose structure: identify topic shifts, group related content, add section headings where none exist. Clean up OCR artifacts (broken words, garbled characters) when obvious, but flag uncertainty rather than guessing.

**Chinese or non-English text:** Preserve the original language. Use the original section titles for headings. The meta.json fields should match the source language (Chinese title stays Chinese, etc.).

## Example

For a paper titled "Attention Is All You Need" with sections Introduction, Background, Model Architecture (with subsections), Training, Results, and Conclusion:

```
intermediate/attention-is-all-you-need/ingestion/
  meta.json
  01_introduction.md
  02_background.md
  03_model-architecture.md
  04_attention.md
  05_position-wise-feed-forward.md
  06_embeddings-and-positional-encoding.md
  07_why-self-attention.md
  08_training.md
  09_results.md
  10_conclusion.md
  11_summary.md
```

Notice how "Model Architecture" was split into multiple files (03-07) because its subsections are substantial enough to stand alone. The summary file at the end wraps up the key contributions.

## Pipeline Continuation

This is **Step 1** of the Forester pipeline. After completing ingestion, the ONLY next step is:

**Step 2: Concept Registry** -- Use the `concept-registry` skill to scan the ingestion output and catalog all concepts that need definitions.

Do NOT skip ahead to definition research, relation finding, or index generation. The concept registry must be created first so the user can review the concept list before committing to downstream work.
