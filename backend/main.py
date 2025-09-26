from fastapi import FastAPI, Body, UploadFile, File, HTTPException, Depends, Request
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
import re
from pydantic import BaseModel, field_validator
from typing import Optional
from collections import defaultdict
from datetime import timedelta

# Load environment variables
load_dotenv()

# Security: Validate required environment variables
REQUIRED_ENV_VARS = ['GEMINI_API_KEY', 'MONGODB_URI']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Configure Gemini
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key == "your_gemini_api_key_here" or len(gemini_api_key) < 30:
    raise RuntimeError("Invalid Gemini API key detected. Please set a valid API key.")

genai.configure(api_key=gemini_api_key)

# Initialize Gemini models with free tier compatible names
text_model = genai.GenerativeModel('gemini-1.5-flash-8b')
vision_model = genai.GenerativeModel('gemini-1.5-flash-8b')  # Using same model for both

# MongoDB connection config
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Mahajan:2456@cluster0.api5hwq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client.guru_multibot
chat_collection = db.chat_history

# Security: Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, client_ip: str):
        now = datetime.now()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(seconds=self.time_window)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        self.requests[client_ip].append(now)

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=30, time_window=60)

# Security: Input validation models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:  # Limit message length
            raise ValueError('Message too long (max 5000 characters)')
        # Remove potentially dangerous characters
        v = re.sub(r'[<>"\';]', '', v.strip())
        return v
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError('Invalid session ID format')
        return v

class ImageRequest(BaseModel):
    description: str
    session_id: Optional[str] = None
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if len(v) > 1000:
            raise ValueError('Description too long (max 1000 characters)')
        v = re.sub(r'[<>"\';]', '', v.strip())
        return v

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

app = FastAPI(
    title="AI Guru Multibot API",
    description="Secure AI Chat API with MongoDB integration",
    version="2.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT') != 'production' else None,  # Hide docs in production
    redoc_url=None  # Disable redoc
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Secure CORS Configuration
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    # Add your production domains here
    # "https://your-app.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # Only needed methods
    allow_headers=["Content-Type", "Authorization"],     # Only needed headers
)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        # Security: Rate limiting
        await rate_limiter.check_rate_limit(http_request.client.host)
        text = request.message
        session_id = request.session_id
        
        # Security: Don't log sensitive data in production
        if os.getenv('ENVIRONMENT') != 'production':
            print(f"Received message length: {len(text)}")
            print(f"API Key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
        
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
async def image_chat(image: UploadFile = File(...), text: str = Body(..., embed=True), session_id: str = Body(None, embed=True), http_request: Request = None):
    try:
        # Security: Rate limiting
        if http_request:
            await rate_limiter.check_rate_limit(http_request.client.host)
        
        # Security: File validation
        MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB default
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        if image.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Max size: 10MB")
        
        if image.content_type not in allowed_types:
            raise HTTPException(status_code=415, detail="Unsupported file type. Use JPEG, PNG, GIF, or WebP")
        
        if not text:
            text = "Describe this image."
        
        # Validate text input
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Description too long (max 1000 characters)")
        
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