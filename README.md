# Record-Video
## Prerequisites

- Node.js (v20+ recommended)
- Vite
- Python 3.10+
- Redis: [Download](https://github.com/tporadowski/redis/releases)
- FFmpeg: [Download](https://github.com/btbn/ffmpeg-builds/releases)
- Tesseract OCR: [Download](https://github.com/UB-Mannheim/tesseract/wiki)
 - Polish language package: [Tessdata](https://github.com/tesseract-ocr/tessdata)
   - Add to: `C:\Program Files\Tesseract-OCR\tessdata`
   - Verify with: `tesseract --list-langs`

## Backend Setup

#1. Clone the repository
```bash
git clone https://github.com/At1z/Record-Video.git
cd Record-Video/backend-python
```
#2. Create virtual environment and install requirements
```bash
cd Record-Video/backend-python
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
#3.Prepare .env File and Groq
[Video with instruction how to gmail with python]( https://www.youtube.com/watch?v=g_j6ILT-X0k&list=LL&index=7&t=405s) :
CopyEMAIL_ADDRESS=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-password
GROQ_API_KEY=your-groq-api-key : [How to get key from groq](https://groq.com)

#4.Prepare Pyannote
Follow: [Pyannote Tutorial how to locally use AI model](https://github.com/pyannote/pyannote-audio/blob/develop/tutorials/community/offline_usage_speaker_diarization.ipynb)

## Front Setup
```bash
cd Record-Video/front
npm install 
```
##Running the Application
#Frontend:
```bash
cd front
npm run dev
```
Redis:
- Navigate the folder with redis and:
```bash
.\redis-server.exe
```
Celery Worker:
```bash
cd Record-Video/backend-python
venv\Scripts\activate
celery -A tasks worker --loglevel=info --pool=solo
```
Backend:
```bash
cd Record-Video/backend-python
venv\Scripts\activate
python main.py
```
<a href="https://docs.google.com/document/d/1y44XQAZmGFZomasfDyaR7TZ-tADvDPqC/edit?usp=sharing&ouid=100259043549172761957&rtpof=true&sd=true">Project Documentation</a>

