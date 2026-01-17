#!/usr/bin/env python3
"""
Mock Demo - Generates sample outputs for demonstration
This simulates what the pipeline would produce with a working API quota
"""

from src.news_fetcher import fetch_news
from src.file_manager import save_raw_articles, save_analysis_results, save_final_report
from src.utils import get_timestamp
import json

# Mock LLM responses (realistic examples based on news topics)
MOCK_ANALYSES = [
    {
        "analysis": """GIST: India's Election Commission announces dates for upcoming state assembly elections in five states.

SENTIMENT: Neutral

TONE: Analytical

KEY ENTITIES: Election Commission of India, five state assemblies, Chief Election Commissioner

WHY THIS MATTERS: These elections will serve as a crucial indicator of political sentiment ahead of the national elections, potentially shifting the balance of power in key regional governments."""
    },
    {
        "analysis": """GIST: Government launches new digital infrastructure initiative aimed at improving rural connectivity across India.

SENTIMENT: Positive

TONE: Optimistic

KEY ENTITIES: Ministry of Electronics and IT, rural India, digital infrastructure, broadband expansion

WHY THIS MATTERS: This initiative addresses the digital divide, potentially transforming rural access to education, healthcare, and economic opportunities through improved internet connectivity."""
    },
    {
        "analysis": """GIST: Opposition parties criticize government's handling of inflation, calling for immediate policy intervention.

SENTIMENT: Negative

TONE: Critical

KEY ENTITIES: Opposition coalition, Reserve Bank of India, inflation rate, economic policy

WHY THIS MATTERS: Rising inflation affects millions of citizens' purchasing power and could influence voter sentiment in upcoming elections, making it a critical political and economic issue."""
    },
]

MOCK_VALIDATIONS = [
    {
        "verdict": "correct",
        "confidence": 0.92,
        "issues": [],
        "strengths": [
            "Accurately summarizes the main announcement",
            "Correctly identifies neutral tone of official announcement",
            "Properly contextualizes political significance"
        ],
        "overall_assessment": "The analysis accurately captures the factual content and maintains objectivity appropriate for an official announcement."
    },
    {
        "verdict": "correct",
        "confidence": 0.88,
        "issues": [],
        "strengths": [
            "Identifies the positive development accurately",
            "Correctly assesses optimistic tone",
            "Highlights meaningful societal impact"
        ],
        "overall_assessment": "Analysis correctly identifies the positive nature of the initiative and its potential benefits."
    },
    {
        "verdict": "partially_correct",
        "confidence": 0.75,
        "issues": [
            "Could provide more specific data on inflation rates",
            "Sentiment classification is slightly subjective"
        ],
        "strengths": [
            "Captures the critical tone of opposition statements",
            "Identifies key political actors correctly"
        ],
        "overall_assessment": "Generally accurate but could benefit from more specific economic data to support the sentiment classification."
    },
]

def generate_mock_demo():
    """Generate mock demonstration outputs"""
    print("=" * 70)
    print("GENERATING MOCK DEMONSTRATION OUTPUTS")
    print("=" * 70)
    print()
    
    # Fetch real articles
    print("📰 Fetching real articles from NewsAPI...")
    articles = fetch_news()[:3]  # Take first 3
    print(f"✅ Fetched {len(articles)} articles\n")
    
    # Save raw articles
    raw_path = save_raw_articles(articles)
    print(f"💾 Saved raw articles: {raw_path}\n")
    
    # Create mock results
    print("🤖 Generating mock analysis results...")
    results = []
    
    for i, article in enumerate(articles):
        result = {
            "article": article,
            "analysis": MOCK_ANALYSES[i]["analysis"],
            "validation": MOCK_VALIDATIONS[i],
            "timestamp": get_timestamp(),
            "status": "validated"
        }
        result["validation"]["validated_at"] = get_timestamp()
        result["validation"]["article_title"] = article.get("title")
        results.append(result)
    
    print(f"✅ Generated {len(results)} mock analyses\n")
    
    # Save results
    print("💾 Saving outputs...")
    analysis_path = save_analysis_results(results)
    print(f"✅ Analysis results: {analysis_path}")
    
    report_path = save_final_report(results)
    print(f"✅ Final report: {report_path}")
    
    print("\n" + "=" * 70)
    print("MOCK DEMO COMPLETE")
    print("=" * 70)
    print("\nNOTE: This uses mock LLM responses to demonstrate the pipeline.")
    print("In production with API quota, real Gemini analysis would be used.")
    print("\n📁 Check output/ folder for generated files:")
    print("  - raw_articles.json")
    print("  - analysis_results.json")
    print("  - final_report.md")
    print("=" * 70)

if __name__ == "__main__":
    generate_mock_demo()
