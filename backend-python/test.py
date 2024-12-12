from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/upload")
async def upload_video(video: UploadFile, email: str = Form(...)):
    allowed_types = ["video/mp4", "video/webm", "video/ogg"]
    if video.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_extension = os.path.splitext(video.filename)[1]
    new_filename = f"{email}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = f"uploads/{new_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    print(f"File received from {email}: {new_filename}")
    
    return {
        "message": "File uploaded successfully",
        "fileName": new_filename,
        "filePath": f"/uploads/{new_filename}",
        "email": email,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 