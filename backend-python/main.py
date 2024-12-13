from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
from datetime import datetime
from screens import extract_different_frames
from audio import convert_webm_to_wav

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for directory in ["uploads/video", "uploads/audio"]:
    if not os.path.exists(directory):
        os.makedirs(directory)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/upload")
async def upload_video(video: UploadFile, email: str = Form(...)):
    allowed_types = ["video/mp4", "video/webm", "video/ogg"]
    if video.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_extension = os.path.splitext(video.filename)[1]
    new_filename = f"{email}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = f"uploads/video/{new_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    print(f"Video file received from {email}: {new_filename}")
    
    try:
        frames = extract_different_frames(
            file_path,
            difference_threshold=0.3
        )
        print(f"Extracted {len(frames)} frames from video")
    except Exception as e:
        print(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail="Error processing video frames")
    
    return {
        "message": "Video uploaded and processed successfully",
        "fileName": new_filename,
        "filePath": f"/uploads/video/{new_filename}",
        "email": email,
        "frames_extracted": len(frames)
    }

@app.post("/upload-audio")
async def upload_audio(audio: UploadFile, email: str = Form(...)):
    allowed_types = ["audio/webm", "audio/mp3", "audio/wav", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid audio file type")
    
    file_extension = os.path.splitext(audio.filename)[1]
    new_filename = f"{email}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = f"uploads/audio/{new_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    print(f"Audio file received from {email}: {new_filename}")
    
    # Convert WEBM to WAV if the file is WEBM
    if audio.content_type == "audio/webm":
        try:
            wav_path = convert_webm_to_wav(file_path)
            # Remove original WEBM file
            os.remove(file_path)
            # Update file path and name to use WAV file
            file_path = wav_path
            new_filename = os.path.basename(wav_path)
        except Exception as e:
            print(f"Error converting audio: {e}")
            raise HTTPException(status_code=500, detail="Error converting audio file")
    
    return {
        "message": "Audio uploaded successfully",
        "fileName": new_filename,
        "filePath": f"/uploads/audio/{new_filename}",
        "email": email,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 