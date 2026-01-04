from langdetect import detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection
DetectorFactory.seed = 0

def detect_language(text: str) -> tuple:
    """
    Detect the language of input text with confidence, handling mixed languages.
    Returns tuple: (language_code, confidence, should_display)
    """
    try:
        # Clean text for better detection
        cleaned_text = text.strip()
        
        # Return None for very short text to avoid inaccurate detection
        if len(cleaned_text) < 5:
            return ('en', 0.0, False)  # Don't show detection for short text
        
        # Check for Indian scripts first (more reliable than langdetect for mixed text)
        indian_lang = detect_mixed_indian_language(cleaned_text)
        if indian_lang:
            return (indian_lang, 0.95, True)  # High confidence for script detection
        
        # Get language probabilities for other languages
        lang_probs = detect_langs(cleaned_text)
        
        if not lang_probs:
            return ('en', 0.0, False)
        
        # Get the most likely language and its confidence
        top_lang = lang_probs[0]
        language_code = top_lang.lang
        confidence = top_lang.prob
        
        # Filter out commonly mis-detected European languages for Indian English users
        problematic_codes = ['fi', 'da', 'no', 'sv', 'et', 'lv', 'lt', 'so', 'cy', 'eu', 'mt', 'ga', 'is', 'fo', 'ca', 'pt', 'ro', 'sk', 'cs', 'hr', 'sl']
        if language_code in problematic_codes:
            return ('en', 0.0, False)  # Treat as English
        
        # Only show language detection if confidence is high enough
        should_display = confidence > 0.85 and language_code != 'en'
        
        return (language_code, confidence, should_display)
        
    except (LangDetectException, Exception) as e:
        print(f"Language detection error: {e}")
        return ('en', 0.0, False)  # Default to English, don't display


def detect_mixed_indian_language(text: str) -> str:
    """Detect mixed Indian languages with English"""
    # Check for Telugu script
    if any('\u0c00' <= char <= '\u0c7f' for char in text):
        return 'te'  # Telugu
    
    # Check for Hindi/Devanagari script
    if any('\u0900' <= char <= '\u097f' for char in text):
        return 'hi'  # Hindi
    
    # Check for Bengali script
    if any('\u0980' <= char <= '\u09ff' for char in text):
        return 'bn'  # Bengali
    
    # Check for Tamil script
    if any('\u0b80' <= char <= '\u0bff' for char in text):
        return 'ta'  # Tamil
    
    # Check for Gujarati script
    if any('\u0a80' <= char <= '\u0aff' for char in text):
        return 'gu'  # Gujarati
    
    # Check for Kannada script
    if any('\u0c80' <= char <= '\u0cff' for char in text):
        return 'kn'  # Kannada
    
    # Check for Malayalam script
    if any('\u0d00' <= char <= '\u0d7f' for char in text):
        return 'ml'  # Malayalam
    
    # Check for Punjabi script
    if any('\u0a00' <= char <= '\u0a7f' for char in text):
        return 'pa'  # Punjabi
    
    return None
