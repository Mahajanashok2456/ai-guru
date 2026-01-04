"""
Configuration and Settings Module
Handles environment variables, constants, and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security: Validate required environment variables
REQUIRED_ENV_VARS = ['GEMINI_API_KEY', 'MONGODB_URI']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY == "your_gemini_api_key_here" or len(GEMINI_API_KEY) < 30:
    raise RuntimeError("Invalid Gemini API key detected. Please set a valid API key.")

# MongoDB connection config
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise RuntimeError("🚨 MONGODB_URI environment variable is required but not set!")

# Rate limiting settings
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_TIME_WINDOW = 60  # seconds

# File upload settings
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB default
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    # Add your production domains here
    # "https://your-app.vercel.app"
]

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Language names mapping for better user experience
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French', 
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'te': 'Telugu',
    'ta': 'Tamil',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'pl': 'Polish',
    'cs': 'Czech',
    'sk': 'Slovak',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'uk': 'Ukrainian',
    'be': 'Belarusian',
    'mk': 'Macedonian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'tr': 'Turkish',
    'az': 'Azerbaijani',
    'kk': 'Kazakh',
    'ky': 'Kyrgyz',
    'uz': 'Uzbek',
    'mn': 'Mongolian',
    'fa': 'Persian',
    'ps': 'Pashto',
    'ku': 'Kurdish',
    'he': 'Hebrew',
    'yi': 'Yiddish',
    'am': 'Amharic',
    'ti': 'Tigrinya',
    'or': 'Odia',
    'as': 'Assamese',
    'my': 'Myanmar',
    'km': 'Khmer',
    'lo': 'Lao',
    'ka': 'Georgian',
    'hy': 'Armenian',
    'is': 'Icelandic',
    'fo': 'Faroese',
    'sq': 'Albanian',
    'el': 'Greek',
    'la': 'Latin',
    'sw': 'Swahili',
    'zu': 'Zulu',
    'xh': 'Xhosa',
    'af': 'Afrikaans',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'ha': 'Hausa',
}
