"""
Data Loader Module
Handles loading and preprocessing data from Kaggle dataset
"""
import pandas as pd
import pickle
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import json
from src.config import (
    KAGGLE_DATASET_PATH,
    CORPUS_PICKLE,
    DATA_DIR,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and preprocess university chatbot dataset"""

    def __init__(self):
        self.corpus = {}
        self.questions = []
        self.answers = []

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        """
        if not isinstance(text, str):
            return str(text)
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def load_kaggle_dataset(self) -> Dict[str, str]:
        """
        Load dataset from Kaggle CSV or JSON file
        Expected format: columns like 'Question', 'Answer' or 'question', 'response'
        """
        if not KAGGLE_DATASET_PATH.exists():
            logger.warning(
                f"Dataset not found at {KAGGLE_DATASET_PATH}. Using fallback intents.json"
            )
            return self._load_intents_json()

        try:
            # Try loading as CSV
            if str(KAGGLE_DATASET_PATH).endswith(".csv"):
                df = pd.read_csv(KAGGLE_DATASET_PATH)
                return self._process_dataframe(df)
            # Try loading as JSON
            elif str(KAGGLE_DATASET_PATH).endswith(".json"):
                with open(KAGGLE_DATASET_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self._process_json_data(data)
        except Exception as e:
            logger.error(f"Error loading Kaggle dataset: {e}")
            logger.info("Falling back to intents.json")
            return self._load_intents_json()

    def _process_dataframe(self, df: pd.DataFrame) -> Dict[str, str]:
        """Process pandas DataFrame into Q&A corpus"""
        corpus = {}

        # Auto-detect column names (case-insensitive)
        question_col = None
        answer_col = None

        for col in df.columns:
            col_lower = col.lower()
            if "question" in col_lower or "query" in col_lower or "q" == col_lower:
                question_col = col
            if "answer" in col_lower or "response" in col_lower or "a" == col_lower:
                answer_col = col

        if question_col is None or answer_col is None:
            logger.warning(
                "Could not auto-detect Q&A columns. Using first two columns."
            )
            question_col = df.columns[0]
            answer_col = df.columns[1]

        logger.info(f"Using columns: Question='{question_col}', Answer='{answer_col}'")

        for idx, row in df.iterrows():
            question = self.clean_text(str(row[question_col]))
            answer = self.clean_text(str(row[answer_col]))

            if question and answer:
                corpus[question] = answer

        logger.info(f"Loaded {len(corpus)} Q&A pairs from dataset")
        return corpus

    def _process_json_data(self, data) -> Dict[str, str]:
        """Process JSON data into Q&A corpus"""
        corpus = {}

        if isinstance(data, dict) and "intents" in data:
            # Handle intents.json format
            for intent in data.get("intents", []):
                responses = intent.get("responses", [])
                for text in intent.get("text", []):
                    question = self.clean_text(text)
                    # Use first response or concatenate all
                    answer = (
                        self.clean_text(responses[0])
                        if responses
                        else "No response available"
                    )
                    if question and answer:
                        corpus[question] = answer

        elif isinstance(data, list):
            # Handle list of Q&A objects
            for item in data:
                if isinstance(item, dict):
                    for key in ["question", "q", "query"]:
                        if key in item:
                            question = self.clean_text(str(item[key]))
                            break
                    for key in ["answer", "response", "a"]:
                        if key in item:
                            answer = self.clean_text(str(item[key]))
                            break
                    if question and answer:
                        corpus[question] = answer

        logger.info(f"Loaded {len(corpus)} Q&A pairs from JSON")
        return corpus

    def _load_intents_json(self) -> Dict[str, str]:
        """Fallback: Load from intents.json in project root"""
        intents_path = Path(__file__).parent.parent / "intents.json"

        if not intents_path.exists():
            logger.warning("No intents.json found. Using minimal corpus.")
            return self._get_minimal_corpus()

        try:
            with open(intents_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            corpus = self._process_json_data(data)
            return corpus if corpus else self._get_minimal_corpus()
        except Exception as e:
            logger.error(f"Error loading intents.json: {e}")
            return self._get_minimal_corpus()

    @staticmethod
    def _get_minimal_corpus() -> Dict[str, str]:
        """Minimal corpus for testing"""
        return {
            "hello": "Hello! How can I help you?",
            "what is admission": "Admission is the process of enrolling in a university program.",
            "tell me about fees": "Fees vary by program. Please contact the admissions office.",
            "how to apply": "You can apply through our online portal on the website.",
            "what are the requirements": "Requirements include high school diploma and entrance exam scores.",
        }

    def load_and_prepare(self) -> Tuple[List[str], Dict[str, str]]:
        """
        Load dataset and prepare corpus
        Returns: (questions_list, corpus_dict)
        """
        # Load corpus
        self.corpus = self.load_kaggle_dataset()

        if not self.corpus:
            logger.error("Failed to load any corpus")
            raise ValueError("No corpus loaded")

        # Extract questions
        self.questions = list(self.corpus.keys())

        logger.info(f"Prepared corpus with {len(self.questions)} questions")
        return self.questions, self.corpus

    def save_corpus(self) -> None:
        """Save corpus to pickle file"""
        CORPUS_PICKLE.parent.mkdir(parents=True, exist_ok=True)

        with open(CORPUS_PICKLE, "wb") as f:
            pickle.dump(self.corpus, f)
        logger.info(f"Corpus saved to {CORPUS_PICKLE}")

    @staticmethod
    def load_corpus() -> Dict[str, str]:
        """Load corpus from pickle file"""
        if not CORPUS_PICKLE.exists():
            raise FileNotFoundError(f"Corpus not found at {CORPUS_PICKLE}")

        with open(CORPUS_PICKLE, "rb") as f:
            corpus = pickle.load(f)
        logger.info(f"Loaded corpus with {len(corpus)} Q&A pairs")
        return corpus


def prepare_dataset():
    """
    Main function to prepare dataset
    Run this once to process and save embeddings
    """
    logger.basicConfig(level=logging.INFO)

    loader = DataLoader()
    questions, corpus = loader.load_and_prepare()
    loader.save_corpus()

    logger.info("Dataset preparation complete!")
    return questions, corpus


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    prepare_dataset()
