"""
MongoDB Database Service
Handles all MongoDB connections, operations, and data persistence
"""
from pymongo import MongoClient
from datetime import datetime
import uuid
from typing import Optional, Dict, List, Any
from config.settings import MONGODB_URI, LANGUAGE_NAMES


# MongoDB connection setup
client = None
db = None
chat_collection = None


def initialize_mongodb():
    """Initialize MongoDB connection with proper settings"""
    global client, db, chat_collection
    
    try:
        # Configure MongoDB client with proper settings
        client = MongoClient(
            MONGODB_URI,
            tlsInsecure=True,  # Disable SSL certificate verification
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=1
        )
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        db = client.guru_multibot
        chat_collection = db.chat_history
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("📝 Using fallback in-memory storage")
        # Fallback to in-memory storage if MongoDB fails
        client = None
        db = None
        chat_collection = None


def get_chat_collection():
    """Get the chat collection instance"""
    return chat_collection


def get_db():
    """Get the database instance"""
    return db


def store_interaction(
    input_type: str,
    user_input: str,
    bot_response: str,
    session_id: Optional[str] = None,
    language_code: Optional[str] = None,
    user_feedback: Optional[Dict] = None,
    input_patterns: Optional[Dict] = None,
    response_format: Optional[Dict] = None,
    interaction_context: Optional[Dict] = None
) -> tuple:
    """
    Store interaction in MongoDB
    
    Args:
        input_type: Type of input (text, image, etc.)
        user_input: User's input message
        bot_response: Bot's response
        session_id: Session identifier
        language_code: Detected language code
        user_feedback: User feedback data
        input_patterns: Analyzed input patterns
        response_format: Detected response format
        interaction_context: Contextual features
    
    Returns:
        tuple: (session_id, interaction_id)
    """
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())[:8]  # Short session ID
    
    interaction_id = None
    
    # Only store in MongoDB if connection is available
    if chat_collection is not None:
        try:
            # Generate a unique interaction ID
            interaction_id = str(uuid.uuid4())
            
            # Create document for MongoDB with learning data
            document = {
                "_id": interaction_id,
                "input_type": input_type,
                "user_input": user_input,
                "bot_response": bot_response,
                "session_id": session_id,
                "language_code": language_code,
                "language_name": LANGUAGE_NAMES.get(language_code, 'Unknown') if language_code else None,
                "timestamp": datetime.utcnow(),
                "user_feedback": user_feedback,  # Store user feedback for learning
                "response_length": len(bot_response) if bot_response else 0,
                "input_patterns": input_patterns,
                "response_format": response_format,
                "interaction_context": interaction_context
            }
            
            # Insert into MongoDB
            chat_collection.insert_one(document)
            print(f"💾 Stored interaction for session {session_id} (Language: {LANGUAGE_NAMES.get(language_code, 'Unknown')})")
            
        except Exception as e:
            print(f"⚠️ Failed to store interaction: {e}")
            interaction_id = f"{session_id}_{int(datetime.utcnow().timestamp())}"  # Fallback ID
    else:
        print(f"📝 In-memory mode: interaction not persisted for session {session_id}")
        interaction_id = f"{session_id}_{int(datetime.utcnow().timestamp())}"  # Fallback ID
    
    return session_id, interaction_id


def get_recent_interactions(session_id: str, limit: int = 5) -> List[Dict]:
    """
    Get recent interactions for a session
    
    Args:
        session_id: Session identifier
        limit: Maximum number of interactions to retrieve
    
    Returns:
        List of interaction documents
    """
    if chat_collection is None:
        return []
    
    try:
        recent_interactions = list(chat_collection.find({
            "session_id": session_id
        }).sort("timestamp", -1).limit(limit))
        return recent_interactions
    except Exception as e:
        print(f"⚠️ Failed to get recent interactions: {e}")
        return []


