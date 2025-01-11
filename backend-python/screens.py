import cv2
import numpy as np
import os
import subprocess
import time
from datetime import datetime
import pytesseract
from PIL import Image

def resize_frame(frame, target_size=(1920, 1080)):
    """Zmienia rozmiar klatki do standardowego rozmiaru"""
    if frame is None:
        return None
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)

def detect_large_face(frame_path, face_threshold=0.3):
    """
    Sprawdza, czy twarz na zdjęciu zajmuje więcej niż określony procent obszaru.
    """
    img = cv2.imread(frame_path)
    if img is None:
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    img_area = img.shape[0] * img.shape[1]

    for (x, y, w, h) in faces:
        face_area = w * h
        if face_area / img_area > face_threshold:
            return True  # Twarz zajmuje więcej niż określony procent zdjęcia

    return False

def extract_different_frames(video_path, difference_threshold=0.5):
    """
    Wyodrębnia pierwszą klatkę z pierwszych 2 sekund wideo i porównuje ją z ostatnią zapisaną
    """
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} does not exist")
        return []

    if os.path.getsize(video_path) == 0:
        print(f"Error: File {video_path} is empty")
        return []

    original_video_path = video_path
    # Konwersja webm do mp4
    if video_path.lower().endswith('.webm'):
        print(f"Converting webm to mp4...")
        mp4_path = video_path.rsplit('.', 1)[0] + '.mp4'
        try:
            command = [
                'ffmpeg',
                '-err_detect', 'ignore_err',
                '-i', video_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-y',
                mp4_path
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                print(f"FFmpeg error output: {result.stderr}")
                mp4_path = video_path
            else:
                video_path = mp4_path
                print(f"Conversion successful, using: {mp4_path}")
                time.sleep(0.5)
                os.remove(original_video_path)
                print(f"Removed original webm file: {original_video_path}")
        except Exception as e:
            print(f"Error converting webm to mp4: {e}")
            mp4_path = video_path

    frames_dir = "uploads/frames"
    os.makedirs(frames_dir, exist_ok=True)

    max_attempts = 3
    cap = None
    for attempt in range(max_attempts):
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            break
        print(f"Attempt {attempt + 1} to open video failed, retrying...")
        time.sleep(0.5)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file after {max_attempts} attempts: {video_path}")
        return []

    saved_frames = []
    
    existing_frames = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
    prev_frame = None
    if existing_frames:
        existing_frames.sort()
        last_frame_path = os.path.join(frames_dir, existing_frames[-1])
        prev_frame = cv2.imread(last_frame_path)
        if prev_frame is not None:
            prev_frame = resize_frame(prev_frame)

    ret, current_frame = cap.read()
    if ret:
        current_frame = resize_frame(current_frame)
        
        if prev_frame is None:
            frame_path = f"{frames_dir}/frame_{int(datetime.now().timestamp())}_0000.jpg"
            cv2.imwrite(frame_path, current_frame)
            saved_frames.append(frame_path)
            print("Saved initial frame")
        else:
            try:
                if prev_frame.shape == current_frame.shape:
                    diff = cv2.absdiff(prev_frame, current_frame)
                    non_zero_count = np.count_nonzero(diff)
                    total_pixels = diff.shape[0] * diff.shape[1] * diff.shape[2]
                    difference = non_zero_count / total_pixels
                    
                    if difference > difference_threshold:
                        frame_path = f"{frames_dir}/frame_{int(datetime.now().timestamp())}_0000.jpg"
                        cv2.imwrite(frame_path, current_frame)
                        saved_frames.append(frame_path)
                        print(f"Saved frame (difference: {difference:.2%})")
                else:
                    print(f"Frame size mismatch: prev={prev_frame.shape}, current={current_frame.shape}")
            except Exception as e:
                print(f"Error processing frame difference: {e}")
    
    cap.release()
    print(f"Successfully saved {len(saved_frames)} frames")

    if video_path != original_video_path and os.path.exists(video_path):
        os.remove(video_path)
        print(f"Removed converted mp4 file: {video_path}")

    return saved_frames

def perform_ocr_on_frames(frame_paths, output_file="uploads/ocr_results.txt", lang="pol"):
    """
    Wykonuje OCR na każdej klatce i aktualizuje plik tekstowy z wynikami.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
              
    extracted_texts = {}

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            extracted_texts = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in f if ":" in line}

    for frame_path in frame_paths:
        frame_name = os.path.basename(frame_path)
        if frame_name in extracted_texts:
            continue  # Pomijaj już przetworzone klatki

        try:
            # Sprawdzenie, czy twarz zajmuje więcej niż 50% zdjęcia
            if detect_large_face(frame_path):
                print(f"Face occupies more than 50% of the frame. Skipping {frame_path}")
                os.remove(frame_path)  # Usuń klatkę z dużą twarzą
                continue

            img = Image.open(frame_path)
            text = pytesseract.image_to_string(img, lang=lang)
            extracted_texts[frame_name] = text.strip()
            print(f"Extracted text from {frame_path}")

            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{frame_name}: {text.strip()}\n")

        except Exception as e:
            print(f"Error extracting text from {frame_path}: {e}")

    return extracted_texts