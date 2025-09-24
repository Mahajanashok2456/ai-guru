from fastapi import FastAPI, Body, UploadFile, File
import mysql.connector
import whisper
import tempfile
import os
import base64
from fastapi.middleware.cors import CORSMiddleware
import ollama


# MySQL connection config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2456',
    'database': 'guru_multibot',
    'port': 3306
}

def store_interaction(input_type, user_input, bot_response):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "INSERT INTO chat_history (input_type, user_input, bot_response) VALUES (%s, %s, %s)"
    cursor.execute(query, (input_type, user_input, bot_response))
    conn.commit()
    cursor.close()
    conn.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(data: dict = Body(...)):
    text = data.get("message")
    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': text}])
    bot_response = response['message']['content']
    store_interaction('text', text, bot_response)
    return {"response": bot_response}

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
        store_interaction('voice', transcribed_text, response_text)
        return {"response": response_text}
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    # Create temporary file for audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Load Whisper model (use 'base' for speed)
        model = whisper.load_model("base")
        result = model.transcribe(temp_path)
        transcribed_text = result["text"].strip()
        
        return {"transcription": transcribed_text}
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
    bot_response = response['message']['content']
    store_interaction('image', text, bot_response)
    return {"response": bot_response}

# Endpoint to fetch all chat history
@app.get("/chat-history")
def get_chat_history():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC")
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"history": history}

# Endpoint to delete a specific chat history entry
@app.delete("/chat-history/{chat_id}")
def delete_chat_history(chat_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if the record exists
        cursor.execute("SELECT id FROM chat_history WHERE id = %s", (chat_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Chat history not found"}
        
        # Delete the record
        cursor.execute("DELETE FROM chat_history WHERE id = %s", (chat_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Chat history deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting chat history: {str(e)}"}

# Endpoint to delete all chat history
@app.delete("/chat-history")
def delete_all_chat_history():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history")
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
        
        return {"success": True, "message": f"Deleted {deleted_count} chat history entries"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting all chat history: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)