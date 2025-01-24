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

1. Clone the repository
```bash
git clone https://github.com/At1z/Record-Video.git
cd Record-Video/backend-python

2. Create venv and install requirements
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
cd ../front
npm install
3. Prepare .env File with email and groq
how to prepare good email: https://www.youtube.com/watch?v=g_j6ILT-X0k&list=LL&index=7&t=405s
EMAIL_ADDRESS=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-password
How to get key from groq : https://groq.com
Create a accont and generate:
GROQ_API_KEY=your-groq-api-key
4. Preapre pyannote
Follow the instruciton from: https://github.com/pyannote/pyannote-audio/blob/develop/tutorials/community/offline_usage_speaker_diarization.ipynb
5: How to start app:
Open 1 terminal at Record-Video/front
npm run dev
Open 2 terminal: navigate folder with redis and : .\redis-server.exe
Open 3 terminal: venv\Scripts\activate and then celery -A tasks worker --loglevel=info --pool=solo
Open 3 terminal: venv\Scripts\activate and then python main.py

<a href="https://docs.google.com/document/d/1y44XQAZmGFZomasfDyaR7TZ-tADvDPqC/edit?usp=sharing&ouid=100259043549172761957&rtpof=true&sd=true">Project Documentation</a>

