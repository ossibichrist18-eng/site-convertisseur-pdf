import subprocess

def compress_video(input_path, output_path):
    """Compresse une vidéo via FFmpeg."""
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path, 
        '-vcodec', 'libx264', '-crf', '28', 
        output_path
    ], check=True)

def video_to_mp3(input_path, output_path):
    """Extrait la piste audio d'une vidéo en fichier MP3 via FFmpeg."""
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path, 
        '-vn', '-acodec', 'libmp3lame', 
        output_path
    ], check=True)

def video_to_gif(input_path, output_path):
    """Convertit une vidéo en GIF animé via FFmpeg."""
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path, 
        '-vf', 'scale=320:-1:flags=lanczos,fps=10', 
        output_path
    ], check=True)

def trim_video(input_path, output_path, start, end):
    """Découpe une portion d'une vidéo via FFmpeg."""
    subprocess.run([
        'ffmpeg', '-y', '-ss', str(start), 
        '-to', str(end), '-i', input_path, 
        '-c', 'copy', output_path
    ], check=True)