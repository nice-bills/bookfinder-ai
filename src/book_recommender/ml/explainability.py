import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


def _normalize_to_list(field_value: Union[str, List[str], None]) -> List[str]:
    """Normalize a string (comma-separated) or list of strings into a list of strings."""
    if not field_value:
        return []
    if isinstance(field_value, list):
        return [str(item).strip() for item in field_value]
    if isinstance(field_value, str):
        return [item.strip() for item in field_value.split(",") if item.strip()]
    return []


def _generate_summary(
    query_text: str, recommended_book: Dict[str, Any], contribution_scores: Dict[str, float]
) -> tuple[str, List[str]]:
    """
    Generates a natural language summary of why a book was recommended.
    Returns the summary string and a list of identified matching features.
    """
    summary = f"Recommended because it's a good match for your interest in '{query_text}'. "

    matching_features = []
    if contribution_scores.get("genres", 0) > 0.1:
        book_genres_list = _normalize_to_list(recommended_book.get("genres"))
        if book_genres_list:
            matching_features.append(f"shares genres like {', '.join(book_genres_list)}")

    if contribution_scores.get("description_keywords", 0) > 0.1:
        if recommended_book.get("description"):
            query_words_lower = set(query_text.lower().split())
            book_description_words_lower = set(recommended_book["description"].lower().split())

            common_keywords = list(query_words_lower.intersection(book_description_words_lower))
            if common_keywords:
                matching_features.append(f"has keywords in description like '{', '.join(common_keywords[:3])}'")

    if contribution_scores.get("authors", 0) > 0.1:
        book_authors_list = _normalize_to_list(recommended_book.get("authors"))
        if book_authors_list and book_authors_list != ["Unknown Author"]:
            matching_features.append(f"is by author(s) {', '.join(book_authors_list)}")

    if matching_features:
        summary += "Specifically, it " + ", and ".join(matching_features) + "."
    else:
        summary += "Its content aligns well with your query."

    return summary, matching_features


def get_contribution_scores(query_text: str, recommended_book: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculates hypothetical contribution scores for different features
    (genres, description keywords, authors) to the recommendation.
    This is a simplified, rule-based approach for demonstration.
    """
    scores = {"genres": 0.0, "description_keywords": 0.0, "authors": 0.0}

    query_genres = set(
        [g.strip() for g in query_text.lower().replace("genre", "").replace("genres", "").split() if g.strip()]
    )
    book_genres_list = _normalize_to_list(recommended_book.get("genres"))
    book_genres = set(g.lower() for g in book_genres_list)
    if query_genres and book_genres:
        overlap = len(query_genres.intersection(book_genres))
        if overlap > 0:
            scores["genres"] = overlap / max(len(query_genres), len(book_genres)) * 0.5

    query_words = set(query_text.lower().split())
    book_description_words = set(recommended_book.get("description", "").lower().split())
    if query_words and book_description_words:
        overlap = len(query_words.intersection(book_description_words))
        if overlap > 0:
            scores["description_keywords"] = min(overlap / 5, 1.0) * 0.3

    query_authors = set([a.strip() for a in query_text.lower().replace("by", "").split() if a.strip()])
    book_authors_list = _normalize_to_list(recommended_book.get("authors"))
    book_authors = set(a.lower() for a in book_authors_list)
    if query_authors and book_authors:
        overlap = len(query_authors.intersection(book_authors))
        if overlap > 0:
            scores["authors"] = overlap / max(len(query_authors), len(book_authors)) * 0.2

    return scores


def explain_recommendation(
    query_text: str, recommended_book: Dict[str, Any], similarity_score: float
) -> Dict[str, Any]:
    """
    Generates an explanation for why a particular book was recommended.

    Args:
        query_text (str): The original natural language query from the user.
        recommended_book (Dict[str, Any]): The details of the recommended book.
        similarity_score (float): The cosine similarity score for the recommendation.

    Returns:
        Dict[str, Any]: A dictionary containing explanation details.
    """
    logger.info(f"Generating explanation for '{recommended_book.get('title')}' based on query '{query_text}'")

    contribution_scores = get_contribution_scores(query_text, recommended_book)

    confidence = "LOW"
    if similarity_score > 0.5:
        confidence = "MEDIUM"
    if similarity_score > 0.7:
        confidence = "HIGH"

    if sum(contribution_scores.values()) > 0.6:
        confidence = "VERY HIGH"
    elif sum(contribution_scores.values()) > 0.3 and confidence == "LOW":
        confidence = "MEDIUM"

    summary, matching_features = _generate_summary(query_text, recommended_book, contribution_scores)

    explanation = {
        "match_score": round(similarity_score * 100),
        "confidence": confidence,
        "summary": summary,
        "matching_features": matching_features,
        "details": {
            "genres_contribution": round(contribution_scores["genres"] * 100),
            "description_keywords_contribution": round(contribution_scores["description_keywords"] * 100),
            "authors_contribution": round(contribution_scores["authors"] * 100),
        },
    }
    logger.debug(f"Explanation generated: {explanation}")
    return explanation


if __name__ == "__main__":
    sample_query = "science fiction about time travel and artificial intelligence"
    sample_book = {
        "id": "123",
        "title": "The Hitchhiker's Guide to the Galaxy",
        "authors": "Douglas Adams",
        "description": (
            "A comedic science fiction series with philosophical undertones " "about a man travelling through space."
        ),
        "genres": "Science Fiction, Comedy, Absurdist",
        "tags": "space, aliens, artificial intelligence, robots, philosophy",
        "rating": 4.5,
    }
    sample_similarity = 0.75

    explanation_result = explain_recommendation(sample_query, sample_book, sample_similarity)

    print("\n--- Explanation Example ---")
    print(f"Match Score: {explanation_result['match_score']}")
    print(f"Confidence: {explanation_result['confidence']}")
    print(f"Why this book? {explanation_result['summary']}")
    print("Details:")
    print(f"  - Genres Contribution: {explanation_result['details']['genres_contribution']}")
    print(
        f"  - Description Keywords Contribution: {explanation_result['details']['description_keywords_contribution']}"
    )
    print(f"  - Authors Contribution: {explanation_result['details']['authors_contribution']}")

    sample_query_2 = "a historical drama with strong female characters"
    sample_book_2 = {
        "id": "456",
        "title": "Pride and Prejudice",
        "authors": ["Jane Austen"],
        "description": "A classic novel of manners, love, and marriage among the English gentry of the 19th century.",
        "genres": ["Romance", "Classic", "Historical"],
        "tags": "social commentary, strong female lead, period drama",
        "rating": 4.2,
    }
    sample_similarity_2 = 0.60
    explanation_result_2 = explain_recommendation(sample_query_2, sample_book_2, sample_similarity_2)

    print("\n--- Explanation Example 2 (with lists) ---")
    print(f"Match Score: {explanation_result_2['match_score']}")
    print(f"Confidence: {explanation_result_2['confidence']}")
    print(f"Why this book? {explanation_result_2['summary']}")
    print("Details:")
    print(f"  - Genres Contribution: {explanation_result_2['details']['genres_contribution']}")
    print(
        f"  - Description Keywords Contribution: {explanation_result_2['details']['description_keywords_contribution']}"
    )
    print(f"  - Authors Contribution: {explanation_result_2['details']['authors_contribution']}")
