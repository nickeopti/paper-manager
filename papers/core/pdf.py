import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = [page.extract_text() for page in pdf_reader.pages]
    return '\n'.join(text).replace('\n', ' ')
