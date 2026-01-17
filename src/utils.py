from datetime import datetime
import os

def get_timestamp() -> str:
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()

def ensure_output_directory(output_dir: str = "output") -> None:
    """Ensure output directory exists."""
    os.makedirs(output_dir, exist_ok=True)

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length characters."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def validate_article(article: dict) -> bool:
    """
    Validate that article has required fields.
    
    Args:
        article: Article dictionary
    
    Returns:
        True if valid, False otherwise
    """
    # Only require title and content (description is optional)
    required_fields = ["title", "content"]
    return all(article.get(field) for field in required_fields)

def format_article_summary(article: dict) -> str:
    """
    Format article into a concise summary string.
    
    Args:
        article: Article dictionary
    
    Returns:
        Formatted summary string
    """
    title = article.get("title", "Untitled")
    source = article.get("source", {}).get("name", "Unknown")
    published = article.get("publishedAt", "Unknown")
    
    return f"{title} | {source} | {published}"

def print_progress(current: int, total: int, message: str = "") -> None:
    """Print progress indicator."""
    percentage = (current / total * 100) if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "-" * (bar_length - filled)
    
    print(f"\r[{bar}] {percentage:.1f}% ({current}/{total}) {message}", end="", flush=True)
    
    if current == total:
        print()  # New line when complete
