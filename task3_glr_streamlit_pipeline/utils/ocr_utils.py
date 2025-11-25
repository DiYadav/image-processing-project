from pdf2image import convert_from_path
import pytesseract
import tempfile, os

def ocr_pdf_page_if_needed(pdf_path, page_number=1, dpi=200):
    """
    Convert specified PDF page (1-indexed) to image and perform OCR.
    Returns text string.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            images = convert_from_path(pdf_path, dpi=dpi, first_page=page_number, last_page=page_number, output_folder=tmpdir)
            if not images:
                return ""
            text = pytesseract.image_to_string(images[0])
            return text or ""
    except Exception as e:
        print("OCR error:", e)
        return ""
