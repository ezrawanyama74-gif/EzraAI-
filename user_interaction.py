"""
User Interaction and Learning Module
Handles user preferences and learns from interactions
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from database import db
from config import USER_PREFS_CONFIG

logger = logging.getLogger(__name__)


class UserInteractionManager:
    """Manages user interactions and learns from feedback"""
    
    def __init__(self):
        self.preferences = {}
        self.interaction_history = []
        self.load_preferences()
        self.learning_enabled = USER_PREFS_CONFIG["learning_enabled"]
        self.feedback_weight = USER_PREFS_CONFIG["feedback_weight"]
    
    def load_preferences(self):
        """Load user preferences from database"""
        try:
            # Set default preferences if not exists
            default_prefs = {
                "name": "User",
                "language": "english",
                "response_style": "formal",
                "timezone": "UTC",
                "favorite_topics": [],
                "learning_mode": True,
            }
            
            for key, default_value in default_prefs.items():
                value = db.get_preference(key)
                self.preferences[key] = value if value is not None else default_value
            
            logger.info("User preferences loaded successfully")
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
    
    def save_preference(self, key: str, value: Any) -> bool:
        """Save user preference"""
        try:
            self.preferences[key] = value
            db.save_preference(key, value)
            logger.info(f"Preference '{key}' saved: {value}")
            return True
        except Exception as e:
            logger.error(f"Error saving preference '{key}': {e}")
            return False
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.preferences.get(key, default)
    
    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update multiple preferences"""
        try:
            for key, value in preferences.items():
                self.save_preference(key, value)
            logger.info(f"Updated {len(preferences)} preferences")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    def log_interaction(self, user_input: str, ai_response: str,
                       interaction_type: str = "general") -> int:
        """Log user-AI interaction"""
        try:
            db.save_interaction(user_input, ai_response, interaction_type)
            
            self.interaction_history.append({
                "user_input": user_input,
                "ai_response": ai_response,
                "type": interaction_type,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only recent interactions in memory
            if len(self.interaction_history) > USER_PREFS_CONFIG["max_history"]:
                self.interaction_history.pop(0)
            
            logger.info(f"Interaction logged: {interaction_type}")
            return len(self.interaction_history)
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
            return -1
    
    def provide_feedback(self, interaction_id: int, feedback_score: float,
                        comments: str = "") -> bool:
        """
        Provide feedback for an interaction
        feedback_score: 0.0 (poor) to 1.0 (excellent)
        """
        try:
            if not 0.0 <= feedback_score <= 1.0:
                logger.warning(f"Invalid feedback score: {feedback_score}")
                return False
            
            db.save_feedback(interaction_id, feedback_score)
            
            if comments:
                logger.info(f"Feedback with comments: {comments}")
            
            logger.info(f"Feedback saved for interaction {interaction_id}: {feedback_score}")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False
    
    def get_interaction_history(self, limit: int = 50) -> List[Dict]:
        """Get interaction history"""
        try:
            interactions = db.get_interactions(limit=limit)
            return interactions
        except Exception as e:
            logger.error(f"Error retrieving interaction history: {e}")
            return []
    
    def get_high_feedback_interactions(self, threshold: float = 0.7,
                                      limit: int = 100) -> List[Dict]:
        """Get interactions with high user feedback for training"""
        try:
            interactions = db.get_interactions(limit=limit, min_feedback=threshold)
            logger.info(f"Retrieved {len(interactions)} high-feedback interactions")
            return interactions
        except Exception as e:
            logger.error(f"Error retrieving high-feedback interactions: {e}")
            return []
    
    def analyze_preferences(self) -> Dict[str, Any]:
        """Analyze user preferences and interaction patterns"""
        try:
            interactions = self.get_interaction_history(limit=200)
            
            if not interactions:
                return {}
            
            # Count interaction types
            type_counts = {}
            for interaction in interactions:
                itype = interaction.get("type", "general")
                type_counts[itype] = type_counts.get(itype, 0) + 1
            
            # Calculate average feedback
            feedbacks = [i.get("feedback", 0) for i in interactions if i.get("feedback")]
            avg_feedback = sum(feedbacks) / len(feedbacks) if feedbacks else 0
            
            analysis = {
                "total_interactions": len(interactions),
                "interaction_types": type_counts,
                "average_feedback": avg_feedback,
                "top_interaction_type": max(type_counts, key=type_counts.get) if type_counts else None,
            }
            
            logger.info(f"User analysis: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing preferences: {e}")
            return {}
    
    def add_favorite_topic(self, topic: str) -> bool:
        """Add topic to user's favorite topics"""
        try:
            favorites = self.get_preference("favorite_topics", [])
            if topic not in favorites:
                favorites.append(topic)
                self.save_preference("favorite_topics", favorites)
                logger.info(f"Added favorite topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Error adding favorite topic: {e}")
            return False
    
    def get_favorite_topics(self) -> List[str]:
        """Get user's favorite topics"""
        return self.get_preference("favorite_topics", [])
    
    def set_response_style(self, style: str) -> bool:
        """
        Set AI response style
        Options: formal, casual, technical, creative, etc.
        """
        valid_styles = ["formal", "casual", "technical", "creative", "concise"]
        if style in valid_styles:
            self.save_preference("response_style", style)
            logger.info(f"Response style set to: {style}")
            return True
        logger.warning(f"Invalid response style: {style}")
        return False
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about AI learning from user interactions"""
        try:
            interactions = self.get_interaction_history(limit=500)
            
            if not interactions:
                return {"message": "Not enough data for insights"}
            
            # Calculate metrics
            total = len(interactions)
            with_feedback = sum(1 for i in interactions if i.get("feedback"))
            avg_feedback = sum(i.get("feedback", 0) for i in interactions) / total if total > 0 else 0
            
            high_quality = sum(1 for i in interactions if i.get("feedback", 0) >= 0.7)
            
            insights = {
                "total_interactions": total,
                "feedback_provided": with_feedback,
                "feedback_percentage": (with_feedback / total * 100) if total > 0 else 0,
                "average_satisfaction": avg_feedback,
                "high_quality_responses": high_quality,
                "improvement_needed": total - high_quality,
                "learning_enabled": self.learning_enabled,
            }
            
            logger.info(f"Learning insights: {insights}")
            return insights
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {}
    
    def export_preferences(self) -> str:
        """Export preferences as JSON"""
        try:
            return json.dumps(self.preferences, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error exporting preferences: {e}")
            return ""
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        return self.preferences.copy()


# Global interaction manager instance
interaction_manager = UserInteractionManager()
