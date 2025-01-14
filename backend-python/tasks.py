from celery import Celery, chain # type: ignore
from audio import convert_webm_to_wav
from speechtotext import convert_audio_to_text
from diarization import diarize_audio
from screens import extract_different_frames
from ocr import perform_ocr_on_frames
from doc import save_to_word
from pdf import convert_docx_to_pdf
import os
import requests
import time

app = Celery("tasks", broker="redis://localhost:6379/0")

def check_recording_status(email):
    try:
        response = requests.get(f"http://localhost:3000/recording-status/{email}")
        return response.json().get("recording", False)
    except:
        return True

def wait_for_recording_to_stop(email, max_wait_time=120):
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if not check_recording_status(email):
            return True
        time.sleep(5)
    return False

@app.task
def convert_to_pdf_if_stopped(prev_result, email):
    if wait_for_recording_to_stop(email):
        word_file_path = "uploads/word.docx"
        pdf_file_path = "uploads/word.pdf"
        convert_docx_to_pdf(word_file_path, pdf_file_path)
        print(f"Konwersja do PDF zakończona dla {email}")
        return True
    else:
        print(f"Timeout: Nagrywanie nie zostało zatrzymane dla {email}")
        return False

@app.task
def process_video_task(file_path):
    frames = extract_different_frames(file_path, difference_threshold=0.3)
    perform_ocr_on_frames(frames)
    ocr_results = "uploads/ocr_results.txt"
    word_file_path = "uploads/word.docx"
    save_to_word(word_file_path, frames, ocr_results, [])
    return len(frames)

@app.task
def process_audio_task(file_path):
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

@app.task
def process_video(file_path, email):
    # Create task chain
    task_chain = chain(
        process_video_task.s(file_path),
        convert_to_pdf_if_stopped.s(email)
    )
    return task_chain()

@app.task
def process_audio(file_path, email):
    # Create task chain
    task_chain = chain(
        process_audio_task.s(file_path),
        convert_to_pdf_if_stopped.s(email)
    )
    return task_chain()