def get_recent_messages(session_id: str, limit: int = 3) -> List[Dict]:
    """
    Get recent messages for conversation context
    
    Args:
        session_id: Session identifier
        limit: Maximum number of messages to retrieve
    
    Returns:
        List of message documents
    """
    if chat_collection is None:
        return []
    
    try:
        recent_messages = list(chat_collection.find({
            "session_id": session_id
        }).sort("timestamp", -1).limit(limit))
        return recent_messages
    except Exception as e:
        print(f"Error getting conversation context: {e}")
        return []


def store_learned_patterns(session_id: str, user_preferences: Dict, interaction_count: int):
    """
    Store learned patterns in a separate collection
    
    Args:
        session_id: Session identifier
        user_preferences: Analyzed user preferences
        interaction_count: Number of interactions analyzed
    """
    if db is None:
        return
    
    try:
        learning_collection = db.learned_patterns
        
        learning_document = {
            "session_id": session_id,
            "user_preferences": user_preferences,
            "last_updated": datetime.utcnow(),
            "interaction_count": interaction_count
        }
        
        # Upsert (update or insert) learning data
        learning_collection.replace_one(
            {"session_id": session_id},
            learning_document,
            upsert=True
        )
        
        print(f"🧠 Updated learning patterns for session {session_id}")
        
    except Exception as e:
        print(f"⚠️ Failed to store learned patterns: {e}")


def get_learned_preferences(session_id: str) -> Dict:
    """
    Retrieve learned preferences for a session
    
    Args:
        session_id: Session identifier
    
    Returns:
        Dictionary of user preferences
    """
    try:
        if db is None:
            return {}
        
        learning_collection = db.learned_patterns
        learned_data = learning_collection.find_one({"session_id": session_id})
        
        if learned_data and "user_preferences" in learned_data:
            return learned_data["user_preferences"]
        
    except Exception as e:
        print(f"⚠️ Failed to retrieve learned preferences: {e}")
    
    return {}


def get_all_sessions(limit: int = 20) -> List[Dict]:
    """
    Get all chat sessions with their metadata
    
    Args:
        limit: Maximum number of sessions to retrieve
    
    Returns:
        List of session documents
    """
    if chat_collection is None:
        return []
    
    try:
        pipeline = [
            {"$match": {"session_id": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$session_id",
                "latest_timestamp": {"$max": "$timestamp"},
                "message_count": {"$sum": 1},
                "first_message": {"$first": "$user_input"}
            }},
            {"$sort": {"latest_timestamp": -1}},
            {"$limit": limit}
        ]
        
        sessions = list(chat_collection.aggregate(pipeline))
        return sessions
        
    except Exception as e:
        print(f"⚠️ Failed to get sessions: {e}")
        return []


def get_session_messages(session_id: str) -> List[Dict]:
    """
    Get all messages for a specific session
    
    Args:
        session_id: Session identifier
    
    Returns:
        List of message documents
    """
    if chat_collection is None:
        return []
    
    try:
        messages = list(chat_collection.find(
            {"session_id": session_id}
        ).sort("timestamp", 1))
        
        # Convert ObjectId to string and format datetime
        for msg in messages:
            if '_id' in msg:
                del msg['_id']
            if 'timestamp' in msg and msg['timestamp']:
                msg['timestamp'] = msg['timestamp'].isoformat()
        
        return messages
        
    except Exception as e:
        print(f"⚠️ Failed to get session messages: {e}")
        return []


def delete_chat_by_id(chat_id: str) -> Dict:
    """
    Delete a specific chat history entry
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Dictionary with success status and message
    """
    if chat_collection is None:
        return {"success": False, "message": "Database unavailable"}
    
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


