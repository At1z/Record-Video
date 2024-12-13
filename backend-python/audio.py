import subprocess
import os

def convert_webm_to_wav(input_file_path):
    """
    Konwertuje plik webm na wav używając FFmpeg
    
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
            '-acodec', 'pcm_s16le', 
            '-ar', '44100',  
            '-ac', '2',  
            output_file_path
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        print(f"Pomyślnie przekonwertowano {input_file_path} na {output_file_path}")
        return output_file_path
        
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas konwersji: {e}")
        raise
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        raise

def convert_audio_to_text(audio_file_path):
    """
    Konwertuje plik audio na tekst używając modelu Whisper
    
    Args:
        audio_file_path (str): Ścieżka do pliku audio (wav)
    
    Returns:
        str: Ścieżka do wygenerowanego pliku tekstowego
    """
    try:
        import whisper
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)
        
        # Tworzenie pliku tekstowego
        text_file_path = audio_file_path.rsplit('.', 1)[0] + '.txt'
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
            
        print(f"Pomyślnie utworzono transkrypcję: {text_file_path}")
        return text_file_path
        
    except Exception as e:
        print(f"Wystąpił błąd podczas transkrypcji: {e}")
        raise
