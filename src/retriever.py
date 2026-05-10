"""
Retriever Module
FAISS-based semantic search
"""
import numpy as np
import logging
from typing import List, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class FAISSRetriever:
    """FAISS-based semantic search retriever"""

    def __init__(self, embeddings: np.ndarray, questions: List[str]):
        """
        Initialize FAISS retriever
        
        Args:
            embeddings: numpy array of shape (num_questions, embedding_dim)
            questions: list of question texts
        """
        self.embeddings = embeddings
        self.questions = questions
        self.index = None
        self.dimension = embeddings.shape[1]

        if len(embeddings) != len(questions):
            raise ValueError(
                f"Embeddings ({len(embeddings)}) and questions ({len(questions)}) count mismatch"
            )

        self._build_index()

    def _build_index(self):
        """Build FAISS index"""
        try:
            import faiss

            logger.info(f"Building FAISS index for {len(self.embeddings)} embeddings")

            # Ensure embeddings are float32 (FAISS requirement)
            embeddings_fp32 = self.embeddings.astype(np.float32)

            # Create index (L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)

            # Add vectors to index
            self.index.add(embeddings_fp32)

            logger.info(f"FAISS index built with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            raise RuntimeError(f"Could not build FAISS index: {e}")

    def retrieve_top_k(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> Tuple[List[str], List[float]]:
        """
        Retrieve top-k most similar questions
        
        Args:
            query_embedding: embedding of query (shape: (embedding_dim,))
            k: number of results to retrieve
            
        Returns:
            Tuple of (questions_list, distances_list)
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")

        # Reshape query embedding
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)

        # Search
        distances, indices = self.index.search(query_embedding, min(k, len(self.questions)))

        # Convert L2 distances to confidence scores (inverse normalization)
        # Confidence = 1 / (1 + distance)
        confidences = [1.0 / (1.0 + float(d)) for d in distances[0]]

        # Get questions
        retrieved_questions = [self.questions[int(idx)] for idx in indices[0]]

        return retrieved_questions, confidences

    def save_index(self, save_path: str) -> None:
        """
        Save FAISS index to disk
        
        Args:
            save_path: Path to save index
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")

        try:
            import faiss

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, save_path)
            logger.info(f"FAISS index saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise

    @staticmethod
    def load_index(save_path: str, questions: List[str]) -> "FAISSRetriever":
        """
        Load FAISS index from disk
        
        Args:
            save_path: Path to load index from
            questions: list of question texts
            
        Returns:
            FAISSRetriever instance
        """
        if not Path(save_path).exists():
            raise FileNotFoundError(f"Index file not found: {save_path}")

        try:
            import faiss

            logger.info(f"Loading FAISS index from {save_path}")
            index = faiss.read_index(save_path)

            retriever = FAISSRetriever.__new__(FAISSRetriever)
            retriever.index = index
            retriever.questions = questions
            retriever.dimension = index.d
            retriever.embeddings = None  # Not needed for inference

            logger.info(f"FAISS index loaded with {index.ntotal} vectors")
            return retriever
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise RuntimeError(f"Could not load FAISS index: {e}")


def prepare_retriever(
    embeddings: np.ndarray,
    questions: List[str],
    index_save_path: str,
) -> FAISSRetriever:
    """
    Main function to prepare FAISS retriever
    
    Args:
        embeddings: numpy array of embeddings
        questions: list of questions
        index_save_path: path to save index
        
    Returns:
        FAISSRetriever instance
    """
    retriever = FAISSRetriever(embeddings, questions)
    retriever.save_index(index_save_path)
    return retriever


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from src.data_loader import DataLoader
    from src.embedder import Embedder
    from src.config import EMBEDDINGS_FILE, FAISS_INDEX_FILE

    # Load data
    loader = DataLoader()
    questions, _ = loader.load_and_prepare()

    # Load embeddings (assume already generated)
    try:
        embeddings = Embedder.load_embeddings(str(EMBEDDINGS_FILE))
    except FileNotFoundError:
        logger.error("Embeddings not found. Run embedder.py first.")
        exit(1)

    # Prepare retriever
    prepare_retriever(embeddings, questions, str(FAISS_INDEX_FILE))
