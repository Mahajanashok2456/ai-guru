from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from models.schemas import FeedbackRequest
import services.db_service as db_service
from utils.rate_limiter import rate_limiter
from utils.interaction import learn_from_feedback

router = APIRouter(tags=["feedback"])

# Get references for compatibility
chat_collection = db_service.get_chat_collection()

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest, http_request: Request):
    """Allow users to provide feedback on AI responses for continuous learning"""
    try:
        # Security: Rate limiting for feedback
        await rate_limiter.check_rate_limit(http_request.client.host)
        
        if chat_collection is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Find the interaction to update using db_service
        interaction = db_service.get_interaction_by_id(feedback.interaction_id)
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        # Update interaction with feedback
        feedback_data = {
            "feedback_type": feedback.feedback_type,
            "feedback_text": feedback.feedback_text,
            "feedback_timestamp": datetime.utcnow()
        }
        
        # Update using db_service
        db_service.update_interaction_feedback(feedback.interaction_id, feedback_data)
        
        # Learn from this feedback
        learn_from_feedback(interaction, feedback_data)
        
        return {
            "success": True, 
            "message": "Feedback received. The AI will learn from this to improve future responses!",
            "feedback_type": feedback.feedback_type
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")
