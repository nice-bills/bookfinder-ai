"""Machine learning modules for BookFinder-AI"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.book_recommender.ml.clustering import cluster_books, get_cluster_names
from src.book_recommender.ml.embedder import generate_embedding_for_query, generate_embeddings
from src.book_recommender.ml.explainability import explain_recommendation
from src.book_recommender.ml.feedback import get_all_feedback, save_feedback
from src.book_recommender.ml.recommender import BookRecommender

__all__ = [
    "BookRecommender",
    "generate_embedding_for_query",
    "generate_embeddings",
    "cluster_books",
    "get_cluster_names",
    "explain_recommendation",
    "save_feedback",
    "get_all_feedback",
]
