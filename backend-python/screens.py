import cv2
import numpy as np
import os
import subprocess
import time
from datetime import datetime

def resize_frame(frame, target_size=(1280, 720)):
    """Zmienia rozmiar klatki do standardowego rozmiaru"""
    if frame is None:
        return None
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)

def extract_different_frames(video_path, interval_seconds=1.0, difference_threshold=0.5):
    """
    Wyodrębnia klatki z wideo w określonych odstępach czasowych
    """
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} does not exist")
        return []

    if os.path.getsize(video_path) == 0:
        print(f"Error: File {video_path} is empty")
        return []

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
        except Exception as e:
            print(f"Error converting webm to mp4: {e}")
            mp4_path = video_path

    # Utworzenie wspólnego folderu na klatki
    frames_dir = "uploads/frames"
    os.makedirs(frames_dir, exist_ok=True)

    # Otwórz wideo
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

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Warning: Invalid FPS, using default value of 30")
        fps = 30
    
    frames_to_skip = int(fps * interval_seconds)
    if frames_to_skip <= 0:
        frames_to_skip = 1

    saved_frames = []
    prev_frame = None
    frame_count = 0
    
    # Znajdź ostatnio zapisaną klatkę
    existing_frames = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
    if existing_frames:
        existing_frames.sort()
        last_frame_path = os.path.join(frames_dir, existing_frames[-1])
        prev_frame = cv2.imread(last_frame_path)
        if prev_frame is not None:
            prev_frame = resize_frame(prev_frame)
    
    while True:
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
            ret, current_frame = cap.read()
            
            if not ret:
                break

            # Zmień rozmiar bieżącej klatki
            current_frame = resize_frame(current_frame)
            if current_frame is None:
                continue

            if prev_frame is None:
                frame_path = f"{frames_dir}/frame_{int(datetime.now().timestamp())}_{frame_count:04d}.jpg"
                cv2.imwrite(frame_path, current_frame)
                saved_frames.append(frame_path)
                prev_frame = current_frame
                print(f"Saved initial frame at {frame_count/fps:.2f}s")
            else:
                try:
                    # Upewnij się, że obie klatki mają ten sam rozmiar
                    if prev_frame.shape == current_frame.shape:
                        diff = cv2.absdiff(prev_frame, current_frame)
                        non_zero_count = np.count_nonzero(diff)
                        total_pixels = diff.shape[0] * diff.shape[1] * diff.shape[2]
                        difference = non_zero_count / total_pixels
                        
                        if difference > difference_threshold:
                            frame_path = f"{frames_dir}/frame_{int(datetime.now().timestamp())}_{frame_count:04d}.jpg"
                            cv2.imwrite(frame_path, current_frame)
                            saved_frames.append(frame_path)
                            prev_frame = current_frame.copy()
                            print(f"Saved frame at {frame_count/fps:.2f}s (difference: {difference:.2%})")
                    else:
                        print(f"Frame size mismatch: prev={prev_frame.shape}, current={current_frame.shape}")
                except Exception as e:
                    print(f"Error processing frame difference: {e}")
                    continue

            frame_count += frames_to_skip

        except Exception as e:
            print(f"Error processing frame {frame_count}: {e}")
            frame_count += frames_to_skip
            continue
    
    cap.release()
    print(f"Successfully saved {len(saved_frames)} frames")
    return saved_frames 