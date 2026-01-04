from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Body
from PIL import Image
import io
import traceback
from models.schemas import ChatRequest
from config.settings import LANGUAGE_NAMES, ENVIRONMENT, MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES
import services.db_service as db_service
import services.ai_service as ai_service
from utils.rate_limiter import rate_limiter
from utils.language import detect_language, detect_mixed_indian_language
from utils.interaction import store_interaction

router = APIRouter(tags=["chat"])

# Get references for compatibility
chat_collection = db_service.get_chat_collection()
text_model = ai_service.get_text_model()
vision_model = ai_service.get_vision_model()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        print(f"DEBUG: Processing chat request: {request.message[:50]}...")
        # Security: Rate limiting
        await rate_limiter.check_rate_limit(http_request.client.host)
        text = request.message
        session_id = request.session_id
        
        # Detect input language with confidence
        detected_lang, confidence, should_display = detect_language(text)
        language_name = LANGUAGE_NAMES.get(detected_lang, 'Unknown')
        
        # Get learned user preferences for personalization
        learned_prefs = db_service.get_learned_preferences(session_id) if session_id else {}
        
        # Get recent conversation context
        recent_context = ""
        if session_id and chat_collection is not None:
            try:
                recent_messages = db_service.get_recent_messages(session_id, limit=3)
                if recent_messages:
                    context_parts = []
                    for msg in reversed(recent_messages):
                        context_parts.append(f"User: {msg.get('user_input', '')}")
                        context_parts.append(f"AI: {msg.get('bot_response', '')}")
                    recent_context = "\n".join(context_parts[-4:])
            except Exception as e:
                print(f"Error getting conversation context: {e}")
        
        if ENVIRONMENT != 'production':
            print(f"Received message length: {len(text)}")
            if should_display:
                print(f"Detected language: {language_name} ({detected_lang}) - Confidence: {confidence:.2f}")
            if learned_prefs:
                print(f"🧠 Using learned preferences: {learned_prefs}")
        
        # Build personalized system prompt
        learned_format_pref = learned_prefs.get('preferred_format', 'neutral')
        learned_formality = learned_prefs.get('formality_level', 'neutral')
        learned_topics = learned_prefs.get('topics_of_interest', [])
        
        mixed_lang = detect_mixed_indian_language(text)
        
        full_prompt = ai_service.build_chat_prompt(
            text=text,
            language_name=language_name,
            detected_lang=detected_lang,
            should_display=should_display,
            learned_format_pref=learned_format_pref,
            learned_formality=learned_formality,
            learned_topics=learned_topics,
            recent_context=recent_context,
            mixed_lang=mixed_lang
        )
        
        response = text_model.generate_content(full_prompt)
        bot_response = response.text if response.text else "Sorry, I couldn't generate a response."
        print(f"Gemini response: {bot_response[:100]}...")
        
        # Store interaction
        session_id, interaction_id = store_interaction('text', text, bot_response, session_id, detected_lang if should_display else None)
        
        response_data = {
            "response": bot_response, 
            "session_id": session_id,
            "interaction_id": interaction_id
        }
        
        if should_display:
            response_data.update({
                "detected_language": detected_lang,
                "language_name": language_name,
                "confidence": confidence
            })
        
        return response_data
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        
        error_message = str(e)
        if "quota" in error_message.lower() or "429" in error_message:
            raise HTTPException(status_code=429, detail="API quota exceeded. Please wait a moment and try again.")
        else:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/image-chat")
async def image_chat(image: UploadFile = File(...), text: str = Body(..., embed=True), session_id: str = Body(None, embed=True), http_request: Request = None):
    try:
        # Security: Rate limiting
        if http_request:
            await rate_limiter.check_rate_limit(http_request.client.host)
        
        # Security: File validation
        if image.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Max size: 10MB")
        
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Unsupported file type. Use JPEG, PNG, GIF, or WebP")
        
        if not text:
            text = "Describe this image."
        
        # Detect input language
        detected_lang, confidence, should_display = detect_language(text)
        language_name = LANGUAGE_NAMES.get(detected_lang, 'Unknown')
        
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Description too long (max 1000 characters)")
        
        if should_display:
            print(f"Image chat - Detected language: {language_name} ({detected_lang}) - Confidence: {confidence:.2f}")
        
        # Read image data
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Detect mixed language
        mixed_lang = detect_mixed_indian_language(text)
        
        # Build vision prompt
        vision_system_prompt = ai_service.build_vision_prompt(
            text=text,
            language_name=language_name,
            detected_lang=detected_lang,
            should_display=should_display,
            mixed_lang=mixed_lang
        )
        
        # Generate response using Gemini Vision
        response = vision_model.generate_content([vision_system_prompt, pil_image])
        bot_response = response.text
        
        # Store interaction
        session_id, interaction_id = store_interaction('image', text, bot_response, session_id, detected_lang if should_display else None)
        
        response_data = {
            "response": bot_response, 
            "session_id": session_id,
            "interaction_id": interaction_id
        }
        
        if should_display:
            response_data.update({
                "detected_language": detected_lang,
                "language_name": language_name,
                "confidence": confidence
            })
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
