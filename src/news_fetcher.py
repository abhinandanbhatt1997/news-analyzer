import os
import uuid
import requests
from typing import List, Dict
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()


class NewsFetcherError(Exception):
    """Custom exception for news fetching failures."""
    pass


def _get_session() -> requests.Session:
    """
    Create a requests session with retry logic.
    """
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


def fetch_news() -> List[Dict]:
    """
    Fetch recent Indian political news articles from NewsAPI.

    Returns:
        List of normalized article dictionaries.

    Raises:
        NewsFetcherError: If API key missing or request fails.
    """
    api_key = os.getenv("NEWSAPI_API_KEY")
    query = os.getenv("NEWS_QUERY", "India politics")
    max_articles = int(os.getenv("MAX_ARTICLES", 12))
    timeout = int(os.getenv("REQUEST_TIMEOUT", 10))

    if not api_key:
        raise NewsFetcherError("Missing NEWSAPI_API_KEY in environment variables.")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": api_key,
    }

    session = _get_session()

    try:
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise NewsFetcherError(f"Failed to fetch news: {e}")

    data = response.json()
    raw_articles = data.get("articles", [])

    normalized_articles = []

    for article in raw_articles:
        title = article.get("title")
        content = article.get("content") or article.get("description")
        source = article.get("source", {}).get("name")
        url = article.get("url")
        published_at = article.get("publishedAt")

        # Filter unusable articles
        if not title or not content or len(content) < 50:
            continue

        normalized_articles.append(
            {
                "id": str(uuid.uuid4()),
                "title": title.strip(),
                "content": content.strip(),
                "source": source or "Unknown",
                "url": url,
                "published_at": published_at,
            }
        )

    if not normalized_articles:
        raise NewsFetcherError("No valid articles found after normalization.")

    return normalized_articles
