"""
Database Module for Ezrex.AI
SQLite database for storing interactions, preferences, and feedback
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = DATABASE_CONFIG["path"]
        self.connection = None
        self.init_database()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=DATABASE_CONFIG["timeout"],
                check_same_thread=DATABASE_CONFIG["check_same_thread"]
            )
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")
        except sqlite3.Error as e:
            logger.error(f"Error closing database: {e}")
    
    def init_database(self):
        """Initialize database with required tables"""
        self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    interaction_type TEXT DEFAULT 'general',
                    feedback REAL,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interaction_type ON interactions(interaction_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interaction_date ON interactions(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback ON interactions(feedback)')
            
            self.connection.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
    
    # Preference management
    def save_preference(self, key: str, value: Any) -> bool:
        """Save or update user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, str(value)))
            self.connection.commit()
            logger.info(f"Preference saved: {key} = {value}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving preference: {e}")
            return False
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Error getting preference: {e}")
            return None
    
    def get_all_preferences(self) -> Dict[str, str]:
        """Get all user preferences"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT key, value FROM user_preferences')
            return {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.error(f"Error getting preferences: {e}")
            return {}
    
    # Interaction management
    def save_interaction(self, user_input: str, ai_response: str,
                        interaction_type: str = "general") -> int:
        """Save user-AI interaction"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO interactions (user_input, ai_response, interaction_type)
                VALUES (?, ?, ?)
            ''', (user_input, ai_response, interaction_type))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error saving interaction: {e}")
            return -1
    
    def get_interactions(self, limit: int = 50, min_feedback: float = None) -> List[Dict]:
        """Get interactions with optional feedback filter"""
        try:
            cursor = self.connection.cursor()
            
            if min_feedback is not None:
                cursor.execute('''
                    SELECT * FROM interactions
                    WHERE feedback >= ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (min_feedback, limit))
            else:
                cursor.execute('''
                    SELECT * FROM interactions
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting interactions: {e}")
            return []
    
    def get_interaction_by_id(self, interaction_id: int) -> Optional[Dict]:
        """Get specific interaction by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM interactions WHERE id = ?', (interaction_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.error(f"Error getting interaction: {e}")
            return None
    
    # Feedback management
    def save_feedback(self, interaction_id: int, feedback_score: float,
                     comments: str = "") -> bool:
        """Save feedback for an interaction"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE interactions
                SET feedback = ?, comments = ?
                WHERE id = ?
            ''', (feedback_score, comments, interaction_id))
            self.connection.commit()
            logger.info(f"Feedback saved for interaction {interaction_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving feedback: {e}")
            return False
    
    # User data management
    def save_user_data(self, data_type: str, content: str, metadata: str = "") -> int:
        """Save user data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO user_data (data_type, content, metadata)
                VALUES (?, ?, ?)
            ''', (data_type, content, metadata))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error saving user data: {e}")
            return -1
    
    def get_user_data(self, data_type: str, limit: int = 50) -> List[Dict]:
        """Get user data by type"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM user_data
                WHERE data_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (data_type, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting user data: {e}")
            return []
    
    # Learning metrics
    def save_metric(self, metric_name: str, metric_value: float) -> bool:
        """Save learning metric"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO learning_metrics (metric_name, metric_value)
                VALUES (?, ?)
            ''', (metric_name, metric_value))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving metric: {e}")
            return False
    
    def get_metrics(self, metric_name: str = None, limit: int = 100) -> List[Dict]:
        """Get learning metrics"""
        try:
            cursor = self.connection.cursor()
            
            if metric_name:
                cursor.execute('''
                    SELECT * FROM learning_metrics
                    WHERE metric_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (metric_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM learning_metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Total interactions
            cursor.execute('SELECT COUNT(*) FROM interactions')
            total_interactions = cursor.fetchone()[0]
            
            # Average feedback
            cursor.execute('SELECT AVG(feedback) FROM interactions WHERE feedback IS NOT NULL')
            avg_feedback = cursor.fetchone()[0] or 0
            
            # Interactions by type
            cursor.execute('''
                SELECT interaction_type, COUNT(*) as count
                FROM interactions
                GROUP BY interaction_type
            ''')
            interactions_by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_interactions': total_interactions,
                'average_feedback': round(avg_feedback, 2),
                'interactions_by_type': interactions_by_type
            }
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Global database instance
db = Database()
