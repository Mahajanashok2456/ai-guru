from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import pymongo
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Mahabharata & Ramayana Chat API", version="1.0.0")

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    question: str

class TestRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    intent: str
    source_evidence: List[Dict[str, Any]]

# Global variables for MongoDB and Gemini
mongodb_client: Optional[MongoClient] = None
gemini_model: Optional[genai.GenerativeModel] = None
EMBEDDING_MODEL_NAME = "models/text-embedding-004"

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongodb_client
    try:
        atlas_uri = os.getenv("ATLAS_URI")
        if not atlas_uri:
            raise ValueError("ATLAS_URI environment variable not set")

        mongodb_client = MongoClient(atlas_uri)
        # Test the connection
        mongodb_client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        return mongodb_client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def init_gemini():
    """Initialize Gemini AI"""
    global gemini_model
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Use the specific model requested
        try:
            gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini AI initialized successfully with gemini-2.5-flash")
            return gemini_model
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI with gemini-2.5-flash: {e}")
            raise Exception(f"Failed to initialize Gemini AI with gemini-2.5-flash. Please check your API key and internet connection. Error: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI: {e}")
        raise

def router_function(message: str) -> str:
    """
    Classify user intent as factual, guidance, or general
    """
    try:
        if gemini_model is None:
            logger.error("Gemini model not initialized")
            return "general"

        router_prompt = f"""
        Analyze the following user message and classify it into exactly one of these categories:
        - factual: Questions about specific events, characters, locations, or historical facts from Mahabharata or Ramayana
        - guidance: Questions seeking wisdom, life advice, moral lessons, or spiritual guidance from the epics
        - general: Casual conversation, greetings, or questions not specifically about the epics

        Message: "{message}"

        Return only one word: factual, guidance, or general.
        """

        response = gemini_model.generate_content(router_prompt)
        intent = response.text.strip().lower()

        # Ensure we return only valid intents
        if intent not in ["factual", "guidance", "general"]:
            intent = "general"

        return intent
    except Exception as e:
        logger.error(f"Error in router function: {e}")
        return "general"

def get_adaptive_prompt(question: str, context: List[Dict]) -> str:
    """
    Generates a prompt that:
    1. Analyzes user tone/intent.
    2. Uses retrieved context (Knowledge Base).
    3. Frames the answer accordingly.
    """
    if not context:
        # Fallback if no context found (relying on internal knowledge)
        return f"""
        You are a wise and adaptive companion.
        
        USER INPUT: "{question}"
        
        ### INSTRUCTIONS:
        1. **Analyze Tone & Intent**: Determine the user's emotional state and underlying need.
        2. **Internal Knowledge**: Since no specific text was retrieved, access your internal knowledge of the Mahabharata and Ramayana.
        3. **Frame the Answer**:
           - **Tone Matching**: Adapt your language to the user's tone. Be empathetic if they are emotional, precise if they are factual.
           - **Seamless Delivery**: Provide the wisdom/facts directly. Do not apologize for not finding text. Just give the best answer you can based on the Epics.
        """

    context_str = "\n".join([f"Info: {doc.get('text', '')}" for doc in context[:4]])

    return f"""
    You are a wise and adaptive companion.

    USER INPUT: "{question}"

    ### INSTRUCTIONS:
    1. **Analyze Tone & Intent**: First, rigorously understand what the user is really asking and how they are feeling (e.g., Are they distressed? Curious? Skeptical? seeking validation?).
    2. **Check Facts (Knowledge Base)**: Use ONLY the following retrieved fragments from the Ancient Epics as your source of truth.
       - KNOWLEDGE BASE:
       {context_str}
    3. **Frame the Answer**:
       - Synthesize the answer using the knowledge above.
       - **Length**: KEEP IT CONCISE. Do not write an essay. Provide 1-2 powerful paragraphs (max 4-5 sentences total).
       - **Tone Matching**: THIS IS CRITICAL. If the user is sad, be a comforting friend. If they are asking a sharp question, be a sharp scholar. Match their energy.
       - **Seamless Integration**: Do NOT say "The Knowledge Base says" or "In the text". Speak the answer as if it is your own deep wisdom. weaving the facts naturally into your response.
    """

