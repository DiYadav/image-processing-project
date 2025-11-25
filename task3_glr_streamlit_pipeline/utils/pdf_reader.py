import pdfplumber
from .ocr_utils import ocr_pdf_page_if_needed
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text from all pages of pdf_path.
    Uses pdfplumber for text first; if page has no text, falls back to OCR for that page.
    Returns combined text string.
    """
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                # fallback to OCR
                ocr_text = ocr_pdf_page_if_needed(pdf_path, page_number=i)
                page_text = ocr_text or ""
            text_parts.append(page_text)
    return "\n\n".join([p for p in text_parts if p])
