from io import BytesIO


def extract_text(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix == "pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
    if suffix in {"ppt", "pptx"}:
        from pptx import Presentation

        slides = Presentation(BytesIO(content)).slides
        return "\n".join(shape.text for slide in slides for shape in slide.shapes if hasattr(shape, "text"))
    if suffix in {"doc", "docx"}:
        from docx import Document

        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    if suffix in {"txt", "md"}:
        return content.decode("utf-8", errors="replace")
    # OCR is deliberately optional; image bytes are stored and queued for a worker.
    if suffix in {"png", "jpg", "jpeg", "webp"}:
        try:
            from PIL import Image
            import pytesseract

            return pytesseract.image_to_string(Image.open(BytesIO(content)))
        except (ImportError, OSError):
            return ""
    return ""


def split_chunks(text: str, size: int = 1100, overlap: int = 160) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        chunks.append(normalized[start:end])
        start = max(start + 1, end - overlap)
    return chunks
