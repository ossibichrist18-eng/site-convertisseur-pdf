import os
import zipfile
from PIL import Image

def _finalize_images(out_paths, tmp_dir, zip_name):
    if len(out_paths) == 1:
        return out_paths[0], False
    zip_path = os.path.join(tmp_dir, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for p in out_paths:
            zf.write(p, os.path.basename(p))
    return zip_path, True

def jpg_to_png(paths, tmp_dir):
    out_paths = []
    for p in paths:
        img = Image.open(p)
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + '.png')
        img.save(out_p, 'PNG')
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_png.zip")

def png_to_jpg(paths, tmp_dir):
    out_paths = []
    for p in paths:
        img = Image.open(p).convert('RGB')
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + '.jpg')
        img.save(out_p, 'JPEG')
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_jpg.zip")

def resize_image(paths, tmp_dir, width, height):
    width, height = int(width), int(height)
    out_paths = []
    for p in paths:
        img = Image.open(p)
        img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
        ext = p.rsplit('.', 1)[-1]
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + f'_resized.{ext}')
        img_resized.save(out_p)
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_redimensionnees.zip")

def to_webp(paths, tmp_dir):
    out_paths = []
    for p in paths:
        img = Image.open(p)
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + '.webp')
        img.save(out_p, 'WEBP')
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_webp.zip")

def compress_image(paths, tmp_dir):
    out_paths = []
    for p in paths:
        img = Image.open(p)
        ext = p.rsplit('.', 1)[-1].lower()
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + f'_compressed.{ext}')
        if ext in ['jpg', 'jpeg']:
            img.save(out_p, 'JPEG', quality=40, optimize=True)
        elif ext == 'png':
            img.save(out_p, 'PNG', optimize=True)
        else:
            img.save(out_p)
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_compressees.zip")

def to_black_and_white(paths, tmp_dir):
    out_paths = []
    for p in paths:
        img = Image.open(p).convert('L')
        ext = p.rsplit('.', 1)[-1]
        out_p = os.path.join(tmp_dir, os.path.basename(p).rsplit('.', 1)[0] + f'_nb.{ext}')
        img.save(out_p)
        out_paths.append(out_p)
    return _finalize_images(out_paths, tmp_dir, "images_nb.zip")