# AI Guru Multibot

A multimodal chat agent built with local models:
- **Text Q&A**: Mistral via Ollama
- **Voice Input**: Whisper for speech-to-text
- **Image Analysis**: LLaVA for vision tasks

All runs locally on Windows 11, no cloud dependencies.

## Features
- Text chat with Mistral LLM
- Record voice, transcribe with Whisper, respond via LLM
- Upload images with optional prompt, analyze with LLaVA
- React frontend, FastAPI backend

## Prerequisites
- Python 3.12+
- Node.js 18+
- Ollama installed and running (models: mistral, llava pulled)
- Git for version control

## Setup

### Backend (Python/FastAPI)
1. Navigate to `backend/`:
   ```
   cd backend
   ```
2. Create virtual environment:
   ```
   python -m venv venv
   ```
3. Activate:
   ```
   venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   (Includes fastapi, uvicorn, ollama, openai-whisper)

### Frontend (React)
1. Navigate to `frontend/`:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```

### Ollama Models
Run in terminal (Ollama service must be running):
```
ollama pull mistral
ollama pull llava
```

## Running the App

1. Start Ollama server:
   ```
   ollama serve
   ```
2. Start backend:
   ```
   cd backend
   venv\Scripts\activate.bat
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Start frontend:
   ```
   cd frontend
   npm start
   ```
4. Open http://localhost:3000 in browser.

## Usage
- **Text**: Type message and send.
- **Voice**: Click 🎤 to record, stop to transcribe and respond.
- **Image**: Click 📷 to select file, add prompt (optional), click "Send Image".

## Project Structure
- `backend/`: FastAPI server with endpoints (/chat, /voice-chat, /image-chat)
- `frontend/`: React app with chat UI
- `docs/`: (Optional documentation)

## Troubleshooting
- Ensure Ollama runs on port 11434.
- Voice: Grant microphone permissions.
- Images: Supported formats (JPEG, PNG).
- Low RAM: Models use ~4-5GB each; close other apps.

## Contributing
Fork, create PRs. Issues welcome.

## License
MIT