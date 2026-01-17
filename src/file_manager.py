import json
import os
from datetime import datetime
from typing import List, Dict

class FileManagerError(Exception):
    pass

def save_raw_articles(articles: List[Dict], output_dir: str = "output") -> str:
    """
    Save raw fetched articles to JSON.
    
    Args:
        articles: List of raw article dictionaries
        output_dir: Directory to save the file
    
    Returns:
        Path to saved file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "raw_articles.json")
        
        output = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "total_articles": len(articles),
                "source": "NewsAPI"
            },
            "articles": articles
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        raise FileManagerError(f"Failed to save raw articles: {str(e)}")

def save_analysis_results(results: List[Dict], output_dir: str = "output") -> str:
    """
    Save LLM analysis results to JSON.
    
    Args:
        results: List of analysis results from LLM#1
        output_dir: Directory to save the file
    
    Returns:
        Path to saved file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "analysis_results.json")
        
        # Count sentiments
        sentiments = {}
        for r in results:
            if r.get("status") == "validated":
                analysis = r.get("analysis", "")
                # Try to extract sentiment from analysis
                if "SENTIMENT:" in analysis:
                    sentiment_line = [line for line in analysis.split('\n') if 'SENTIMENT:' in line]
                    if sentiment_line:
                        sentiment = sentiment_line[0].replace('SENTIMENT:', '').strip()
                        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        output = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_articles": len(results),
                "sentiment_breakdown": sentiments
            },
            "results": results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        raise FileManagerError(f"Failed to save analysis results: {str(e)}")

def save_final_report(results: List[Dict], output_dir: str = "output") -> str:
    """
    Save final markdown report with validation results.
    
    Args:
        results: List of validated results
        output_dir: Directory to save the file
    
    Returns:
        Path to saved file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "final_report.md")
        
        # Calculate statistics
        total = len(results)
        validated = sum(1 for r in results if r.get("status") == "validated")
        
        # Count sentiments from analyses
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        for r in results:
            if r.get("status") == "validated":
                analysis = r.get("analysis", "")
                if "Positive" in analysis:
                    sentiment_counts["Positive"] += 1
                elif "Negative" in analysis:
                    sentiment_counts["Negative"] += 1
                elif "Neutral" in analysis:
                    sentiment_counts["Neutral"] += 1
        
        # Build markdown content
        md_content = f"""# News Analysis Report

**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Articles Analyzed:** {validated}
**Source:** NewsAPI

---

## Summary

- **Positive:** {sentiment_counts["Positive"]} articles
- **Negative:** {sentiment_counts["Negative"]} articles
- **Neutral:** {sentiment_counts["Neutral"]} articles

---

## Detailed Analysis

"""
        
        article_num = 1
        for result in results:
            if result.get("status") != "validated":
                continue
                
            article = result.get("article", {})
            analysis = result.get("analysis", "")
            validation = result.get("validation", {})
            
            # Parse analysis into components
            gist = ""
            sentiment = ""
            tone = ""
            
            # More flexible parsing
            lines = analysis.split('\n')
            for i, line in enumerate(lines):
                line_upper = line.upper()
                if 'GIST' in line_upper and ':' in line:
                    gist = line.split(':', 1)[1].strip() if ':' in line else ""
                    # Check if gist continues on next line
                    if not gist and i + 1 < len(lines):
                        gist = lines[i + 1].strip()
                elif 'SENTIMENT' in line_upper and ':' in line:
                    sentiment = line.split(':', 1)[1].strip() if ':' in line else ""
                    if not sentiment and i + 1 < len(lines):
                        sentiment = lines[i + 1].strip()
                elif 'TONE' in line_upper and ':' in line:
                    tone = line.split(':', 1)[1].strip() if ':' in line else ""
                    if not tone and i + 1 < len(lines):
                        tone = lines[i + 1].strip()
            
            # Fallback: if still empty, use the full analysis
            if not gist and not sentiment and not tone:
                gist = analysis[:200] + "..." if len(analysis) > 200 else analysis
            
            # Validation verdict emoji
            verdict = validation.get("verdict", "unknown")
            verdict_symbol = {
                "correct": "✓",
                "partially_correct": "~",
                "incorrect": "✗"
            }.get(verdict, "?")
            
            validation_text = validation.get("overall_assessment", "No validation details")
            
            md_content += f"""### Article {article_num}: "{article.get('title', 'Untitled')}"

- **Source:** [{article.get('source', 'Unknown')}]({article.get('url', '#')})
- **Gist:** {gist}
- **LLM#1 Sentiment:** {sentiment}
- **LLM#2 Validation:** {verdict_symbol} {verdict.replace('_', ' ').title()}. {validation_text}
- **Tone:** {tone}

---

"""
            article_num += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
        
    except Exception as e:
        raise FileManagerError(f"Failed to save final report: {str(e)}")
