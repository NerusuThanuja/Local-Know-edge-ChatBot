"""
Advanced Features Module (Optional Enhancements)
Can be integrated into main app.py as needed
"""
import streamlit as st
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# Feature 1: Voice Input (requires streamlit-mic-recorder)
def add_voice_input():
    """
    Add voice input feature (requires: pip install streamlit-mic-recorder)
    
    Usage:
        if st.checkbox("Enable voice input"):
            audio_bytes = audio_recorder()
            if audio_bytes:
                # Process audio...
    """
    try:
        from streamlit_mic_recorder import audio_recorder
        return audio_recorder
    except ImportError:
        logger.warning("streamlit-mic-recorder not installed. Voice input disabled.")
        st.info("To enable voice input, run: `pip install streamlit-mic-recorder`")
        return None


# Feature 2: Response Analytics
class ResponseAnalytics:
    """Track and analyze chatbot responses"""

    def __init__(self):
        self.responses = []
        self.queries = []

    def log_response(self, query: str, response: Dict[str, Any]):
        """Log query and response for analytics"""
        self.queries.append({
            "query": query,
            "timestamp": datetime.now(),
            "length": len(query)
        })
        self.responses.append({
            "status": response.get("status"),
            "confidence": response.get("confidence", 0),
            "num_alternatives": len(response.get("alternatives", [])),
            "timestamp": datetime.now()
        })

    def get_stats(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        if not self.responses:
            return {}

        confidences = [r["confidence"] for r in self.responses if r.get("confidence")]
        
        return {
            "total_queries": len(self.queries),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "success_rate": sum(1 for r in self.responses if r["status"] == "success") / len(self.responses),
            "avg_query_length": sum(q["length"] for q in self.queries) / len(self.queries) if self.queries else 0,
        }

    def display_stats(self):
        """Display analytics in Streamlit"""
        stats = self.get_stats()
        if not stats:
            st.info("No analytics data yet")
            return

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", stats.get("total_queries", 0))
        with col2:
            st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.1%}")
        with col3:
            st.metric("Success Rate", f"{stats.get('success_rate', 0):.1%}")
        with col4:
            st.metric("Avg Query Length", f"{stats.get('avg_query_length', 0):.0f} chars")


# Feature 3: Search Highlighting
def highlight_answer(answer: str, query: str) -> str:
    """
    Highlight query keywords in answer
    
    Args:
        answer: The answer text
        query: The query text
        
    Returns:
        HTML string with highlighted keywords
    """
    keywords = query.lower().split()
    highlighted = answer

    for keyword in keywords:
        if len(keyword) > 3:  # Only highlight words longer than 3 chars
            # Find and highlight (case-insensitive)
            import re
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(
                lambda m: f"<mark>{m.group()}</mark>",
                highlighted
            )

    return highlighted


# Feature 4: Conversation Export
def export_conversation(messages: list, format: str = "txt") -> str:
    """
    Export conversation to file
    
    Args:
        messages: List of message dictionaries
        format: Export format ('txt', 'md', 'csv', 'json')
        
    Returns:
        Export file content
    """
    if format == "txt":
        content = "CONVERSATION TRANSCRIPT\n"
        content += "=" * 50 + "\n\n"
        for msg in messages:
            role = "USER" if msg["role"] == "user" else "BOT"
            content += f"{role}:\n{msg['content']}\n\n"
        return content

    elif format == "md":
        content = "# Conversation Transcript\n\n"
        for msg in messages:
            if msg["role"] == "user":
                content += f"> **User:** {msg['content']}\n\n"
            else:
                content += f"**Bot:** {msg['content']}\n\n"
        return content

    elif format == "json":
        import json
        return json.dumps(messages, indent=2)

    elif format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Role", "Message", "Timestamp"])
        for msg in messages:
            writer.writerow([
                msg.get("role", "").upper(),
                msg.get("content", ""),
                msg.get("timestamp", "")
            ])
        return output.getvalue()


