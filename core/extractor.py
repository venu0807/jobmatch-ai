import io
import re
from pathlib import Path
import pypdf

DEFAULT_RESUME_PATH = r"D:\V\VenuGopalReddy-PythonFSD-Resume.pdf"

def clean_extracted_text(text: str) -> str:
    """
    Cleans OCR artifacts, hyphenated line-breaks, and multiple spaces.
    """
    if not text:
        return ""
    # Fix hyphenated words broken across lines (e.g., 'serv-\ning' -> 'serving')
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # Fix ligatures (fi, fl)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    # Replace multiple newlines and tabs
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def extract_text_from_pdf_file(file_path: str) -> str:
    """
    Extracts text from a local PDF path.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    reader = pypdf.PdfReader(str(path))
    pages_text = []
    for page in reader.pages:
        t = page.extract_text() or ""
        pages_text.append(t)
    raw = "\n".join(pages_text)
    return clean_extracted_text(raw)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from uploaded PDF bytes.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []
    for page in reader.pages:
        t = page.extract_text() or ""
        pages_text.append(t)
    raw = "\n".join(pages_text)
    return clean_extracted_text(raw)

def get_default_resume_text() -> dict:
    """
    Attempts to read the default resume from D:\\V\\...
    Returns {'success': bool, 'text': str, 'path': str, 'error': str}
    """
    try:
        txt = extract_text_from_pdf_file(DEFAULT_RESUME_PATH)
        return {
            "success": True,
            "text": txt,
            "path": DEFAULT_RESUME_PATH,
            "filename": Path(DEFAULT_RESUME_PATH).name
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "path": DEFAULT_RESUME_PATH,
            "error": str(e)
        }
