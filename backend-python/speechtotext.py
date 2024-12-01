import speech_recognition as sr
from pydub import AudioSegment
import os

def convert_audio_to_wav(audio_path):
    """Konwertuje różne formaty audio do WAV."""
    try:
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        if file_ext == '.wav':
            return audio_path
            
        wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
        
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format='wav')
        
        return wav_path
    except Exception as e:
        raise Exception(f"Błąd konwersji audio: {str(e)}")

def convert_video_to_text(audio_path, language='pl-PL'):
    """
    Konwertuje audio na tekst z zaawansowanymi opcjami.
    
    Parameters:
    - audio_path: ścieżka do pliku audio
    - language: język rozpoznawania (domyślnie polski)
    
    Returns:
    - tekst lub informacja o błędzie
    """
    try:
        wav_path = convert_audio_to_wav(audio_path)
        
        recognizer = sr.Recognizer()
        
        # Dostosowanie parametrów rozpoznawania
        recognizer.energy_threshold = 300  # Próg energii dla wykrywania mowy
        recognizer.dynamic_energy_threshold = True  # Dynamiczne dostosowanie progu
        recognizer.pause_threshold = 0.3  # Zmniejszony czas pauzy dla lepszego wychwytywania końcówek
        recognizer.phrase_threshold = 0.1  # Próg wykrywania fraz
        recognizer.non_speaking_duration = 0.1  # Krótszy czas ciszy między słowami
        
        with sr.AudioFile(wav_path) as source:
            
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(
                audio,
                language=language,
                show_all=False,  
            )
            return {
                'status': 'success',
                'text': text,
                'language': language
            }
            
        except sr.UnknownValueError:
            try:
                alternate_language = 'en-US' if language == 'pl-PL' else 'pl-PL'
                text = recognizer.recognize_google(
                    audio,
                    language=alternate_language,
                )
                return {
                    'status': 'success',
                    'text': text,
                    'language': alternate_language
                }
            except:
                return {
                    'status': 'error',
                    'message': 'Nie udało się rozpoznać mowy w żadnym języku'
                }
                
        except sr.RequestError as e:
            return {
                'status': 'error',
                'message': f'Błąd API: {str(e)}'
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Błąd podczas przetwarzania: {str(e)}'
        }
    finally:
        if 'wav_path' in locals() and wav_path != audio_path:
            try:
                os.remove(wav_path)
            except:
                pass

if __name__ == "__main__":
    # Przykład użycia
    audio_path = "uploads/@gmail.com_1733064722.wav"
    result = convert_video_to_text(audio_path)
    
    if result['status'] == 'success':
        print(f"Transkrypcja ({result['language']}):", result['text'])
    else:
        print("Błąd:", result['message'])