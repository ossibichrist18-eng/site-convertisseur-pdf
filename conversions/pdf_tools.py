import os
import io
import zipfile
import pikepdf
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas

def merge_pdfs(input_paths, output_path):
    writer = PdfWriter()
    for path in input_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)

def split_pdf(input_path, output_dir):
    reader = PdfReader(input_path)
    zip_path = os.path.join(output_dir, 'pages_extraites.zip')
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            page_path = os.path.join(output_dir, f'page_{i + 1}.pdf')
            with open(page_path, 'wb') as f:
                writer.write(f)
            zf.write(page_path, f'page_{i + 1}.pdf')
    return zip_path

def convert_pdf_to_excel(input_path, output_path):
    import camelot
    import pandas as pd
    tables = camelot.read_pdf(input_path, pages='all')
    if len(tables) == 0:
        raise ValueError("Aucun tableau détecté dans ce PDF")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for i, table in enumerate(tables):
            table.df.to_excel(writer, sheet_name=f'Tableau_{i + 1}', index=False)

def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        page.compress_content_streams()
    with open(output_path, 'wb') as f:
        writer.write(f)

def remove_pdf_password(input_path, password, output_path):
    with pikepdf.open(input_path, password=password) as pdf:
        pdf.save(output_path)

def add_page_numbers(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(w, h))
        c.setFont("Helvetica", 11)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawCentredString(w / 2, 20, str(i + 1))
        c.save()
        packet.seek(0)
        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)

def add_watermark(input_path, output_path, text):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(w, h))
        c.setFont("Helvetica", 40)
        c.setFillColorRGB(0.7, 0.7, 0.7, alpha=0.4)
        c.saveState()
        c.translate(w / 2, h / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()
        packet.seek(0)
        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)

def protect_pdf(input_path, output_path, password):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(output_path, 'wb') as f:
        writer.write(f)