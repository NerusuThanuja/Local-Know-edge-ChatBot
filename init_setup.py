"""
Initialization Script
Run this on first setup to prepare the chatbot
"""
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required packages are installed"""
    logger.info("Checking dependencies...")
    
    required = [
        "streamlit",
        "sentence_transformers",
        "faiss",
        "numpy",
        "pandas",
        "torch",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            logger.info(f"✓ {package}")
        except ImportError:
            missing.append(package)
            logger.error(f"✗ {package} not found")
    
    if missing:
        logger.error(f"Missing packages: {missing}")
        logger.info("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("✓ All dependencies installed")
    return True


def check_directories():
    """Ensure all required directories exist"""
    logger.info("Checking directories...")
    
    dirs = [
        Path("data"),
        Path("embeddings"),
        Path("assets"),
        Path("src"),
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)
        logger.info(f"✓ {dir_path}")
    
    logger.info("✓ All directories ready")
    return True


def prepare_embeddings():
    """Prepare embeddings and FAISS index"""
    logger.info("Preparing embeddings and FAISS index...")
    
    from src.data_loader import DataLoader
    from src.embedder import Embedder
    from src.retriever import FAISSRetriever
    from src.config import EMBEDDINGS_FILE, FAISS_INDEX_FILE, CORPUS_PICKLE
    
    # Check if already prepared
    if EMBEDDINGS_FILE.exists() and FAISS_INDEX_FILE.exists():
        logger.info("✓ Embeddings already prepared")
        return True
    
    try:
        # Load data
        logger.info("Loading dataset...")
        loader = DataLoader()
        questions, corpus = loader.load_and_prepare()
        loader.save_corpus()
        logger.info(f"✓ Loaded {len(corpus)} Q&A pairs")
        
        # Generate embeddings
        logger.info("Generating embeddings (this may take 5-15 minutes)...")
        embedder = Embedder()
        embeddings = embedder.embed_texts(questions, show_progress=True)
        embedder.save_embeddings(embeddings, str(EMBEDDINGS_FILE))
        logger.info("✓ Embeddings generated")
        
        # Build FAISS index
        logger.info("Building FAISS index...")
        retriever = FAISSRetriever(embeddings, questions)
        retriever.save_index(str(FAISS_INDEX_FILE))
        logger.info("✓ FAISS index built")
        
        return True
    except Exception as e:
        logger.error(f"Failed to prepare embeddings: {e}")
        return False


def test_chatbot():
    """Test chatbot with sample queries"""
    logger.info("Testing chatbot...")
    
    from src.chatbot import Chatbot
    
    try:
        chatbot = Chatbot()
        
        if not chatbot.is_ready:
            logger.error("Chatbot not ready")
            return False
        
        test_queries = [
            "Hello",
            "What is admission?",
            "How to apply?",
        ]
        
        for query in test_queries:
            response = chatbot.answer_query(query)
            if response.get("status") == "success":
                logger.info(f"✓ Query: '{query}' → Got response")
            else:
                logger.warning(f"⚠ Query: '{query}' → {response.get('status')}")
        
        logger.info("✓ Chatbot working")
        return True
    except Exception as e:
        logger.error(f"Chatbot test failed: {e}")
        return False


def main():
    """Run full initialization"""
    logger.info("=" * 60)
    logger.info("University Chatbot - Initialization")
    logger.info("=" * 60)
    
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Creating directories", check_directories),
        ("Preparing embeddings", prepare_embeddings),
        ("Testing chatbot", test_chatbot),
    ]
    
    results = []
    for step_name, step_func in steps:
        logger.info(f"\n{step_name}...")
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            logger.error(f"{step_name} failed: {e}")
            results.append((step_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Initialization Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for step_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {step_name}")
        if not result:
            all_passed = False
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("✅ Setup complete! Run: streamlit run app.py")
    else:
        logger.error("❌ Setup failed. Check errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
