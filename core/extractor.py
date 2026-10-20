import io
import re
from pathlib import Path
import pypdf

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_PDF_PATH = BASE_DIR / "data" / "default_resume.pdf"
PROJECT_TXT_PATH = BASE_DIR / "data" / "default_resume.txt"
LOCAL_WINDOWS_PATH = Path(r"D:\V\VenuGopalReddy-PythonFSD-Resume.pdf")

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
    Attempts to read the default resume from:
    1. Local Windows D:\\V\\VenuGopalReddy-PythonFSD-Resume.pdf (Primary master copy)
    2. Bundled data/default_resume.pdf (works in Docker / Render / Cloud)
    3. Bundled data/default_resume.txt (fast clean text fallback)
    """
    # 1. Local Windows master copy (Primary when running natively on host)
    if LOCAL_WINDOWS_PATH.exists():
        try:
            # Auto-sync bundled files if master is newer or bundled missing
            if not PROJECT_PDF_PATH.exists() or LOCAL_WINDOWS_PATH.stat().st_mtime > PROJECT_PDF_PATH.stat().st_mtime:
                import shutil
                shutil.copyfile(str(LOCAL_WINDOWS_PATH), str(PROJECT_PDF_PATH))
                txt = extract_text_from_pdf_file(str(LOCAL_WINDOWS_PATH))
                if txt:
                    with open(PROJECT_TXT_PATH, "w", encoding="utf-8") as f:
                        f.write(txt)
            else:
                txt = extract_text_from_pdf_file(str(LOCAL_WINDOWS_PATH))

            if txt:
                return {
                    "success": True,
                    "text": txt,
                    "path": str(LOCAL_WINDOWS_PATH),
                    "filename": LOCAL_WINDOWS_PATH.name
                }
        except Exception:
            pass

    # 2. Bundled project PDF
    if PROJECT_PDF_PATH.exists():
        try:
            txt = extract_text_from_pdf_file(str(PROJECT_PDF_PATH))
            if txt:
                return {
                    "success": True,
                    "text": txt,
                    "path": "VenuGopalReddy-PythonFSD-Resume.pdf",
                    "filename": "VenuGopalReddy-PythonFSD-Resume.pdf"
                }
        except Exception:
            pass

    # 3. Bundled clean text
    if PROJECT_TXT_PATH.exists():
        try:
            with open(PROJECT_TXT_PATH, "r", encoding="utf-8") as f:
                txt = f.read().strip()
            if txt:
                return {
                    "success": True,
                    "text": txt,
                    "path": "VenuGopalReddy-PythonFSD-Resume.pdf",
                    "filename": "VenuGopalReddy-PythonFSD-Resume.pdf"
                }
        except Exception:
            pass

    return {
        "success": False,
        "text": "",
        "path": "default_resume.pdf",
        "error": "Default resume file not found. Please upload your PDF resume."
    }
