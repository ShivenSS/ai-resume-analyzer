from pypdf import PdfReader
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise ValueError(
            "Could not extract text from this PDF. It may be a scanned "
            "image rather than a text-based PDF."
        )

    return full_text


if __name__ == "__main__":
    with open("test_resume.pdf", "rb") as f:
        pdf_bytes = f.read()

    extracted = extract_text_from_pdf(pdf_bytes)
    print(extracted)