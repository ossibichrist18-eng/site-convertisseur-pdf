import os
import io
import asyncio
import zipfile
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
import edge_tts

# 1. GÉNÉRATEUR DE LIVRE AUDIO (PDF en MP3)
async def synthesize_text(text, output_path):
    communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
    await communicate.save(output_path)

def convert_pdf_to_audio(input_path, output_path):
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        text_page = page.extract_text()
        if text_page:
            text += text_page + "\n"
            
    if not text.strip():
        raise ValueError("Aucun texte lisible n'a pu être extrait de ce PDF.")
    
    text_limite = text[:50000]
    asyncio.run(synthesize_text(text_limite, output_path))


# 2. OCR (PDF Scanné ou Image en Texte TXT)
def ocr_file_to_txt(input_path, output_path):
    text = ""
    if input_path.lower().endswith('.pdf'):
        images = convert_from_path(input_path)
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img, lang='fra+eng')
            text += f"--- Page {i + 1} ---\n{page_text}\n\n"
    else:
        img = Image.open(input_path)
        text = pytesseract.image_to_string(img, lang='fra+eng')
        
    if not text.strip():
        raise ValueError("L'OCR n'a détecté aucun texte lisible sur ce document.")
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)


# 3. ANONYMISEUR (Nettoyer les métadonnées PDF)
def anonymize_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    writer.add_metadata({
        "/Author": "",
        "/Creator": "",
        "/Producer": "",
        "/Subject": "",
        "/Title": "",
        "/CreationDate": "",
        "/ModDate": ""
    })
    
    with open(output_path, 'wb') as f:
        writer.write(f)


# 4. EXTRACTEUR D'IMAGES INTÉGRÉES (PDF en ZIP d'images d'origine)
def extract_pdf_images(input_path, output_zip_path):
    reader = PdfReader(input_path)
    image_count = 0
    
    with zipfile.ZipFile(output_zip_path, 'w') as zf:
        for page_idx, page in enumerate(reader.pages):
            if hasattr(page, 'images') and page.images:
                for img_idx, img in enumerate(page.images):
                    image_count += 1
                    ext = img.name.rsplit('.', 1)[-1] if '.' in img.name else 'png'
                    friendly_name = f"image_page_{page_idx + 1}_{img_idx + 1}.{ext}"
                    zf.writestr(friendly_name, img.data)
                    
    if image_count == 0:
        raise ValueError("Aucune image intégrée n'a été trouvée à l'intérieur de ce PDF.")