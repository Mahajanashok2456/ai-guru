"""
AI Service Module
Handles all Gemini API interactions and AI model operations
"""
import google.generativeai as genai
from PIL import Image
from config.settings import GEMINI_API_KEY


# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini models
text_model = genai.GenerativeModel('gemini-flash-latest')
vision_model = genai.GenerativeModel('gemini-flash-latest')


def get_text_model():
    """Get the text model instance"""
    return text_model


def get_vision_model():
    """Get the vision model instance"""
    return vision_model


def generate_text_response(prompt: str) -> str:
    """
    Generate text response using Gemini text model
    
    Args:
        prompt: The full prompt to send to the model
    
    Returns:
        Generated text response
    """
    response = text_model.generate_content(prompt)
    return response.text if response.text else "Sorry, I couldn't generate a response."


def generate_vision_response(prompt: str, image: Image.Image) -> str:
    """
    Generate response using Gemini vision model with image
    
    Args:
        prompt: The text prompt to send with the image
        image: PIL Image object
    
    Returns:
        Generated text response
    """
    response = vision_model.generate_content([prompt, image])
    return response.text


def test_gemini_connection() -> dict:
    """
    Test Gemini API connection
    
    Returns:
        Dictionary with status and response
    """
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            return {"status": "error", "message": "Gemini API key not configured"}
        
        # Test simple request
        response = text_model.generate_content("Say hello")
        return {"status": "success", "message": "Gemini API working", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": f"Gemini API error: {str(e)}"}


def build_chat_prompt(
    text: str,
    language_name: str,
    detected_lang: str,
    should_display: bool,
    learned_format_pref: str,
    learned_formality: str,
    learned_topics: list,
    recent_context: str,
    mixed_lang: str = None
) -> str:
    """
    Build personalized system prompt for chat
    """
    if should_display and detected_lang != 'en':
        system_prompt = f"""You are an intelligent AI assistant.
Your goal is to be helpful, harmless, and honest.

Key Behavior:
- Be helpful and direct. Skip wordy intros like "I can help" or "Great question".
- CONCISE BY DEFAULT: Get straight to the answer. Avoid fluff to save tokens.
- Match user's energy and format (list vs paragraph) without over-explaining.

Learned Preferences:
- Format: {learned_format_pref}
- Tone: {learned_formality}
- Topics: {', '.join(learned_topics[:3]) if learned_topics else "None yet"}

Language Rules:
- User is speaking: {language_name} ({detected_lang})
- RESPOND ONLY IN {language_name.upper()}.
- Match their dialect/script exactly (e.g., Hinglish).

Context:
{f"Recent conversation:{chr(10)}{recent_context}{chr(10)}" if recent_context else ""}
User Message: """
    else:
        from config.settings import LANGUAGE_NAMES
        system_prompt = f"""You are an intelligent AI assistant.
Your goal is to be helpful, harmless, and honest.

Key Behavior:
- Be direct and efficient. Do not use filler introductions or small talk.
- CONCISE BY DEFAULT: Provide the solution or answer immediately to save tokens.
- Match user's investment level. Short question = short, direct answer.

Learned Preferences:
- Format: {learned_format_pref}
- Tone: {learned_formality}
- Topics: {', '.join(learned_topics[:3]) if learned_topics else "None yet"}

Language Rules:
- {f"User is mixing {LANGUAGE_NAMES.get(mixed_lang, mixed_lang)} with English." if mixed_lang else "User is speaking English."}
- Match their language style exactly.

Context:
{f"Recent conversation:{chr(10)}{recent_context}{chr(10)}" if recent_context else ""}
User Message: """
    
    # Combine system prompt with user message
    full_prompt = system_prompt + text.strip()
    return full_prompt


def build_vision_prompt(
    text: str,
    language_name: str,
    detected_lang: str,
    should_display: bool,
    mixed_lang: str = None
) -> str:
    """
    Build vision system prompt for image analysis
    
    Args:
        text: User's request about the image
        language_name: Detected language name
        detected_lang: Detected language code
        should_display: Whether to display language detection
        mixed_lang: Mixed language code if detected
    
    Returns:
        Vision system prompt string
    """
    if should_display and detected_lang != 'en':
        vision_system_prompt = f"""You are an intelligent AI assistant that analyzes images while perfectly adapting to the user's communication style and needs.

🌍 CRITICAL LANGUAGE & CULTURAL RULES:
- The user is speaking in {language_name} (code: {detected_lang})
- **ABSOLUTE REQUIREMENT: RESPOND ONLY IN {language_name.upper()}** 
- If user mixes languages, match their EXACT mixed style
- Never respond in a different language unless specifically asked to translate
- Use culturally relevant references from their region

🔄 TRANSLATION EXCEPTION:
- ONLY if the user explicitly asks for translation, then provide it
- Otherwise, ALWAYS respond in {language_name}

ADAPTIVE IMAGE ANALYSIS:
- ANALYZE their request style: Simple curiosity or detailed analysis?
- SIMPLE requests ("What's this?", "Describe this") = Brief, natural description matching their tone
- DETAILED requests ("Analyze this image", "Tell me everything") = Full structured format
- CASUAL tone = Relaxed, conversational description with minimal formatting
- PROFESSIONAL context = Organized, structured analysis with appropriate sections

SMART FORMATTING (Use based on their request complexity):
- For SIMPLE questions: Natural description, minimal structure
- For COMPLEX analysis: Use **bold**, emojis 📸🎨🔍, sections, bullet points
- For TECHNICAL requests: Focus on relevant technical details with clear organization
- For EMOTIONAL/PERSONAL requests: Match their energy and use appropriate emojis

RESPONSE APPROACH & TOKEN EFFICIENCY:
- **NO INTRODUCTORY FLUFF**: Do not start with "I can help you with that" or "This image looks interesting". Start the description immediately.
- **MATCH INVESTMENT**: SHORT curiosity = SHORT, 1-2 sentence answer.
- **DETAILED analysis request** = Full structured breakdown.
- Be honest about unclear elements. No filler words.

**FINAL INSTRUCTION: RESPOND IN {language_name.upper()} ONLY** (unless specifically asked to translate). Match their exact language pattern and request style. User's request about this image: """ + text
    else:
        from config.settings import LANGUAGE_NAMES
        # For English or mixed language image requests  
        vision_system_prompt = f"""You are an intelligent AI assistant that analyzes images while perfectly adapting to the user's communication style and needs.

🌍 CRITICAL LANGUAGE RULES:
{"- **MIXED LANGUAGE DETECTED**: User is mixing " + LANGUAGE_NAMES.get(mixed_lang, mixed_lang) + " with English" if mixed_lang else "- **PRIMARY LANGUAGE**: English"}
- **ABSOLUTE REQUIREMENT: Match the user's EXACT language pattern**
- If they mix languages (Hinglish, Tenglish, etc.), respond in the SAME mixed style
- If they write pure English, respond in English
- Never randomly switch to other languages unless asked for translation

🔄 TRANSLATION EXCEPTION:
- ONLY if user explicitly asks for translation, provide it
- Otherwise, ALWAYS match their language pattern exactly

ADAPTIVE IMAGE ANALYSIS:
- ANALYZE their request style: Simple curiosity or detailed analysis?
- SIMPLE requests ("What's this?", "Describe this") = Brief, natural description matching their tone
- DETAILED requests ("Analyze this image", "Tell me everything") = Full structured format
- CASUAL tone = Relaxed, conversational description with minimal formatting  
- PROFESSIONAL context = Organized, structured analysis with appropriate sections

MANDATORY SYSTEMATIC IMAGE ANALYSIS:
- **NEVER write in paragraphs** for image descriptions
- **ALWAYS use this exact format:**

**📸 1. Main Subject**
- Key observation 1
- Key observation 2

**🎨 2. Visual Details**
- Color details
- Composition details

**🔍 3. Context & Setting**
- Environment details
- Background elements

- **Use numbered sections with emojis and bold headings**
- **Use bullet points under each section**
- **No paragraph descriptions allowed**
- **ONLY use paragraphs** if user specifically says "describe in paragraph form"

TOKEN-EFFICIENT & DIRECT RESPONSES:
- **NO SMALL TALK**: Don't say "I've analyzed the image" or "Sure, here's what I see".
- **START IMMEDIATELY**: Begin with the first section or description line.
- SHORT question = SHORT answer. don't over-explain if curiosity is simple.
- Match their investment level with your response depth.

CONVERSATION STYLE MATCHING:
- Match the user's energy and speaking style completely
- If they're casual, be casual back with natural language
- If they mix languages or use slang, mirror that naturally
- Be enthusiastic when they're excited, professional when they're formal
- Ask follow-ups only when it fits their conversation style

**FINAL LANGUAGE INSTRUCTION:**
{f"- **RESPOND IN MIXED {LANGUAGE_NAMES.get(mixed_lang, mixed_lang).upper()} + ENGLISH** (match their exact mixed pattern)" if mixed_lang else "- **RESPOND IN ENGLISH** (unless specifically asked to translate)"}
- Never randomly switch languages - match their exact input pattern
- If they ask for translation, provide it; otherwise stick to their language style

Use systematic structure by default - organize information clearly with headings and bullets. User's request about this image: """ + text
    
    return vision_system_prompt
