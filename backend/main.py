from fastapi import FastAPI, Body, UploadFile, File, HTTPException
from pymongo import MongoClient
import tempfile
import os
import base64
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Gemini models with free tier compatible names
text_model = genai.GenerativeModel('gemini-1.5-flash-8b')
vision_model = genai.GenerativeModel('gemini-1.5-flash-8b')  # Using same model for both

# MongoDB connection config
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Mahajan:2456@cluster0.api5hwq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client.guru_multibot
chat_collection = db.chat_history

def store_interaction(input_type, user_input, bot_response, session_id=None):
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())[:8]  # Short session ID
    
    # Create document for MongoDB
    document = {
        "_id": str(uuid.uuid4()),
        "input_type": input_type,
        "user_input": user_input,
        "bot_response": bot_response,
        "session_id": session_id,
        "timestamp": datetime.utcnow()
    }
    
    # Insert into MongoDB
    chat_collection.insert_one(document)
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
    try:
        # Get sessions with their latest message timestamp for ordering using MongoDB aggregation
        pipeline = [
            {"$match": {"session_id": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$session_id",
                "latest_timestamp": {"$max": "$timestamp"},
                "message_count": {"$sum": 1},
                "first_message": {"$first": "$user_input"}
            }},
            {"$sort": {"latest_timestamp": -1}},
            {"$limit": 20}
        ]
        
        sessions = list(chat_collection.aggregate(pipeline))
        
        grouped_history = []
        for session in sessions:
            session_id = session['_id']
            
            # Get all messages for this session
            messages = list(chat_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", 1))
            
            # Convert ObjectId to string and format datetime
            for msg in messages:
                if '_id' in msg:
                    del msg['_id']
                if 'timestamp' in msg and msg['timestamp']:
                    msg['timestamp'] = msg['timestamp'].isoformat()
            
            # Create session object with first message as title
            first_message = session.get('first_message', '')
            session_title = first_message[:50] + "..." if len(first_message) > 50 else first_message
            
            grouped_history.append({
                'session_id': session_id,
                'session_title': session_title,
                'message_count': session['message_count'],
                'latest_timestamp': session['latest_timestamp'].isoformat() if session['latest_timestamp'] else None,
                'messages': messages
            })
        
        return {"sessions": grouped_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")
    return {"sessions": grouped_history}

# Endpoint to delete a specific chat history entry
@app.delete("/chat-history/{chat_id}")
def delete_chat_history(chat_id: str):
    try:
        # Check if the record exists
        existing_record = chat_collection.find_one({"_id": chat_id})
        if not existing_record:
            return {"success": False, "message": "Chat history not found"}
        
        # Delete the record
        result = chat_collection.delete_one({"_id": chat_id})
        
        if result.deleted_count > 0:
            return {"success": True, "message": "Chat history deleted successfully"}
        else:
            return {"success": False, "message": "Failed to delete chat history"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting chat history: {str(e)}"}

# Endpoint to delete all chat history
@app.delete("/chat-history")
def delete_all_chat_history():
    try:
        result = chat_collection.delete_many({})
        deleted_count = result.deleted_count
        
        return {"success": True, "message": f"Deleted {deleted_count} chat history entries"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting all chat history: {str(e)}"}

# Endpoint to delete an entire session
@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    try:
        # Check if the session exists
        count = chat_collection.count_documents({"session_id": session_id})
        
        if count == 0:
            return {"success": False, "message": "Session not found"}
        
        # Delete all messages in the session
        result = chat_collection.delete_many({"session_id": session_id})
        deleted_count = result.deleted_count
        
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