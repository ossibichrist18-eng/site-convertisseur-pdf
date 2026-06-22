import subprocess

def mp3_to_wav(input_path, output_path):
    """Convertit un fichier MP3 en WAV via FFmpeg."""
    subprocess.run(['ffmpeg', '-y', '-i', input_path, output_path], check=True)

def wav_to_mp3(input_path, output_path):
    """Convertit un fichier WAV en MP3 via FFmpeg."""
    subprocess.run(['ffmpeg', '-y', '-i', input_path, '-acodec', 'libmp3lame', output_path], check=True)