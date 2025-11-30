import ast
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pandas as pd

from src.book_recommender.core.exceptions import DataNotFoundError, FileProcessingError
from src.book_recommender.utils import ensure_dir_exists

logger = logging.getLogger(__name__)


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans, deduplicates, and engineers features on a raw book DataFrame.

    This function performs the following main operations:
    1.  Handles missing columns by initializing them as empty strings.
    2.  Fills any NaN values in text columns with empty strings.
    3.  Converts all text columns to string type for safety.
    4.  Creates lowercase versions of 'title' and 'authors' for matching,
        while preserving the original casing for display.
    5.  Deduplicates the DataFrame based on the lowercased title.
    6.  Removes rows with empty titles.
    7.  Engineers the 'combined_text' feature for embeddings, applying a
        weighting strategy to give more importance to the title and author.

    Args:
        df (pd.DataFrame): The raw book data, typically from a CSV.

    Returns:
        pd.DataFrame: The processed DataFrame ready for embedding.

    Raises:
        ValueError: If the DataFrame is empty after processing.
    """
    logger.info("Starting data cleaning and preparation...")
    logger.info(f"Found columns in CSV: {df.columns.tolist()}")

    expected_cols = ["title", "authors", "genres", "description", "tags"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            logger.warning(f"Column '{col}' not found in CSV. Initializing as empty.")

    df[expected_cols] = df[expected_cols].fillna("")

    for col in expected_cols:
        df[col] = df[col].astype(str)

    if "book_id" in df.columns:
        df["id"] = df["book_id"].astype(str)
        logger.info("Using 'book_id' as the unique identifier.")
    else:
        df["id"] = df.index.astype(str)
        logger.warning("No 'book_id' column found. Generated 'id' from DataFrame index.")

    for col in ["genres", "tags"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: ", ".join(ast.literal_eval(x)) if (x.startswith("[") and x.endswith("]")) else x
            )

    df["title_lower"] = df["title"].str.strip().str.lower()
    df["authors_lower"] = df["authors"].str.strip().str.lower()

    # Clean description text (remove HTML tags and artifacts)
    # This regex removes <br>, <i>, <b> tags and their closing counterparts
    import re
    def clean_html_text(text):
        if not isinstance(text, str):
            return text
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)  # Replace <br> with newline
        text = re.sub(r'<[^>]+>', '', text)  # Remove other HTML tags
        return text.strip()

    df["description"] = df["description"].apply(clean_html_text)

    # Lowercase genres/tags for normalization, but keep description/title case for display
    for col in ["genres", "tags"]:
        df[col] = df[col].str.strip().str.lower()

    original_rows = len(df)
    df.drop_duplicates(subset=["title_lower"], keep="first", inplace=True)
    new_rows = len(df)
    if new_rows < original_rows:
        logger.info(f"Removed {original_rows - new_rows} duplicate books based on title.")

    original_rows = len(df)
    df.dropna(subset=["title_lower"], inplace=True)
    df = df[df["title_lower"] != ""].copy()
    if len(df) < original_rows:
        logger.warning(f"Dropped {original_rows - len(df)} rows with missing titles.")

    if df.empty:
        logger.error("DataFrame is empty after cleaning. No valid book data to process.")
        raise ValueError(
            "No valid books found after processing. The dataset might be empty or contain only invalid entries."
        )

    logger.info("Creating 'combined_text' for embeddings with weighted fields...")
    # Use lowercased description ONLY for embedding generation, not for storage
    df["combined_text"] = (
        (df["title_lower"] + " ") * 3
        + "by "
        + df["authors_lower"]
        + ". "
        + "genres: "
        + df["genres"]
        + ". "
        + "description: "
        + df["description"].str.lower()
        + ". "
        + "tags: "
        + df["tags"]
    )
    return df


def clean_and_prepare_data(raw_path: str, processed_path: str) -> pd.DataFrame:
    """
    Orchestrator function that loads raw data, processes it, and saves the result.

    This function chains the data processing steps:
    1.  Loads the raw CSV data from `raw_path`.
    2.  Calls `process_dataframe` to perform all cleaning and feature engineering.
    3.  Saves the cleaned DataFrame to a Parquet file at `processed_path`.

    Args:
        raw_path (str): The file path for the raw CSV data.
        processed_path (str): The file path to save the processed Parquet file.

    Returns:
        pd.DataFrame: The fully processed DataFrame.

    Raises:
        DataNotFoundError: If the file at `raw_path` is not found.
        FileProcessingError: If the CSV file cannot be parsed.
    """
    if not os.path.exists(raw_path):
        logger.error(f"Raw data file not found at: {raw_path}")
        raise DataNotFoundError(f"Raw data file not found at: {raw_path}")

    try:
        logger.info(f"Loading raw data from {raw_path}...")
        raw_df = pd.read_csv(raw_path)
        logger.info(f"Loaded {len(raw_df)} rows.")
    except (pd.errors.ParserError, UnicodeDecodeError) as e:
        logger.error(f"Failed to parse CSV from {raw_path}: {e}")
        raise FileProcessingError(f"Failed to parse CSV from {raw_path}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading CSV from {raw_path}: {e}")
        raise

    processed_df = process_dataframe(raw_df)

    try:
        ensure_dir_exists(processed_path)
        logger.info(f"Saving processed data to {processed_path}...")
        processed_df.to_parquet(processed_path, index=False)
        logger.info(f"Successfully saved {len(processed_df)} processed rows.")
    except Exception as e:
        logger.error(f"Failed to save processed data to {processed_path}: {e}")
        raise

    return processed_df


if __name__ == "__main__":
    import argparse

    import book_recommender.core.config as config

    if os.getenv("LOG_LEVEL"):
        logging.basicConfig(level=os.getenv("LOG_LEVEL"))
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Clean and prepare book data.")
    parser.add_argument("--raw-path", type=str, default=config.RAW_DATA_PATH, help="Path to the raw CSV data file.")
    parser.add_argument(
        "--processed-path",
        type=str,
        default=config.PROCESSED_DATA_PATH,
        help="Path to save the processed Parquet file.",
    )
    args = parser.parse_args()

    logger.info("--- Starting Data Processing Standalone Script ---")
    clean_and_prepare_data(raw_path=args.raw_path, processed_path=args.processed_path)
    logger.info("--- Data Processing Finished ---")
