import os
from pdf2docx import Converter

def convert_pdf_to_word(pdf_path, docx_path):
    """Convertit un fichier PDF en document Word (.docx) modifiable."""
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()