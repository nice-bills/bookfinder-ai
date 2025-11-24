import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def prepare_goodreads_data():
    """
    Convert Goodreads CSV format to the format expected by data_processor.

    Maps:
    - Book → title
    - Author → authors
    - Avg_Rating → rating
    - Description → description
    - Genres → genres
    - Creates 'tags' from genres
    - Drops: Unnamed: 0, Num_Ratings, URL
    """
    input_path = "data/raw/goodreads_data.csv"
    output_path = "data/raw/books_prepared.csv"

    logger.info(f"Loading Goodreads data from {input_path}...")

    try:
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} books")
        logger.info(f"Original columns: {df.columns.tolist()}")

        if "Unnamed: 0" in df.columns or "" in df.columns:
            df = df.drop(columns=[col for col in df.columns if "Unnamed" in str(col) or col == ""])
            logger.info("Dropped unnamed index column")

        logger.info("Renaming columns...")
        df = df.rename(
            columns={
                "Book": "title",
                "Author": "authors",
                "Avg_Rating": "rating",
                "Description": "description",
                "Genres": "genres",
            }
        )

        df["tags"] = ""
        logger.info("Created 'tags' column (empty - can be populated later)")

        columns_to_keep = ["title", "authors", "genres", "description", "tags", "rating"]

        missing_cols = [col for col in columns_to_keep if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns after mapping: {missing_cols}")
            logger.error(f"Available columns: {df.columns.tolist()}")
            raise ValueError(f"Column mapping failed. Missing: {missing_cols}")

        df = df[columns_to_keep]

        logger.info(f"Final shape: {df.shape}")
        logger.info(f"Final columns: {df.columns.tolist()}")
        logger.info(f"Sample row:\n{df.iloc[0]}")

        null_rows = df.isnull().all(axis=1).sum()
        if null_rows > 0:
            logger.warning(f"Found {null_rows} completely null rows - will be removed by processor")

        logger.info(f"Saving prepared data to {output_path}...")
        df.to_csv(output_path, index=False)
        logger.info(f" Successfully prepared {len(df)} books")

        logger.info("\n Dataset Summary:")
        logger.info(f"  Total books: {len(df)}")
        logger.info(f"  Books with ratings: {df['rating'].notna().sum()}")
        logger.info(f"  Books with descriptions: {(df['description'] != '').sum()}")
        logger.info(f"  Average rating: {df['rating'].mean():.2f}")

        print("\n Data preparation complete!")
        print(f"   Input:  {input_path}")
        print(f"   Output: {output_path}")
        print("\n Next steps:")
        print("   1. Update src/config.py line 17:")
        print("      RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, 'books_prepared.csv')")
        print("   2. Run: python src/data_processor.py")
        print("   3. Run: python src/embedder.py")
        print("   4. Run: streamlit run app.py")

        return df

    except FileNotFoundError:
        logger.error(f"File not found: {input_path}")
        logger.error("Make sure goodreads_data.csv exists in data/raw/")
        raise
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise


if __name__ == "__main__":
    prepare_goodreads_data()
