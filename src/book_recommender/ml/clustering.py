import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


def cluster_books(embeddings: np.ndarray, n_clusters: int = 20, random_state: int = 42) -> tuple[np.ndarray, KMeans]:
    """
    Cluster books using K-Means.

    Args:
        embeddings (np.ndarray): A 2D NumPy array of book embeddings.
        n_clusters (int): The number of clusters to form.
        random_state (int): Seed for reproducibility.

    Returns:
        tuple[np.ndarray, KMeans]: A tuple containing:
            - np.ndarray: An array of cluster labels for each book.
            - KMeans: The fitted KMeans model.
    """
    logger.info(f"Starting K-Means clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    clusters = kmeans.fit_predict(embeddings)
    logger.info("K-Means clustering completed.")
    return clusters, kmeans


def get_cluster_names(book_data: pd.DataFrame, clusters: np.ndarray) -> dict[int, str]:
    """
    Generate descriptive names for clusters based on the most common genres.

    Args:
        book_data (pd.DataFrame): DataFrame containing book metadata, including a 'genres' column.
        clusters (np.ndarray): An array of cluster labels for each book.

    Returns:
        dict[int, str]: A dictionary mapping cluster IDs to their descriptive names.
    """
    logger.info("Generating descriptive names for clusters...")
    cluster_names = {}

    temp_genres_list = book_data["genres"].apply(
        lambda x: [g.strip() for g in x.split(",") if g.strip()] if isinstance(x, str) else []
    )

    for cluster_id in range(max(clusters) + 1):
        cluster_books_indices = np.where(clusters == cluster_id)[0]
        if len(cluster_books_indices) == 0:
            cluster_names[cluster_id] = f"Empty Cluster {cluster_id}"
            logger.warning(f"Cluster {cluster_id} is empty.")
            continue

        genres_in_cluster = temp_genres_list.iloc[cluster_books_indices]

        all_genres = [genre for sublist in genres_in_cluster for genre in sublist]

        if all_genres:
            genre_counts = pd.Series(all_genres).value_counts()
            top_genre = genre_counts.index[0]
            cluster_names[cluster_id] = f"{top_genre.title()} Collection"
        else:
            cluster_names[cluster_id] = f"Miscellaneous Cluster {cluster_id}"
        logger.debug(f"Cluster {cluster_id} named: {cluster_names[cluster_id]}")

    logger.info("Cluster names generated.")
    return cluster_names
