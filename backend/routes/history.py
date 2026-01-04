"""
Chat History Routes
Handles chat history retrieval and deletion
"""
from fastapi import APIRouter, HTTPException
import services.db_service as db_service


router = APIRouter(tags=["history"])

# Get reference to chat_collection for compatibility
chat_collection = db_service.get_chat_collection()


@router.get("/chat-history")
def get_chat_history():
    try:
        # Return empty sessions if MongoDB is not available
        if chat_collection is None:
            return {"sessions": [], "status": "MongoDB unavailable - using temporary session storage"}
        
        # Get sessions using db_service
        sessions = db_service.get_all_sessions(limit=20)
        
        grouped_history = []
        for session in sessions:
            session_id = session['_id']
            
            # Get all messages for this session using db_service
            messages = db_service.get_session_messages(session_id)
            
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


@router.delete("/chat-history/{chat_id}")
def delete_chat_history(chat_id: str):
    """Delete a specific chat history entry"""
    return db_service.delete_chat_by_id(chat_id)


@router.delete("/chat-history")
def delete_all_chat_history():
    """Delete all chat history"""
    return db_service.delete_all_chats()


@router.delete("/session/{session_id}")
def delete_session_endpoint(session_id: str):
    """Delete an entire session"""
    return db_service.delete_session(session_id)