# Feature 5: Custom Response Formatting
def create_response_card(answer: str, confidence: float, alternatives: list = None):
    """
    Create a nice card display for response
    
    Args:
        answer: Main answer text
        confidence: Confidence score (0-1)
        alternatives: List of alternative answers
    """
    # Confidence color coding
    if confidence > 0.8:
        conf_color = "🟢"
        conf_text = "High Confidence"
    elif confidence > 0.5:
        conf_color = "🟡"
        conf_text = "Medium Confidence"
    else:
        conf_color = "🔴"
        conf_text = "Low Confidence"

    # Display main answer
    st.markdown(f"""
    <div style='background: rgba(102, 126, 234, 0.1); 
                padding: 16px; 
                border-radius: 10px;
                border-left: 4px solid #667eea;'>
        <h4>📌 Answer</h4>
        <p>{answer}</p>
        <p style='font-size: 12px; color: #999;'>
            {conf_color} {conf_text} ({confidence:.0%})
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display alternatives if available
    if alternatives:
        st.markdown("### 🔗 Related Information")
        for i, alt in enumerate(alternatives, 1):
            with st.expander(f"Alternative {i} ({alt.get('confidence', 0):.0%} confidence)"):
                st.write(alt.get("answer", ""))


# Feature 6: Query Suggestions (Smart Suggestions)
def get_query_suggestions(chatbot, recent_queries: list = None) -> list:
    """
    Generate query suggestions based on knowledge base
    
    Args:
        chatbot: Chatbot instance
        recent_queries: List of recent queries
        
    Returns:
        List of suggested queries
    """
    suggestions = [
        "What is the admission process?",
        "How much are the fees?",
        "What are the eligibility requirements?",
        "When is the application deadline?",
        "Do you offer scholarships?",
        "What is the student-to-teacher ratio?",
        "Tell me about the campus facilities",
        "What are the popular programs?",
    ]

    # Return random subset
    import random
    return random.sample(suggestions, min(4, len(suggestions)))


# Feature 7: Theme Customization
THEMES = {
    "dark": {
        "primary_color": "#667eea",
        "secondary_color": "#764ba2",
        "background": "linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%)",
        "text_color": "#f0f0f0",
    },
    "light": {
        "primary_color": "#5568d3",
        "secondary_color": "#6b47b5",
        "background": "linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)",
        "text_color": "#1a1a1a",
    },
    "ocean": {
        "primary_color": "#0ea5e9",
        "secondary_color": "#06b6d4",
        "background": "linear-gradient(135deg, #0f172a 0%, #164e63 100%)",
        "text_color": "#e0f2fe",
    }
}


# Feature 8: Feedback System
class FeedbackSystem:
    """Collect user feedback on responses"""

    def __init__(self):
        self.feedback_data = []

    def collect_feedback(self, response_id: str, rating: int, comment: str = ""):
        """
        Collect feedback for a response
        
        Args:
            response_id: ID of the response
            rating: Rating (1-5)
            comment: Optional comment
        """
        self.feedback_data.append({
            "response_id": response_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now()
        })
        logger.info(f"Feedback collected: {rating}/5 - {comment}")

    def display_feedback_widget(self, response_id: str):
        """Display feedback widget in Streamlit"""
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            rating = st.slider("Rate this response", 1, 5, key=f"rating_{response_id}")

        with col2:
            if st.button("👍 Helpful", key=f"helpful_{response_id}"):
                self.collect_feedback(response_id, 5)
                st.success("Thanks for your feedback!")

        with col3:
            if st.button("👎 Not Helpful", key=f"not_helpful_{response_id}"):
                self.collect_feedback(response_id, 1)
                st.info("We'll improve!")


# Feature 9: Multi-Language Support (Placeholder)
def set_language(lang_code: str = "en"):
    """
    Set language for UI
    
    Args:
        lang_code: Language code (en, es, fr, etc.)
    """
    translations = {
        "en": {
            "title": "University Chatbot",
            "placeholder": "Ask about admissions...",
            "send": "Send",
        },
        "es": {
            "title": "Chatbot Universitario",
            "placeholder": "Pregunta sobre admisiones...",
            "send": "Enviar",
        },
        "fr": {
            "title": "Chatbot Universitaire",
            "placeholder": "Posez des questions sur les admissions...",
            "send": "Envoyer",
        },
    }
    return translations.get(lang_code, translations["en"])


# Feature 10: Performance Monitoring
class PerformanceMonitor:
    """Monitor chatbot performance"""

    def __init__(self):
        self.timings = []
        self.error_count = 0
        self.success_count = 0

    def log_query_time(self, query_time: float):
        """Log query processing time"""
        self.timings.append(query_time)

    def log_error(self):
        """Log an error"""
        self.error_count += 1

    def log_success(self):
        """Log a successful query"""
        self.success_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.timings:
            return {}

        import statistics
        return {
            "avg_response_time": statistics.mean(self.timings),
            "median_response_time": statistics.median(self.timings),
            "error_count": self.error_count,
            "success_count": self.success_count,
            "error_rate": self.error_count / (self.error_count + self.success_count) if (self.error_count + self.success_count) > 0 else 0,
        }

    def display_metrics(self):
        """Display metrics in Streamlit"""
        metrics = self.get_metrics()
        if not metrics:
            return

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Response Time", f"{metrics.get('avg_response_time', 0):.2f}s")
        with col2:
            st.metric("Success Count", metrics.get("success_count", 0))
        with col3:
            st.metric("Error Rate", f"{metrics.get('error_rate', 0):.1%}")


if __name__ == "__main__":
    # Demo: Show how to use these features
    print("Advanced Features Module")
    print("=" * 50)
    print("Available features:")
    print("1. Voice Input (requires streamlit-mic-recorder)")
    print("2. Response Analytics")
    print("3. Search Highlighting")
    print("4. Conversation Export")
    print("5. Custom Response Cards")
    print("6. Query Suggestions")
    print("7. Theme Customization")
    print("8. Feedback System")
    print("9. Multi-Language Support")
    print("10. Performance Monitoring")
    print("\nImport and use in app.py as needed")
