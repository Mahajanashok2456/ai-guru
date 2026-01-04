"""
Learning Service Module
Handles all learning, feedback, and pattern analysis logic
"""
import re
from typing import Dict, List, Any
from collections import Counter


def analyze_input_patterns(user_input: str) -> Dict[str, Any]:
    """Analyze patterns in user input to learn preferences"""
    patterns = {
        "request_type": "",
        "formality_level": "",
        "length_preference": "",
        "keywords": []
    }
    
    user_input_lower = user_input.lower()
    
    # Detect request type
    if any(word in user_input_lower for word in ['paragraph', 'write', 'describe', 'tell me about', 'essay']):
        patterns["request_type"] = "paragraph"
    elif any(word in user_input_lower for word in ['explain', 'list', 'break down', 'steps', 'outline']):
        patterns["request_type"] = "structured"
    elif any(word in user_input_lower for word in ['hi', 'hello', 'thanks', 'how are you']):
        patterns["request_type"] = "casual"
    else:
        patterns["request_type"] = "mixed"
    
    # Detect formality level
    formal_indicators = ['please', 'could you', 'would you', 'kindly', 'sir', 'madam']
    casual_indicators = ['hey', 'yo', 'sup', 'what\'s up', 'cool', 'awesome']
    
    if any(word in user_input_lower for word in formal_indicators):
        patterns["formality_level"] = "formal"
    elif any(word in user_input_lower for word in casual_indicators):
        patterns["formality_level"] = "casual"
    else:
        patterns["formality_level"] = "neutral"
    
    # Length preference detection
    if len(user_input) < 20:
        patterns["length_preference"] = "short"
    elif len(user_input) > 100:
        patterns["length_preference"] = "detailed"
    else:
        patterns["length_preference"] = "medium"
    
    # Extract key topics/keywords
    words = re.findall(r'\b[a-zA-Z]{3,}\b', user_input.lower())
    common_words = {'the', 'and', 'you', 'for', 'are', 'with', 'can', 'about', 'what', 'how', 'that', 'this'}
    patterns["keywords"] = [word for word in words if word not in common_words][:10]
    
    return patterns


def detect_response_format(bot_response: str) -> Dict[str, Any]:
    """Analyze the format of bot response"""
    if not bot_response:
        return "empty"
    
    format_info = {
        "has_bullets": bool(re.search(r'^[\s]*[-•*]', bot_response, re.MULTILINE)),
        "has_numbering": bool(re.search(r'^[\s]*\d+\.', bot_response, re.MULTILINE)),
        "has_sections": bool(re.search(r'\*\*.*\*\*', bot_response)),
        "has_emojis": bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', bot_response)),
        "length": len(bot_response),
        "format_type": ""
    }
    
    if format_info["has_sections"] and (format_info["has_bullets"] or format_info["has_numbering"]):
        format_info["format_type"] = "structured"
    elif not format_info["has_bullets"] and not format_info["has_numbering"] and not format_info["has_sections"]:
        format_info["format_type"] = "paragraph"
    else:
        format_info["format_type"] = "mixed"
    
    return format_info


def extract_context_features(user_input: str, bot_response: str) -> Dict[str, Any]:
    """Extract contextual features for learning"""
    return {
        "topic": extract_topic(user_input),
        "sentiment": detect_sentiment(user_input),
        "complexity": assess_complexity(user_input),
        "success_indicators": detect_success_patterns(user_input, bot_response)
    }


def extract_topic(text: str) -> str:
    """Simple topic extraction"""
    topics = {
        'science': ['science', 'physics', 'chemistry', 'biology', 'research'],
        'technology': ['AI', 'computer', 'software', 'programming', 'tech'],
        'education': ['learn', 'study', 'school', 'education', 'knowledge'],
        'general': []
    }
    
    text_lower = text.lower()
    for topic, keywords in topics.items():
        if any(keyword in text_lower for keyword in keywords):
            return topic
    return 'general'


def detect_sentiment(text: str) -> str:
    """Simple sentiment detection"""
    positive_words = ['good', 'great', 'awesome', 'excellent', 'love', 'like', 'amazing']
    negative_words = ['bad', 'terrible', 'hate', 'dislike', 'awful', 'wrong']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    return 'neutral'


def assess_complexity(text: str) -> str:
    """Assess input complexity"""
    if len(text) < 30:
        return 'simple'
    elif len(text) > 100 or any(word in text.lower() for word in ['complex', 'detailed', 'comprehensive', 'analyze']):
        return 'complex'
    return 'medium'


def detect_success_patterns(user_input: str, bot_response: str) -> Dict[str, bool]:
    """Detect patterns that indicate successful interactions"""
    success_patterns = {
        "format_match": check_format_alignment(user_input, bot_response),
        "appropriate_length": check_length_appropriateness(user_input, bot_response),
        "topic_relevance": check_topic_relevance(user_input, bot_response)
    }
    return success_patterns


