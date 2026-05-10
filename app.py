"""
Streamlit Chatbot UI
Production-ready chatbot interface with glassmorphic design
"""
import streamlit as st
import logging
from typing import List, Dict
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.chatbot import Chatbot, initialize_chatbot
from src.utils import ResponseCache, format_response_for_ui
from src.config import CHAT_MAX_HISTORY, DEFAULT_THEME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="University Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Session state initialization
def initialize_session_state():
    """Initialize Streamlit session state"""
    if "chatbot" not in st.session_state:
        with st.spinner("🔄 Initializing chatbot..."):
            st.session_state.chatbot = initialize_chatbot()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "response_cache" not in st.session_state:
        st.session_state.response_cache = ResponseCache()

    if "theme" not in st.session_state:
        st.session_state.theme = DEFAULT_THEME

    if "show_alternatives" not in st.session_state:
        st.session_state.show_alternatives = True

    if "show_confidence" not in st.session_state:
        st.session_state.show_confidence = True

    if "auto_scroll" not in st.session_state:
        st.session_state.auto_scroll = True


# Sidebar
def render_sidebar():
    """Render sidebar with controls"""
    st.sidebar.markdown("## 🎓 University Chatbot")

    # Theme toggle
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    with col2:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()

    st.sidebar.divider()

    # Settings
    st.sidebar.markdown("### ⚙️ Settings")
    st.session_state.show_alternatives = st.sidebar.checkbox(
        "Show alternative answers", value=True
    )
    st.session_state.show_confidence = st.sidebar.checkbox(
        "Show confidence scores", value=True
    )
    st.session_state.auto_scroll = st.sidebar.checkbox("Auto-scroll", value=True)

    st.sidebar.divider()

    # Chat history
    st.sidebar.markdown("### 📋 Chat History")

    if st.session_state.messages:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.markdown(f"**{len(st.session_state.messages)} messages**")
        with col2:
            if st.button("🗑️", help="Clear chat", key="clear_btn"):
                st.session_state.messages = []
                st.session_state.response_cache.clear()
                st.rerun()

        # Show recent messages
        st.markdown("**Recent queries:**")
        for i, msg in enumerate(st.session_state.messages[-5:]):
            if msg["role"] == "user":
                query = msg["content"][:50]
                if len(msg["content"]) > 50:
                    query += "..."
                if st.button(f"↪️ {query}", key=f"history_{i}", use_container_width=True):
                    st.session_state.input_query = msg["content"]
                    st.rerun()
    else:
        st.sidebar.info("💬 No messages yet. Start a conversation!")

    st.sidebar.divider()

    # Chatbot status
    st.sidebar.markdown("### 📊 Status")
    if st.session_state.chatbot.is_ready:
        st.sidebar.success("✅ Chatbot Ready")
        status = st.session_state.chatbot.get_status()
        st.sidebar.metric("Corpus Size", f"{status['corpus_size']} Q&As")
    else:
        st.sidebar.error("❌ Chatbot Error")
        st.sidebar.warning(
            "Failed to initialize chatbot. Please check your setup."
        )


# Main chat interface
def render_chat_interface():
    """Render main chat interface"""
    st.markdown("## 🎯 Ask Me Anything")

    # Chat messages container
    messages_container = st.container()

    with messages_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown(
                """
                <div style='text-align: center; padding: 40px 20px;'>
                    <h2 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              -webkit-background-clip: text;
                              -webkit-text-fill-color: transparent;
                              background-clip: text;'>
                        Welcome to University Chatbot! 🎓
                    </h2>
                    <p style='color: #b0b0b0; font-size: 16px;'>
                        Ask me anything about university admissions, fees, programs, or general information.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Display messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("assistant", avatar="🎓"):
                        st.markdown(message["content"])

    # Input area
    st.markdown("<br>" * 3, unsafe_allow_html=True)

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([20, 1])

        with col1:
            user_input = st.text_input(
                "Your question",
                placeholder="Ask about admissions, fees, programs...",
                label_visibility="collapsed",
            )

        with col2:
            send_button = st.form_submit_button("📤", use_container_width=True)

        if send_button and user_input.strip():
            handle_user_input(user_input)


def handle_user_input(user_input: str):
    """
    Handle user input and generate response
    
    Args:
        user_input: User's question
    """
    # Add user message to history
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Try to get cached response
    cached_response = st.session_state.response_cache.get(user_input)

    if cached_response:
        bot_response = cached_response
        logger.info("Using cached response")
    else:
        # Get response from chatbot
        if not st.session_state.chatbot.is_ready:
            bot_response = "❌ Chatbot is not ready. Please refresh the page."
        else:
            try:
                raw_response = st.session_state.chatbot.answer_query(
                    user_input
                )
                st.session_state.response_cache.set(user_input, raw_response)
                bot_response = format_bot_response(raw_response)
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                bot_response = f"❌ Error: {str(e)}"

    # Add bot response to history
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_response}
    )

    # Limit history
    if len(st.session_state.messages) > CHAT_MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-CHAT_MAX_HISTORY :]

    st.rerun()


def format_bot_response(response: Dict) -> str:
    """
    Format bot response for display
    
    Args:
        response: Response dictionary from chatbot
        
    Returns:
        Formatted markdown string
    """
    if response["status"] != "success":
        return response.get("answer", "Unable to process query")

    answer = response.get("answer", "")
    confidence = response.get("confidence", 0)
    alternatives = response.get("alternatives", [])

    # Build markdown response
    formatted = f"**Answer:** {answer}\n\n"

    if st.session_state.show_confidence:
        confidence_pct = f"{confidence * 100:.0f}%"
        if confidence > 0.8:
            formatted += f"✅ **Confidence:** {confidence_pct}\n\n"
        elif confidence > 0.5:
            formatted += f"⚠️ **Confidence:** {confidence_pct}\n\n"
        else:
            formatted += f"❓ **Confidence:** {confidence_pct}\n\n"

    if st.session_state.show_alternatives and alternatives:
        formatted += "**Related Answers:**\n"
        for i, alt in enumerate(alternatives, 1):
            alt_text = alt["answer"][:100]
            if len(alt["answer"]) > 100:
                alt_text += "..."
            alt_confidence = f"{alt['confidence'] * 100:.0f}%"
            formatted += f"\n{i}. {alt_text}\n   *(Confidence: {alt_confidence})*"

    return formatted


# Main app
def main():
    """Main application"""
    initialize_session_state()

    # Check chatbot status
    if not st.session_state.chatbot.is_ready:
        st.error(
            "❌ Failed to initialize chatbot. Please check:\n"
            "1. All dependencies are installed\n"
            "2. The dataset exists or will be downloaded\n"
            "3. Check the logs for more details"
        )
        return

    # Render layout
    render_sidebar()
    render_chat_interface()


if __name__ == "__main__":
    main()
