# tasks.py
##  celery -A tasks worker --loglevel=info --pool=solo <- odpalenie kolejki
## .\redis-server.exe <-odpalenie redis
from celery import Celery # type: ignore
from audio import convert_webm_to_wav
from speechtotext import  convert_audio_to_text
from diarization import diarize_audio
from screens import extract_different_frames
from ocr import perform_ocr_on_frames
from doc import save_to_word
from pdf import convert_docx_to_pdf
import os

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def process_video(file_path):
    try:
        frames = extract_different_frames(file_path, difference_threshold=0.3)
        ocr_results_path = perform_ocr_on_frames(frames)
        word_file_path = "uploads/word.docx"
        save_to_word(word_file_path, frames, ocr_results_path, None)

        return len(frames)
    except Exception as e:
        raise Exception(f"Error processing video: {e}")

@app.task
def process_audio(file_path):

    try:
        if file_path.endswith(".webm"):
            wav_path = convert_webm_to_wav(file_path)
            os.remove(file_path)
            file_path = wav_path

        results = diarize_audio(file_path)

        print(f"{'Speaker':<15}{'Start Time':<15}{'End Time':<15}")
        print("-" * 30)

        for segment in results:
            print(f"{segment['speaker']:<15}{segment['start_time']:<15}{segment['end_time']:<15}")

        text_results = convert_audio_to_text(file_path, results, 0.15) 
        word_file_path = "uploads/word.docx"
        save_to_word(word_file_path, [], [], text_results)

        return "git"
    except Exception as e:
        raise Exception(f"Error processing audio: {e}")
    
@app.task
def convert_to_pdf_if_stopped(email):
    if (email):
        word_file_path = "uploads/word.docx"
        pdf_file_path = "uploads/word.pdf"
        convert_docx_to_pdf(email, word_file_path, pdf_file_path)
        print(f"Konwersja do PDF zakończona dla {email}")
        return True
    else:
        print(f"Timeout: Nagrywanie nie zostało zatrzymane dla {email}")
        return False