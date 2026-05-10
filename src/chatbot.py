"""
Chatbot Core Module
Main RAG pipeline combining embedder and retriever
"""
import logging
from typing import Dict, List, Tuple
import numpy as np

from src.config import (
    EMBEDDING_MODEL,
    TOP_K,
    SIMILARITY_THRESHOLD,
    CORPUS_PICKLE,
    EMBEDDINGS_FILE,
    FAISS_INDEX_FILE,
)
from src.embedder import Embedder
from src.retriever import FAISSRetriever
from src.data_loader import DataLoader

logger = logging.getLogger(__name__)


class Chatbot:
    """RAG-based University Chatbot"""

    def __init__(self):
        """Initialize chatbot with embedder and retriever"""
        self.embedder = None
        self.retriever = None
        self.corpus = None
        self.is_ready = False

        try:
            self._initialize()
            self.is_ready = True
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            self.is_ready = False

    def _initialize(self):
        """Initialize all components"""
        logger.info("Initializing chatbot components...")

        # Load corpus
        try:
            self.corpus = DataLoader.load_corpus()
            logger.info(f"Loaded corpus with {len(self.corpus)} Q&A pairs")
        except FileNotFoundError:
            logger.warning("Corpus not found. Preparing dataset...")
            loader = DataLoader()
            questions, corpus = loader.load_and_prepare()
            self.corpus = corpus
            loader.save_corpus()

        # Load or create embedder and retriever
        try:
            # Try to load pre-computed index
            self.embedder = Embedder(model_name=EMBEDDING_MODEL)
            self.retriever = FAISSRetriever.load_index(
                str(FAISS_INDEX_FILE), list(self.corpus.keys())
            )
            logger.info("Loaded pre-computed embeddings and FAISS index")
        except Exception as e:
            logger.warning(f"Could not load pre-computed index: {e}. Generating new...")
            self._generate_embeddings_and_index()

    def _generate_embeddings_and_index(self):
        """Generate embeddings and build FAISS index"""
        logger.info("Generating embeddings and building FAISS index...")

        # Create embedder
        self.embedder = Embedder(model_name=EMBEDDING_MODEL)

        # Generate embeddings
        questions = list(self.corpus.keys())
        embeddings = self.embedder.embed_texts(questions, show_progress=True)

        # Save embeddings
        self.embedder.save_embeddings(embeddings, str(EMBEDDINGS_FILE))

        # Build and save FAISS index
        self.retriever = FAISSRetriever(embeddings, questions)
        self.retriever.save_index(str(FAISS_INDEX_FILE))

        logger.info("Embeddings and FAISS index generated successfully")

    def answer_query(self, query: str, top_k: int = TOP_K) -> Dict:
        """
        Answer a user query using RAG
        
        Args:
            query: User question
            top_k: Number of answers to retrieve
            
        Returns:
            Dictionary with answer, alternatives, and metadata
        """
        if not self.is_ready:
            return {
                "status": "error",
                "message": "Chatbot not initialized",
                "answer": "I'm having trouble connecting to my knowledge base. Please try again.",
            }

        try:
            # Embed query
            query_embedding = self.embedder.embed_single(query)

            # Retrieve top-k
            retrieved_questions, confidences = self.retriever.retrieve_top_k(
                query_embedding, k=top_k
            )

            # Format response
            if not retrieved_questions:
                return {
                    "status": "no_match",
                    "answer": "Sorry, I couldn't find relevant information in my knowledge base. Could you rephrase your question?",
                    "confidence": 0.0,
                }

            best_match = retrieved_questions[0]
            best_confidence = confidences[0]

            # Check confidence threshold
            if best_confidence < SIMILARITY_THRESHOLD:
                return {
                    "status": "low_confidence",
                    "answer": "I found some information but I'm not very confident about it. Could you rephrase?",
                    "suggested_answer": self.corpus[best_match],
                    "confidence": best_confidence,
                }

            # Build response
            main_answer = self.corpus[best_match]
            alternatives = [
                {
                    "question": retrieved_questions[i],
                    "answer": self.corpus[retrieved_questions[i]],
                    "confidence": confidences[i],
                }
                for i in range(1, min(len(retrieved_questions), top_k))
            ]

            response = {
                "status": "success",
                "query": query,
                "matched_question": best_match,
                "answer": main_answer,
                "confidence": best_confidence,
                "alternatives": alternatives,
                "num_alternatives": len(alternatives),
            }

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "message": str(e),
                "answer": "An error occurred while processing your query. Please try again.",
            }

    def format_response(self, response_dict: Dict) -> str:
        """
        Format response dictionary for display
        
        Args:
            response_dict: Response dictionary from answer_query
            
        Returns:
            Formatted string response
        """
        if response_dict["status"] != "success":
            return response_dict.get("answer", "Unable to process query")

        answer = response_dict.get("answer", "No answer found")
        confidence = response_dict.get("confidence", 0)
        alternatives = response_dict.get("alternatives", [])

        # Format answer
        formatted = f"**Answer:** {answer}\n\n"
        formatted += f"*Confidence: {confidence:.1%}*"

        # Add alternatives if available
        if alternatives:
            formatted += "\n\n**Related Answers:**\n"
            for i, alt in enumerate(alternatives, 1):
                formatted += f"\n{i}. {alt['answer']}\n   *(Confidence: {alt['confidence']:.1%})*"

        return formatted

    def get_status(self) -> Dict:
        """Get chatbot status"""
        return {
            "is_ready": self.is_ready,
            "embedding_model": EMBEDDING_MODEL,
            "corpus_size": len(self.corpus) if self.corpus else 0,
            "top_k": TOP_K,
        }


def initialize_chatbot() -> Chatbot:
    """Initialize and return chatbot instance"""
    return Chatbot()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize chatbot
    chatbot = Chatbot()

    if not chatbot.is_ready:
        print("Failed to initialize chatbot")
        exit(1)

    # Test queries
    test_queries = [
        "What is admission?",
        "How to apply?",
        "Tell me about fees",
        "Unknown topic xyz",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        response = chatbot.answer_query(query)
        formatted = chatbot.format_response(response)
        print(formatted)