def delete_all_chats() -> Dict:
    """
    Delete all chat history
    
    Returns:
        Dictionary with success status and message
    """
    if chat_collection is None:
        return {"success": False, "message": "Database unavailable"}
    
    try:
        result = chat_collection.delete_many({})
        deleted_count = result.deleted_count
        
        return {"success": True, "message": f"Deleted {deleted_count} chat history entries"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting all chat history: {str(e)}"}


def delete_session(session_id: str) -> Dict:
    """
    Delete an entire session and its learned patterns
    
    Args:
        session_id: Session identifier
    
    Returns:
        Dictionary with success status and message
    """
    if chat_collection is None:
        return {"success": False, "message": "Database unavailable"}
    
    try:
        # Check if the session exists
        count = chat_collection.count_documents({"session_id": session_id})
        
        if count == 0:
            return {"success": False, "message": "Session not found"}
        
        # Delete all messages in the session
        result = chat_collection.delete_many({"session_id": session_id})
        deleted_count = result.deleted_count
        
        # Also delete learned patterns for this session
        if db is not None:
            learning_collection = db.learned_patterns
            learning_collection.delete_one({"session_id": session_id})
        
        return {"success": True, "message": f"Session deleted successfully. {deleted_count} messages removed."}
    except Exception as e:
        return {"success": False, "message": f"Error deleting session: {str(e)}"}


def get_interaction_by_id(interaction_id: str) -> Optional[Dict]:
    """
    Get a specific interaction by ID
    
    Args:
        interaction_id: Interaction identifier
    
    Returns:
        Interaction document or None
    """
    if chat_collection is None:
        return None
    
    try:
        interaction = chat_collection.find_one({"_id": interaction_id})
        return interaction
    except Exception as e:
        print(f"⚠️ Failed to get interaction: {e}")
        return None


def update_interaction_feedback(interaction_id: str, feedback_data: Dict) -> bool:
    """
    Update interaction with user feedback
    
    Args:
        interaction_id: Interaction identifier
        feedback_data: Feedback data to store
    
    Returns:
        True if successful, False otherwise
    """
    if chat_collection is None:
        return False
    
    try:
        chat_collection.update_one(
            {"_id": interaction_id},
            {"$set": {"user_feedback": feedback_data}}
        )
        return True
    except Exception as e:
        print(f"⚠️ Failed to update feedback: {e}")
        return False


def store_feedback_analysis(feedback_analysis: Dict):
    """
    Store detailed feedback analysis
    
    Args:
        feedback_analysis: Feedback analysis data
    """
    if db is None:
        return
    
    try:
        feedback_collection = db.user_feedback
        feedback_collection.insert_one(feedback_analysis)
    except Exception as e:
        print(f"⚠️ Failed to store feedback analysis: {e}")


def update_learned_patterns_from_feedback(
    session_id: str,
    current_patterns: Dict,
    feedback_type: str,
    interaction: Dict,
    feedback_timestamp: datetime
):
    """
    Update learned patterns based on user feedback
    
    Args:
        session_id: Session identifier
        current_patterns: Current learned patterns
        feedback_type: Type of feedback
        interaction: Interaction data
        feedback_timestamp: Timestamp of feedback
    """
    if db is None:
        return
    
    try:
        learning_collection = db.learned_patterns
        
        # Update patterns based on feedback
        user_prefs = current_patterns.get("user_preferences", {})
        
        if feedback_type == "format_mismatch":
            # User didn't like the format - adjust preference
            input_patterns = interaction.get("input_patterns", {})
            requested_format = input_patterns.get("request_type", "unknown")
            user_prefs["preferred_format"] = requested_format
        
        elif feedback_type == "too_long":
            user_prefs["preferred_length"] = "short"
        
        elif feedback_type == "too_short":
            user_prefs["preferred_length"] = "detailed"
        
        elif feedback_type == "thumbs_up":
            # Reinforce current patterns
            response_format = interaction.get("response_format", {})
            if "format_type" in response_format:
                user_prefs["preferred_format"] = response_format["format_type"]
        
        # Add feedback to history
        feedback_history = current_patterns.get("feedback_history", [])
        feedback_history.append({
            "feedback_type": feedback_type,
            "timestamp": feedback_timestamp,
            "interaction_context": {
                "request_type": interaction.get("input_patterns", {}).get("request_type"),
                "response_format": interaction.get("response_format", {}).get("format_type"),
                "response_length": len(interaction.get("bot_response", ""))
            }
        })
        
        # Keep only recent feedback (last 20 items)
        feedback_history = feedback_history[-20:]
        
        # Update the document
        updated_patterns = {
            "session_id": session_id,
            "user_preferences": user_prefs,
            "feedback_history": feedback_history,
            "last_updated": datetime.utcnow(),
            "total_feedback_count": len(feedback_history)
        }
        
        learning_collection.replace_one(
            {"session_id": session_id},
            updated_patterns,
            upsert=True
        )
        
        print(f"🎯 Updated learning patterns for session {session_id} based on {feedback_type} feedback")
        
    except Exception as e:
        print(f"⚠️ Failed to update learned patterns from feedback: {e}")


def get_learning_analytics() -> Dict:
    """
    Get analytics about the AI's learning progress
    
    Returns:
        Dictionary with learning analytics
    """
    if db is None:
        return {"status": "Database unavailable"}
    
    try:
        learning_collection = db.learned_patterns
        feedback_collection = db.user_feedback
        
        # Get learning statistics
        total_sessions_with_learning = learning_collection.count_documents({})
        
        # Get feedback statistics
        feedback_stats = {}
        if feedback_collection:
            pipeline = [
                {"$group": {
                    "_id": "$feedback_type",
                    "count": {"$sum": 1}
                }}
            ]
            feedback_results = list(feedback_collection.aggregate(pipeline))
            feedback_stats = {item["_id"]: item["count"] for item in feedback_results}
        
        # Get common user preferences
        user_preferences = list(learning_collection.find({}, {"user_preferences": 1, "session_id": 1}))
        
        format_preferences = {}
        formality_preferences = {}
        
        for pref_doc in user_preferences:
            prefs = pref_doc.get("user_preferences", {})
            
            fmt_pref = prefs.get("preferred_format", "unknown")
            format_preferences[fmt_pref] = format_preferences.get(fmt_pref, 0) + 1
            
            form_pref = prefs.get("formality_level", "unknown")
            formality_preferences[form_pref] = formality_preferences.get(form_pref, 0) + 1
        
        return {
            "learning_stats": {
                "sessions_with_learning_data": total_sessions_with_learning,
                "total_feedback_received": sum(feedback_stats.values()) if feedback_stats else 0
            },
            "feedback_breakdown": feedback_stats,
            "user_preference_trends": {
                "format_preferences": format_preferences,
                "formality_preferences": formality_preferences
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get learning analytics: {str(e)}"}


def calculate_learning_effectiveness() -> Any:
    """
    Calculate how well the AI is learning from feedback
    
    Returns:
        Dictionary with effectiveness metrics or status message
    """
    if db is None:
        return "Database unavailable"
    
    try:
        feedback_collection = db.user_feedback
        
        # Get recent feedback (last 50 interactions)
        recent_feedback = list(feedback_collection.find({}).sort("feedback_timestamp", -1).limit(50))
        
        if len(recent_feedback) < 10:
            return "Insufficient data for effectiveness calculation"
        
        positive_feedback = sum(1 for fb in recent_feedback if fb.get("feedback_type") in ["thumbs_up"])
        negative_feedback = sum(1 for fb in recent_feedback if fb.get("feedback_type") in ["thumbs_down", "format_mismatch", "off_topic"])
        
        if positive_feedback + negative_feedback == 0:
            return "No explicit positive/negative feedback received"
        
        effectiveness_score = positive_feedback / (positive_feedback + negative_feedback)
        
        return {
            "effectiveness_percentage": round(effectiveness_score * 100, 1),
            "recent_feedback_analyzed": len(recent_feedback),
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "improvement_status": "improving" if effectiveness_score > 0.7 else "needs_improvement"
        }
        
    except Exception as e:
        return f"Error calculating effectiveness: {str(e)}"


# Initialize MongoDB connection when module is imported
initialize_mongodb()
