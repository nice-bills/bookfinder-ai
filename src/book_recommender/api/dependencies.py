import logging
import os
import pickle
import sys
from functools import lru_cache

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from slowapi import Limiter
from slowapi.util import get_remote_address

import src.book_recommender.core.config as config
from src.book_recommender.core.exceptions import DataNotFoundError
from src.book_recommender.ml.clustering import (
    cluster_books,
    get_cluster_names,
)
from src.book_recommender.ml.embedder import (
    load_model as embedder_load_model,
)
from src.book_recommender.ml.recommender import BookRecommender

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

CLUSTER_CACHE_PATH = config.PROCESSED_DATA_DIR / "cluster_cache.pkl"
MODEL_CACHE_PATH = config.PROCESSED_DATA_DIR / "model_cache"


@lru_cache(maxsize=1)
def get_recommender() -> BookRecommender:
    """Load and cache BookRecommender (fast - uses cached files)"""
    try:
        logger.info("Loading book data and embeddings...")
        book_data_df = pd.read_parquet(config.PROCESSED_DATA_PATH)
        embeddings_arr = np.load(config.EMBEDDINGS_PATH)

        recommender = BookRecommender(book_data=book_data_df, embeddings=embeddings_arr)
        logger.info(f"Recommender ready | {len(book_data_df)} books loaded")
        return recommender
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise DataNotFoundError(
            f"Missing data files. Check '{config.PROCESSED_DATA_PATH}' and '{config.EMBEDDINGS_PATH}'"
        )
    except Exception as e:
        logger.error(f"Error initializing recommender: {e}")
        raise


@lru_cache(maxsize=1)
def get_sentence_transformer_model() -> SentenceTransformer:
    """
    Load model using the centralized, robust loader from embedder.py.
    The loader handles checking for a local cache and downloading if missing.
    """
    logger.info("Requesting embedding model...")
    return embedder_load_model(config.EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_clusters_data() -> tuple[np.ndarray, dict, pd.DataFrame]:
    """
    Get clusters data with intelligent caching.

    Loads from cache if available, otherwise generates and caches.
    """
    logger.info("Loading cluster data...")

    if CLUSTER_CACHE_PATH.exists():
        try:
            cache_mtime = os.path.getmtime(CLUSTER_CACHE_PATH)
            embeddings_mtime = os.path.getmtime(config.EMBEDDINGS_PATH)

            if cache_mtime > embeddings_mtime:
                logger.info("Loading clusters from cache...")
                with open(CLUSTER_CACHE_PATH, "rb") as f:
                    clusters_arr, names, book_data_df = pickle.load(f)
                logger.info(f"Clusters loaded from cache | {len(names)} clusters")
                return clusters_arr, names, book_data_df
            else:
                logger.info("Cache outdated, regenerating...")
        except Exception as e:
            logger.warning(f"Cache load failed: {e}, regenerating...")

    logger.info("Generating clusters (this takes ~30 seconds)...")
    recommender = get_recommender()
    book_data_df = recommender.book_data.copy()
    embeddings_arr = recommender.embeddings

    clusters_arr, _ = cluster_books(embeddings_arr, n_clusters=config.NUM_CLUSTERS)
    book_data_df["cluster_id"] = clusters_arr
    names = get_cluster_names(book_data_df, clusters_arr)

    try:
        with open(CLUSTER_CACHE_PATH, "wb") as f:
            pickle.dump((clusters_arr, names, book_data_df), f)
        logger.info(f"Clusters cached to {CLUSTER_CACHE_PATH}")
    except Exception as e:
        logger.warning(f"Failed to cache clusters: {e}")

    logger.info(f"Clusters ready | {len(names)} clusters generated")
    return clusters_arr, names, book_data_df
