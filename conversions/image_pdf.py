import os
import zipfile
from pdf2image import convert_from_path
from PIL import Image

def convert_pdf_to_jpg(input_path, output_dir):
    """Extrait les pages d'un PDF sous forme d'images JPG et les zippe."""
    images = convert_from_path(input_path)
    zip_path = os.path.join(output_dir, "pages_images.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for i, img in enumerate(images):
            img_path = os.path.join(output_dir, f"page_{i+1}.jpg")
            img.save(img_path, "JPEG")
            zf.write(img_path, f"page_{i+1}.jpg")
    return zip_path

def convert_image_to_pdf(paths, out_path):
    """Convertit une liste d'images (PNG, JPG) en un seul fichier PDF."""
    images = []
    for p in paths:
        img = Image.open(p).convert('RGB')
        images.append(img)
    if images:
        images[0].save(out_path, save_all=True, append_images=images[1:])