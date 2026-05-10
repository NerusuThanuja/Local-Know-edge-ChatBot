"""
Utility Functions
Helper functions for formatting, caching, and processing
"""
import hashlib
import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def hash_query(query: str) -> str:
    """
    Create hash of query for caching
    
    Args:
        query: Query string
        
    Returns:
        MD5 hash of query
    """
    return hashlib.md5(query.lower().encode()).hexdigest()


def format_timestamp(timestamp: datetime = None) -> str:
    """
    Format datetime to readable string
    
    Args:
        timestamp: datetime object (default: now)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class ResponseCache:
    """Simple response cache"""

    def __init__(self, max_size: int = 100):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of cached responses
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get(self, query: str) -> Dict[str, Any]:
        """
        Get cached response
        
        Args:
            query: Query string
            
        Returns:
            Cached response or None
        """
        key = hash_query(query)
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None

    def set(self, query: str, response: Dict[str, Any]) -> None:
        """
        Set cached response
        
        Args:
            query: Query string
            response: Response dictionary
        """
        key = hash_query(query)

        # Remove least accessed item if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            lru_key = min(self.access_count, key=self.access_count.get)
            del self.cache[lru_key]
            del self.access_count[lru_key]

        self.cache[key] = response
        self.access_count[key] = 0

    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.access_count.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": sum(self.access_count.values()),
        }


def format_response_for_ui(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format chatbot response for UI display
    
    Args:
        response: Response from chatbot.answer_query()
        
    Returns:
        Formatted response dictionary
    """
    if response["status"] != "success":
        return {
            "text": response.get(
                "answer", "I encountered an error processing your query."
            ),
            "confidence": 0,
            "alternatives": [],
            "is_error": True,
        }

    return {
        "text": response.get("answer", ""),
        "confidence": response.get("confidence", 0),
        "alternatives": [
            {
                "text": alt.get("answer", ""),
                "confidence": alt.get("confidence", 0),
            }
            for alt in response.get("alternatives", [])
        ],
        "is_error": False,
        "matched_question": response.get("matched_question", ""),
    }


def save_conversation(
    conversation: List[Dict[str, str]], save_path: str = "conversations.jsonl"
) -> None:
    """
    Save conversation to JSONL file
    
    Args:
        conversation: List of messages
        save_path: Path to save conversation
    """
    try:
        with open(save_path, "a", encoding="utf-8") as f:
            for message in conversation:
                json.dump(
                    {**message, "timestamp": format_timestamp()},
                    f,
                    ensure_ascii=False,
                )
                f.write("\n")
        logger.info(f"Conversation saved to {save_path}")
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")


def load_conversations(save_path: str = "conversations.jsonl") -> List[Dict]:
    """
    Load conversations from JSONL file
    
    Args:
        save_path: Path to load conversations from
        
    Returns:
        List of conversation messages
    """
    conversations = []
    if not Path(save_path).exists():
        return conversations

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line))
        logger.info(f"Loaded {len(conversations)} messages from {save_path}")
    except Exception as e:
        logger.error(f"Failed to load conversations: {e}")

    return conversations


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text (for HTML display)
    
    Args:
        text: Text to highlight
        keywords: List of keywords to highlight
        
    Returns:
        HTML string with highlighted keywords
    """
    highlighted = text
    for keyword in keywords:
        highlighted = highlighted.replace(
            keyword, f"<mark>{keyword}</mark>"
        )  # HTML mark tag for highlighting
    return highlighted


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test cache
    cache = ResponseCache(max_size=5)
    cache.set("test query", {"answer": "test answer"})
    cached = cache.get("test query")
    print(f"Cached response: {cached}")
    print(f"Cache stats: {cache.get_stats()}")
