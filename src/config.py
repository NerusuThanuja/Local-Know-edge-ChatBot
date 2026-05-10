"""
Configuration file for the RAG Chatbot
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
EMBEDDINGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# File paths
CORPUS_PICKLE = EMBEDDINGS_DIR / "metadata.pkl"
EMBEDDINGS_FILE = EMBEDDINGS_DIR / "corpus_embeddings.npy"
FAISS_INDEX_FILE = EMBEDDINGS_DIR / "faiss_index.index"
KAGGLE_DATASET_PATH = DATA_DIR / "university_dataset.csv"

# Model configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 32

# Retrieval configuration
TOP_K = 5
SIMILARITY_THRESHOLD = 0.3

# Kaggle dataset (you need to download manually or via API)
KAGGLE_DATASET_NAME = "tusharpaul2001/university-chatbot-dataset"

# UI Configuration
CHAT_MAX_HISTORY = 50
DEFAULT_THEME = "dark"

# Logging
LOG_LEVEL = "INFO"
