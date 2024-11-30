import cv2
import numpy as np
import os
import subprocess
import time

def extract_different_frames(video_path, interval_seconds=1.0, difference_threshold=0.5):
    """
    Wyodrębnia klatki z wideo w określonych odstępach czasowych
    """
    # Sprawdź czy plik istnieje
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
            result = subprocess.run(command, 
                                 capture_output=True, 
                                 text=True, 
                                 check=False)
            
            if result.returncode != 0:
                print(f"FFmpeg error output: {result.stderr}")
                # Spróbuj użyć oryginalnego pliku, jeśli konwersja się nie powiedzie
                print("Attempting to process original file...")
                mp4_path = video_path
            else:
                video_path = mp4_path
                print(f"Conversion successful, using: {mp4_path}")
                # Poczekaj chwilę, aby upewnić się, że plik jest gotowy
                time.sleep(0.5)
        except Exception as e:
            print(f"Error converting webm to mp4: {e}")
            # Kontynuuj z oryginalnym plikiem
            mp4_path = video_path

    # Utworzenie folderu na klatki
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    frames_dir = f"uploads/frames_{video_name}"
    os.makedirs(frames_dir, exist_ok=True)

    # Spróbuj otworzyć wideo kilka razy
    max_attempts = 3
    for attempt in range(max_attempts):
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            break
        print(f"Attempt {attempt + 1} to open video failed, retrying...")
        time.sleep(0.5)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file after {max_attempts} attempts: {video_path}")
        return []

    # Pobierz informacje o wideo
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Warning: Invalid FPS, using default value of 30")
        fps = 30
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    print(f"Video FPS: {fps}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {duration:.2f} seconds")

    # Oblicz ile klatek należy przeskoczyć
    frames_to_skip = int(fps * interval_seconds)
    if frames_to_skip <= 0:
        frames_to_skip = 1

    saved_frames = []
    prev_frame = None
    frame_count = 0
    
    while True:
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
            ret, current_frame = cap.read()
            
            if not ret:
                break

            if prev_frame is None:
                frame_path = f"{frames_dir}/frame_{frame_count:04d}.jpg"
                cv2.imwrite(frame_path, current_frame)
                saved_frames.append(frame_path)
                prev_frame = current_frame
                print(f"Saved initial frame at {frame_count/fps:.2f}s")
            else:
                try:
                    diff = cv2.absdiff(prev_frame, current_frame)
                    non_zero_count = np.count_nonzero(diff)
                    total_pixels = diff.shape[0] * diff.shape[1] * diff.shape[2]
                    difference = non_zero_count / total_pixels
                    
                    if difference > difference_threshold:
                        frame_path = f"{frames_dir}/frame_{frame_count:04d}.jpg"
                        cv2.imwrite(frame_path, current_frame)
                        saved_frames.append(frame_path)
                        prev_frame = current_frame.copy()
                        print(f"Saved frame at {frame_count/fps:.2f}s (difference: {difference:.2%})")
                except Exception as e:
                    print(f"Error processing frame difference: {e}")
                    continue

            frame_count += frames_to_skip
            if frame_count >= total_frames:
                break

        except Exception as e:
            print(f"Error processing frame {frame_count}: {e}")
            frame_count += frames_to_skip
            continue
    
    cap.release()
    print(f"Successfully saved {len(saved_frames)} frames")
    return saved_frames 