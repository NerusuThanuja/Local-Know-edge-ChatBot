"""
Embedder Module
Generates embeddings using sentence-transformers
"""
import numpy as np
import logging
from typing import List, Tuple
from pathlib import Path
from tqdm import tqdm

# Import sentence-transformers lazily to avoid loading on import
logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings using sentence-transformers"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedder with specified model
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        self._load_model()

    def _load_model(self):
        """Lazy load sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            # Get embedding dimension
            dummy_embedding = self.model.encode(["test"])
            self.embedding_dim = dummy_embedding.shape[1]
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Could not load embedding model: {e}")

    def embed_texts(
        self, texts: List[str], batch_size: int = 32, show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for embedding
            show_progress: Show progress bar
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)

        logger.info(f"Generating embeddings for {len(texts)} texts")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0]

    @staticmethod
    def save_embeddings(embeddings: np.ndarray, save_path: str) -> None:
        """
        Save embeddings to numpy file
        
        Args:
            embeddings: numpy array of embeddings
            save_path: Path to save embeddings
        """
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        np.save(save_path, embeddings)
        logger.info(f"Embeddings saved to {save_path}")

    @staticmethod
    def load_embeddings(save_path: str) -> np.ndarray:
        """
        Load embeddings from numpy file
        
        Args:
            save_path: Path to load embeddings from
            
        Returns:
            numpy array of embeddings
        """
        if not Path(save_path).exists():
            raise FileNotFoundError(f"Embeddings file not found: {save_path}")

        embeddings = np.load(save_path)
        logger.info(f"Loaded embeddings with shape: {embeddings.shape}")
        return embeddings


def prepare_embeddings(
    questions: List[str], save_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> np.ndarray:
    """
    Main function to prepare embeddings
    
    Args:
        questions: List of questions to embed
        save_path: Path to save embeddings
        model_name: Model to use for embedding
        
    Returns:
        numpy array of embeddings
    """
    embedder = Embedder(model_name=model_name)
    embeddings = embedder.embed_texts(questions, show_progress=True)
    embedder.save_embeddings(embeddings, save_path)
    return embeddings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from src.data_loader import DataLoader
    from src.config import EMBEDDINGS_FILE

    loader = DataLoader()
    questions, _ = loader.load_and_prepare()
    prepare_embeddings(questions, str(EMBEDDINGS_FILE))
