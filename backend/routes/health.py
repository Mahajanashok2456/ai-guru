"""
Health Check Routes
Handles health check and test endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import services.ai_service as ai_service


router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    return {"message": "AI Guru Multibot API is running", "docs": "/docs"}


@router.get("/test-gemini")
def test_gemini():
    """Test endpoint to verify Gemini API connection"""
    try:
        result = ai_service.test_gemini_connection()
        return result
    except Exception as e:
        return {"status": "error", "message": f"Gemini API test failed: {str(e)}"}


@router.get("/feedback-test")
def test_feedback_endpoint():
    """Test endpoint to verify feedback system is working"""
    return {"status": "Feedback endpoint is working!", "timestamp": datetime.utcnow().isoformat()}
