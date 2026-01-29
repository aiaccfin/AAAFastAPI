from fastapi import UploadFile
from PyPDF2  import PdfReader

def is_textpdf(file: UploadFile) -> bool:
    try:
        pdf_reader = PdfReader(file.file)
        for page in pdf_reader.pages:
          
            if page.extract_text().strip():  # If any text exists on the page
                print('is textpdf?')
                return True
        return False
    except Exception as e:
        return False  # If reading fails, treat as non-text PDF
