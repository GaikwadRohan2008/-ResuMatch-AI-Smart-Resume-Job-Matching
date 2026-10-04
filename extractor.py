import os
import re
from typing import Dict, Any

def extract_text_from_pdf(file_bytes) -> str:
    """Extracts text from a PDF file using pypdf, with robust fallback."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_bytes)
        text = ""
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"

def extract_text_from_docx(file_bytes) -> str:
    """Extracts text from a DOCX file using python-docx."""
    try:
        import docx
        import io
        doc = docx.Document(io.BytesIO(file_bytes.read() if hasattr(file_bytes, 'read') else file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        full_text.append(cell.text)
        return "\n".join(full_text).strip()
    except Exception as e:
        return f"[Error extracting DOCX: {str(e)}]"

def extract_text(file_obj, filename: str) -> str:
    """Universal text extractor supporting PDF, DOCX, and TXT files."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_obj)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_obj)
    elif ext in [".txt", ".md"]:
        if hasattr(file_obj, "read"):
            content = file_obj.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="ignore")
            return str(content)
        return str(file_obj)
    else:
        # Fallback for raw text-like streams
        try:
            if hasattr(file_obj, "read"):
                return file_obj.read().decode("utf-8", errors="ignore")
            return str(file_obj)
        except Exception:
            return ""
