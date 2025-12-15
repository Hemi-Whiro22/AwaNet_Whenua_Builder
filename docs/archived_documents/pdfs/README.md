# Place your PDF documents here for processing

This folder holds PDF files that will be:
1. OCR'd with StealthOCR (macron-safe)
2. Chunked into semantic segments
3. Embedded as vectors
4. Stored in Supabase with metadata

## Supported Formats
- PDF (text or image-based)
- Scanned documents
- Research papers
- Court records
- Historical documents

## Processing
Upload PDFs via:
- Direct file placement here
- POST /kitenga/ocr endpoint
- POST /mauri/orchestrate with operation=ocr_only

All PDFs automatically get:
- Text extraction
- Macron preservation (ā, ē, ī, ō, ū)
- Cultural tagging
- Vector embeddings