def perform_vector_search(query: str, limit: int = 5) -> List[Dict]:
    """Perform vector search on MongoDB"""
    try:
        if mongodb_client is None:
            logger.error("MongoDB client not initialized")
            return []

        db = mongodb_client["mahabharata_db"]
        collection = db["texts"]

        # Generate embedding for the query using Gemini
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=query,
            task_type="retrieval_document"
        )

        query_embedding = result['embedding']

        # Perform vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "text_embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 2,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "text": 1,
                    "source": 1,
                    "chapter": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return []

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        logger.info(f"Received question: {request.question}")

        # Check if services are initialized
        if mongodb_client is None:
            logger.error("MongoDB client is None")
            return ChatResponse(
                answer="MongoDB connection failed. Please check your ATLAS_URI in the .env file.",
                intent="general",
                source_evidence=[]
            )

        if gemini_model is None:
            logger.error("Gemini model is None")
            return ChatResponse(
                answer="Gemini AI initialization failed. Please check your GEMINI_API_KEY in the .env file.",
                intent="general",
                source_evidence=[]
            )

        # Classify intent
        intent = router_function(request.question)
        logger.info(f"Classified intent: {intent}")

        response_data = {
            "answer": "",
            "intent": intent,
            "source_evidence": []
        }

        if intent in ["factual", "guidance"]:
            # Query expansion for better context retrieval
            expanded_query = request.question
            try:
                expansion_prompt = f"""
                Analyze the following user question and generate 2-3 keywords or short phrases that represent the core emotional themes, moral dilemmas, or epic concepts from Mahabharata and Ramayana that are relevant to the user's situation.

                User question: "{request.question}"

                Provide only the keywords or phrases, separated by commas. Examples: betrayal, dharma dilemma, grief, karma, resilience.
                """
                expansion_response = gemini_model.generate_content(expansion_prompt)
                themes = [theme.strip() for theme in expansion_response.text.strip().split(',') if theme.strip()]
                if themes:
                    expanded_query = request.question + " " + " ".join(themes)
                    logger.info(f"Expanded query: {expanded_query}")
            except Exception as e:
                logger.warning(f"Query expansion failed: {e}. Using original question.")

            # Perform vector search for context using expanded query
            search_results = perform_vector_search(expanded_query)

            if search_results:
                response_data["source_evidence"] = [
                    {
                        "text": doc.get("text", ""),
                        "source": doc.get("source", "Unknown"),
                        "chapter": doc.get("chapter", ""),
                        "score": doc.get("score", 0)
                    }
                    for doc in search_results
                ]

                # Use the new unified adaptive prompt for both factual and guidance
                prompt = get_adaptive_prompt(request.question, search_results)

                # Get response from Gemini
                response = gemini_model.generate_content(prompt)
                response_data["answer"] = response.text
            else:
                # Use the same unified prompt but with empty context (triggers fallback logic inside)
                prompt = get_adaptive_prompt(request.question, [])
                response = gemini_model.generate_content(prompt)
                response_data["answer"] = response.text
        else:
            # General conversation
            general_prompt = f"""
            You are a wise, empathetic, and supportive companion.
            
            The user message is: "{request.question}"

            Please respond in a warm, friendly, and grounded manner.
            Do not mention that you are an AI or that you rely on the Mahabharata or Ramayana.
            Simply offer your presence, your ear, and a willingness to discuss life, challenges, or wisdom.
            If the user says "Hello" or greets you, welcome them delicately and ask how they are feeling today.
            """

            response = gemini_model.generate_content(general_prompt)
            response_data["answer"] = response.text

        return ChatResponse(**response_data)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            answer=f"An error occurred: {str(e)}. Please check the backend logs for details.",
            intent="general",
            source_evidence=[]
        )

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    try:
        init_mongodb()
        init_gemini()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Don't raise the exception - let the server start anyway
        # This way the /chat endpoint can still return meaningful errors

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Mahabharata & Ramayana Chat API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mongodb": "connected", "gemini": "initialized"}

@app.post("/test")
async def simple_test_endpoint(request: TestRequest):
    """Simple test endpoint that doesn't use MongoDB or Gemini"""
    return {
        "message": "Test successful!",
        "received_question": request.question,
        "length": len(request.question)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)