import services.db_service as db_service
import services.learning_service as learning_service
from datetime import datetime

def store_interaction(input_type, user_input, bot_response, session_id=None, language_code=None, user_feedback=None):
    """Wrapper function for db_service.store_interaction to maintain compatibility"""
    # Analyze patterns before storing using learning_service
    input_patterns = learning_service.analyze_input_patterns(user_input)
    response_format = learning_service.detect_response_format(bot_response)
    interaction_context = learning_service.extract_context_features(user_input, bot_response)
    
    # Store using db_service
    session_id, interaction_id = db_service.store_interaction(
        input_type=input_type,
        user_input=user_input,
        bot_response=bot_response,
        session_id=session_id,
        language_code=language_code,
        user_feedback=user_feedback,
        input_patterns=input_patterns,
        response_format=response_format,
        interaction_context=interaction_context
    )
    
    # Learn from this interaction for future improvements
    chat_collection = db_service.get_chat_collection()
    if chat_collection is not None:
        learn_from_interaction({
            "_id": interaction_id,
            "session_id": session_id,
            "user_input": user_input,
            "bot_response": bot_response,
            "input_patterns": input_patterns,
            "response_format": response_format,
            "interaction_context": interaction_context
        })
    
    return session_id, interaction_id

def learn_from_interaction(interaction_data):
    """Learn patterns from successful interactions to improve future responses"""
    try:
        chat_collection = db_service.get_chat_collection()
        if chat_collection is None:
            return
        
        # Analyze recent interactions for learning patterns using db_service
        recent_interactions = db_service.get_recent_interactions(
            interaction_data["session_id"],
            limit=5
        )
        
        # Learn user preferences for this session
        user_preferences = learning_service.analyze_user_preferences(recent_interactions)
        
        # Store learned patterns using db_service
        db_service.store_learned_patterns(
            session_id=interaction_data["session_id"],
            user_preferences=user_preferences,
            interaction_count=len(recent_interactions)
        )
            
    except Exception as e:
        print(f"⚠️ Learning process failed: {e}")

def learn_from_feedback(interaction, feedback_data):
    """Learn from user feedback to improve future responses"""
    try:
        db = db_service.get_db()
        if db is None:
            return
        
        session_id = interaction.get("session_id")
        
        # Store detailed feedback analysis using db_service
        feedback_analysis = {
            "session_id": session_id,
            "interaction_id": interaction.get("_id"),
            "feedback_type": feedback_data["feedback_type"],
            "user_input": interaction.get("user_input"),
            "bot_response": interaction.get("bot_response"),
            "input_patterns": interaction.get("input_patterns", {}),
            "response_format": interaction.get("response_format", {}),
            "feedback_timestamp": feedback_data["feedback_timestamp"],
            "improvement_suggestions": learning_service.generate_improvement_suggestions(interaction, feedback_data)
        }
        
        db_service.store_feedback_analysis(feedback_analysis)
        
        # Update learned patterns based on feedback
        if session_id:
            update_learned_patterns_from_feedback(session_id, interaction, feedback_data)
        
        print(f"🧠 Learned from {feedback_data['feedback_type']} feedback for session {session_id}")
        
    except Exception as e:
        print(f"⚠️ Failed to learn from feedback: {e}")

def update_learned_patterns_from_feedback(session_id, interaction, feedback_data):
    """Update learned patterns based on user feedback"""
    try:
        db = db_service.get_db()
        if db is None:
            return
        
        feedback_type = feedback_data["feedback_type"]
        
        # Get current learned patterns
        learning_collection = db.learned_patterns
        current_patterns = learning_collection.find_one({"session_id": session_id})
        if not current_patterns:
            current_patterns = {
                "session_id": session_id,
                "user_preferences": {},
                "feedback_history": [],
                "last_updated": datetime.utcnow()
            }
        
        # Update patterns using db_service
        db_service.update_learned_patterns_from_feedback(
            session_id=session_id,
            current_patterns=current_patterns,
            feedback_type=feedback_type,
            interaction=interaction,
            feedback_timestamp=feedback_data["feedback_timestamp"]
        )
        
    except Exception as e:
        print(f"⚠️ Failed to update learned patterns from feedback: {e}")
