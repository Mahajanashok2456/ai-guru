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

def store_interaction(input_type, user_input, bot_response, session_id=None):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Create session_id column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE chat_history ADD COLUMN session_id VARCHAR(50)")
        conn.commit()
    except mysql.connector.Error:
        pass  # Column already exists
    
    # Generate session_id if not provided
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())[:8]  # Short session ID
    
    query = "INSERT INTO chat_history (input_type, user_input, bot_response, session_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (input_type, user_input, bot_response, session_id))
    conn.commit()
    cursor.close()
    conn.close()
    return session_id

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
    session_id = data.get("session_id")  # Get session_id from frontend
    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': text}])
    bot_response = response['message']['content']
    session_id = store_interaction('text', text, bot_response, session_id)
    return {"response": bot_response, "session_id": session_id}

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...), session_id: str = None):
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
        session_id = store_interaction('voice', transcribed_text, response_text, session_id)
        return {"response": response_text, "session_id": session_id}
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

# Endpoint to fetch all chat history grouped by sessions
@app.get("/chat-history")
def get_chat_history():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Get sessions with their latest message timestamp for ordering
    cursor.execute("""
        SELECT session_id, 
               MAX(timestamp) as latest_timestamp,
               COUNT(*) as message_count
        FROM chat_history 
        WHERE session_id IS NOT NULL
        GROUP BY session_id 
        ORDER BY latest_timestamp DESC 
        LIMIT 20
    """)
    sessions = cursor.fetchall()
    
    grouped_history = []
    for session in sessions:
        session_id = session['session_id']
        
        # Get all messages for this session
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE session_id = %s 
            ORDER BY timestamp ASC
        """, (session_id,))
        messages = cursor.fetchall()
        
        # Create session object with first message as title
        session_title = messages[0]['user_input'][:50] + "..." if len(messages[0]['user_input']) > 50 else messages[0]['user_input']
        
        grouped_history.append({
            'session_id': session_id,
            'session_title': session_title,
            'message_count': session['message_count'],
            'latest_timestamp': session['latest_timestamp'],
            'messages': messages
        })
    
    cursor.close()
    conn.close()
    return {"sessions": grouped_history}

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

# Endpoint to delete an entire session
@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if the session exists
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE session_id = %s", (session_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Session not found"}
        
        # Delete all messages in the session
        cursor.execute("DELETE FROM chat_history WHERE session_id = %s", (session_id,))
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
        
        return {"success": True, "message": f"Session deleted successfully. {deleted_count} messages removed."}
    except Exception as e:
        return {"success": False, "message": f"Error deleting session: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)