def check_format_alignment(user_input: str, bot_response: str) -> bool:
    """Check if response format matches user request"""
    user_lower = user_input.lower()
    
    # User asked for paragraph
    if any(word in user_lower for word in ['paragraph', 'write', 'describe']):
        has_structure = bool(re.search(r'\*\*.*\*\*', bot_response) or re.search(r'^[\s]*[-•*\d+\.]', bot_response, re.MULTILINE))
        return not has_structure  # Success if no structure when paragraph requested
    
    # User asked for structure
    elif any(word in user_lower for word in ['explain', 'list', 'break down', 'steps']):
        has_structure = bool(re.search(r'\*\*.*\*\*', bot_response) or re.search(r'^[\s]*[-•*\d+\.]', bot_response, re.MULTILINE))
        return has_structure  # Success if structured when structure requested
    
    return True  # Neutral case


def check_length_appropriateness(user_input: str, bot_response: str) -> bool:
    """Check if response length is appropriate for the request"""
    if len(user_input) < 20:  # Short question
        return len(bot_response) < 500  # Should get short response
    elif len(user_input) > 100:  # Detailed question
        return len(bot_response) > 200  # Should get detailed response
    return True


def check_topic_relevance(user_input: str, bot_response: str) -> bool:
    """Simple topic relevance check"""
    user_topics = set(re.findall(r'\b[a-zA-Z]{4,}\b', user_input.lower()))
    response_topics = set(re.findall(r'\b[a-zA-Z]{4,}\b', bot_response.lower()))
    
    if len(user_topics) > 0:
        relevance_score = len(user_topics.intersection(response_topics)) / len(user_topics)
        return relevance_score > 0.3  # At least 30% topic overlap
    return True


def analyze_user_preferences(interactions: List[Dict]) -> Dict[str, Any]:
    """Analyze user preferences from interaction history"""
    if not interactions:
        return {}
    
    preferences = {
        "preferred_format": "neutral",
        "preferred_length": "medium",
        "formality_level": "neutral",
        "topics_of_interest": [],
        "successful_patterns": []
    }
    
    # Analyze format preferences
    format_requests = [i["input_patterns"]["request_type"] for i in interactions if "input_patterns" in i]
    if format_requests:
        most_common_format = max(set(format_requests), key=format_requests.count)
        preferences["preferred_format"] = most_common_format
    
    # Analyze length preferences
    length_prefs = [i["input_patterns"]["length_preference"] for i in interactions if "input_patterns" in i]
    if length_prefs:
        preferences["preferred_length"] = max(set(length_prefs), key=length_prefs.count)
    
    # Analyze formality preferences
    formality_levels = [i["input_patterns"]["formality_level"] for i in interactions if "input_patterns" in i]
    if formality_levels:
        preferences["formality_level"] = max(set(formality_levels), key=formality_levels.count)
    
    # Extract topics of interest
    all_keywords = []
    for interaction in interactions:
        if "input_patterns" in interaction and "keywords" in interaction["input_patterns"]:
            all_keywords.extend(interaction["input_patterns"]["keywords"])
    
    if all_keywords:
        keyword_counts = Counter(all_keywords)
        preferences["topics_of_interest"] = [word for word, count in keyword_counts.most_common(10)]
    
    return preferences


def generate_improvement_suggestions(interaction: Dict, feedback_data: Dict) -> List[str]:
    """Generate specific improvement suggestions based on feedback"""
    suggestions = []
    feedback_type = feedback_data["feedback_type"]
    
    if feedback_type == "format_mismatch":
        input_patterns = interaction.get("input_patterns", {})
        request_type = input_patterns.get("request_type", "unknown")
        suggestions.append(f"User requested {request_type} format but got different format")
        suggestions.append("Improve format detection and matching")
    
    elif feedback_type == "too_long":
        response_length = len(interaction.get("bot_response", ""))
        suggestions.append(f"Response was {response_length} chars - user prefers shorter responses")
        suggestions.append("Reduce response length for this user")
    
    elif feedback_type == "too_short":
        response_length = len(interaction.get("bot_response", ""))
        suggestions.append(f"Response was {response_length} chars - user wants more detail")
        suggestions.append("Increase response depth for this user")
    
    elif feedback_type == "off_topic":
        suggestions.append("Improve topic relevance detection")
        suggestions.append("Better analyze user intent and stay focused")
    
    elif feedback_type == "thumbs_up":
        suggestions.append("This response format and style worked well")
        suggestions.append("Reinforce similar patterns for this user")
    
    elif feedback_type == "thumbs_down":
        suggestions.append("General dissatisfaction - analyze all aspects")
        suggestions.append("Review format, tone, and content relevance")
    
    return suggestions
