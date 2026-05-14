"""
pdf_extractor.py

Responsibilities:
- Accept an UploadFile from the FastAPI route layer
- Validate: content-type, magic bytes, file size, non-empty content
- Extract page text via pdfplumber
- Return raw joined text ready for text_cleaner

Raises HTTPException with structured detail on every failure.
No business logic — caller decides what to do with the text.
"""

import io
import pdfplumber
from fastapi import UploadFile, HTTPException

# Maximum accepted file size (10 MB). Resumes are never legitimately larger.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# PDF magic bytes — every valid PDF starts with %PDF
_PDF_MAGIC = b"%PDF"


def _validate_content_type(file: UploadFile) -> None:
    """
    Reject obviously wrong MIME types.
    'application/octet-stream' is allowed because some browsers/OS combinations
    report generic binary MIME for PDFs.
    """
    allowed = {"application/pdf", "application/octet-stream"}
    ct = (file.content_type or "").split(";")[0].strip().lower()
    if ct and ct not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ct}'. Only PDF files are accepted.",
        )


def _validate_magic_bytes(raw: bytes) -> None:
    """
    Confirm the file actually starts with the PDF magic header (%PDF).
    Guards against renamed non-PDF files that pass MIME type checks.
    """
    if not raw.startswith(_PDF_MAGIC):
        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file does not appear to be a valid PDF. "
                "Please upload a PDF resume."
            ),
        )


def extract_text_from_upload(file: UploadFile) -> str:
    """
    Validate and extract text from a PDF UploadFile.

    Validation order (fail-fast):
    1. MIME type check
    2. Read bytes
    3. Empty file check
    4. File size limit check
    5. PDF magic bytes check
    6. pdfplumber extraction
    7. Non-empty text check

    Returns raw page text joined by double newlines.
    Raises HTTPException(400) on every invalid condition.
    """
    _validate_content_type(file)

    raw_bytes = file.file.read()

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        mb = len(raw_bytes) / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({mb:.1f} MB). Maximum allowed size is 10 MB.",
        )

    _validate_magic_bytes(raw_bytes)

    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="The PDF appears to have no pages.",
                )
            pages: list[str] = []
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    pages.append(text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not parse the PDF. "
                "Ensure it is a valid, non-password-protected PDF. "
                f"({type(exc).__name__})"
            ),
        ) from exc

    if not pages:
        raise HTTPException(
            status_code=400,
            detail=(
                "No extractable text found in the PDF. "
                "It may be a scanned image. "
                "Please upload a text-based PDF."
            ),
        )

    return "\n\n".join(pages)