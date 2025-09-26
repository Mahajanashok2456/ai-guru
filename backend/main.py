from fastapi import FastAPI, Body, UploadFile, File, HTTPException
import mysql.connector
import tempfile
import os
import base64
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Gemini models with free tier compatible names
text_model = genai.GenerativeModel('gemini-1.5-flash-8b')
vision_model = genai.GenerativeModel('gemini-1.5-flash-8b')  # Using same model for both

# MySQL connection config
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '2456'),
    'database': os.getenv('DB_NAME', 'guru_multibot'),
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
    try:
        text = data.get("message")
        session_id = data.get("session_id")  # Get session_id from frontend
        
        print(f"Received message: {text}")
        print(f"API Key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
        
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response using Gemini
        print("Calling Gemini API...")
        response = text_model.generate_content(text.strip())
        bot_response = response.text if response.text else "Sorry, I couldn't generate a response."
        print(f"Gemini response: {bot_response[:100]}...")
        
        # Store interaction in database
        session_id = store_interaction('text', text, bot_response, session_id)
        return {"response": bot_response, "session_id": session_id}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # Handle specific API errors
        error_message = str(e)
        if "quota" in error_message.lower() or "429" in error_message:
            error_detail = "API quota exceeded. Please wait a moment and try again, or check your Gemini API billing settings."
        elif "404" in error_message and "model" in error_message.lower():
            error_detail = "Model not found. Please check your Gemini API configuration."
        elif "api key" in error_message.lower() or "authentication" in error_message.lower():
            error_detail = "Invalid API key. Please check your Gemini API key configuration."
        else:
            error_detail = f"Error generating response: {str(e)}"
            
        raise HTTPException(status_code=500, detail=error_detail)

# Test endpoint to verify Gemini API connection
@app.get("/test-gemini")
async def test_gemini():
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_gemini_api_key_here":
            return {"status": "error", "message": "Gemini API key not configured"}
        
        # Test simple request
        response = text_model.generate_content("Say hello")
        return {"status": "success", "message": "Gemini API working", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": f"Gemini API error: {str(e)}"}

# Voice chat functionality removed - not supported with Gemini API only
# Use text chat instead

@app.post("/image-chat")
async def image_chat(image: UploadFile = File(...), text: str = Body(..., embed=True), session_id: str = Body(None, embed=True)):
    try:
        if not text:
            text = "Describe this image."
        
        # Read image data
        image_bytes = await image.read()
        
        # Convert to PIL Image for Gemini
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Generate response using Gemini Vision
        response = vision_model.generate_content([text, pil_image])
        bot_response = response.text
        
        # Store interaction in database
        session_id = store_interaction('image', text, bot_response, session_id)
        return {"response": bot_response, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

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
    print("🚀 Starting AI Guru Multibot Backend...")
    print("📡 API Documentation: http://localhost:8001/docs")
    print("🔗 Chat API: http://localhost:8001/chat")
    print("🧪 Test Gemini: http://localhost:8001/test-gemini")
    uvicorn.run(app, host="0.0.0.0", port=8001)