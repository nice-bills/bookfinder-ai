import logging
import os
import pickle
import sys
import numpy as np
import pandas as pd

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.book_recommender.core.config as config
from src.book_recommender.ml.clustering import cluster_books, get_cluster_names

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def precompute_clusters():
    logger.info("--- Starting Cluster Pre-computation ---")
    
    # 1. Load Data
    if not os.path.exists(config.PROCESSED_DATA_PATH) or not os.path.exists(config.EMBEDDINGS_PATH):
        logger.error("Data files missing. Run data processor and embedder first.")
        return

    logger.info(f"Loading book data from {config.PROCESSED_DATA_PATH}...")
    book_data_df = pd.read_parquet(config.PROCESSED_DATA_PATH)
    
    logger.info(f"Loading embeddings from {config.EMBEDDINGS_PATH}...")
    embeddings_arr = np.load(config.EMBEDDINGS_PATH)

    # 2. Cluster
    n_clusters = config.NUM_CLUSTERS
    logger.info(f"Clustering {len(book_data_df)} books into {n_clusters} clusters...")
    
    clusters_arr, _ = cluster_books(embeddings_arr, n_clusters=n_clusters)
    
    # 3. Name Clusters
    book_data_df["cluster_id"] = clusters_arr
    names = get_cluster_names(book_data_df, clusters_arr)
    
    # 4. Save Cache
    cache_path = config.PROCESSED_DATA_DIR / "cluster_cache.pkl"
    logger.info(f"Saving cache to {cache_path}...")
    
    try:
        with open(cache_path, "wb") as f:
            # Must match the tuple structure expected by api/dependencies.py
            # (clusters_arr, names, book_data_df)
            pickle.dump((clusters_arr, names, book_data_df), f)
        logger.info("Successfully pre-computed and cached clusters.")
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")

if __name__ == "__main__":
    precompute_clusters()
