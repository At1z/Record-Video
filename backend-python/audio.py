import subprocess
import os

def convert_webm_to_wav(input_file_path):
    """
    Konwertuje plik webm na wav używając FFmpeg z wysoką jakością
    
    Args:
        input_file_path (str): Ścieżka do pliku webm
    
    Returns:
        str: Ścieżka do wygenerowanego pliku wav
    """
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_file_path}")
    
    output_file_path = input_file_path.rsplit('.', 1)[0] + '.wav'
    
    try:
        command = [
            'ffmpeg',
            '-i', input_file_path, 
            '-vn',  
            '-acodec', 'pcm_s24le',  # Głębia bitowa: 24-bitowa
            '-ar', '48000',          # Częstotliwość próbkowania: 48 kHz
            '-ac', '2',              # Liczba kanałów: Stereo
            output_file_path
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        print(f"Pomyślnie przekonwertowano {input_file_path} na {output_file_path}")
        return output_file_path
        
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas konwersji: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        raise
