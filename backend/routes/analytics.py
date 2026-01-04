"""
Analytics Routes
Handles learning analytics and effectiveness metrics
"""
from fastapi import APIRouter
import services.db_service as db_service


router = APIRouter(tags=["analytics"])


def calculate_learning_effectiveness():
    """Calculate how well the AI is learning from feedback"""
    return db_service.calculate_learning_effectiveness()


@router.get("/learning-analytics")
def get_learning_analytics_endpoint():
    """Get analytics about the AI's learning progress"""
    analytics = db_service.get_learning_analytics()
    if "error" not in analytics:
        analytics["learning_effectiveness"] = calculate_learning_effectiveness()
    return analytics
