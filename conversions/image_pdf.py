import os
from zipfile import ZipFile
from pdf2image import convert_from_path
from PIL import Image

def convert_pdf_to_jpg(pdf_path, output_dir):
    """Extrait toutes les pages d'un PDF sous forme d'images et les packages dans un ZIP"""
    images = convert_from_path(pdf_path)
    zip_path = os.path.join(output_dir, "images.zip")
    
    with ZipFile(zip_path, 'w') as zipf:
        for i, image in enumerate(images):
            img_name = f"page_{i+1}.jpg"
            img_path = os.path.join(output_dir, img_name)
            image.save(img_path, 'JPEG')
            zipf.write(img_path, arcname=img_name)
            
    return zip_path

def convert_image_to_pdf(image_paths, output_pdf_path):
    """Prend une liste d'images et génère un unique PDF compilé"""
    converted_images = []
    
    for path in image_paths:
        img = Image.open(path)
        # Forcer la conversion en RGB (car le format PDF ne supporte pas le mode RGBA alpha des PNG transparents)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.convert("RGBA").split()[3])
            converted_images.append(bg)
        else:
            converted_images.append(img.convert('RGB'))
            
    if converted_images:
        first_img = converted_images[0]
        first_img.save(output_pdf_path, save_all=True, append_images=converted_images[1:])