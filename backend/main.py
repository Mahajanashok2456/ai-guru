from fastapi import FastAPI, Body, UploadFile, File
import whisper
import tempfile
import os
import base64
from fastapi.middleware.cors import CORSMiddleware
import ollama

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(data: dict = Body(...)):
    text = data.get("message")
    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': text}])
    return {"response": response['message']['content']}

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    # Create temporary file for audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Load Whisper model (use 'base' for speed, adjust as needed)
        model = whisper.load_model("base")
        result = model.transcribe(temp_path)
        transcribed_text = result["text"].strip()

        if not transcribed_text:
            return {"response": "Sorry, I couldn't understand the audio."}

        # Query Ollama with transcribed text
        ollama_response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': transcribed_text}])
        response_text = ollama_response['message']['content']

        return {"response": response_text}
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/image-chat")
async def image_chat(image: UploadFile = File(...), text: str = Body(..., embed=True)):
    if not text:
        text = "Describe this image."
    
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    response = ollama.chat(
        model='llava',
        messages=[
            {
                'role': 'user',
                'content': text,
                'images': [image_b64]
            }
        ]
    )
    return {"response": response['message']['content']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)