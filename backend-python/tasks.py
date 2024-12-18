# tasks.py
##  celery -A tasks worker --loglevel=info --pool=solo <- odpalenie kolejki
## .\redis-server.exe <-odpalenie redis
from celery import Celery
from audio import convert_webm_to_wav
from speechtotext import  convert_audio_to_text
from diarization import diarize_audio
from screens import extract_different_frames
import os

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def process_video(file_path):

    try:
        frames = extract_different_frames(file_path, difference_threshold=0.3)
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
        print("-" * 45)
        
        for segment in results:
            print(f"{segment['speaker']:<15}{segment['start_time']:<15}{segment['end_time']:<15}")
        
        convert_audio_to_text(file_path, results)
        return "git"
    except Exception as e:
        raise Exception(f"Error processing audio: {e}")
