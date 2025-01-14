from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
from datetime import datetime
from tasks import process_video, process_audio 
from typing import Dict

app = FastAPI()

recording_status: Dict[str, bool] = {}

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

@app.post("/recording-status")
async def update_recording_status(email: str = Form(...), status: bool = Form(...)):
    recording_status[email] = status
    print(f"Recording status for {email}: {'active' if status else 'stopped'}")
    return {"message": "Status updated", "email": email, "recording": status}

@app.get("/recording-status/{email}")
async def get_recording_status(email: str):
    status = recording_status.get(email, False)
    return {"email": email, "recording": status}

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
    
    task = process_video.apply_async(args=[file_path])
    
    return {
        "message": "Video uploaded and processing started",
        "fileName": new_filename,
        "filePath": f"/uploads/video/{new_filename}",
        "email": email,
        "task_id": task.id 
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
    
 
    task = process_audio.apply_async(args=[file_path])
    
    return {
        "message": "Audio uploaded and processing started",
        "fileName": new_filename,
        "filePath": f"/uploads/audio/{new_filename}",
        "email": email,
        "task_id": task.id  
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 