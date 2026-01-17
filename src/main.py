#!/usr/bin/env python3
"""
News Analyzer - Main Pipeline
Fetches news → Analyzes with LLM#1 → Validates with LLM#2 → Saves reports
"""

from src.news_fetcher import fetch_news, NewsFetcherError
from src.llm_analyzer import analyze_article, LLMAnalysisError
from src.llm_validator import validate_analysis, LLMValidationError
from src.file_manager import save_raw_articles, save_analysis_results, save_final_report, FileManagerError
from src.utils import get_timestamp, print_progress, validate_article
import sys
import time

def main():
    """Main pipeline execution."""
    print("=" * 70)
    print("NEWS ANALYZER - Dual LLM Analysis & Validation Pipeline")
    print("=" * 70)
    print()
    
    results = []
    articles = []
    
    try:
        # Step 1: Fetch News
        print("📰 Step 1: Fetching news articles...")
        articles = fetch_news()
        print(f"✅ Successfully fetched {len(articles)} articles\n")
        
        if not articles:
            print("⚠️  No articles found. Exiting.")
            return
        
        # Save raw articles
        try:
            raw_path = save_raw_articles(articles)
            print(f"💾 Raw articles saved: {raw_path}\n")
        except FileManagerError as e:
            print(f"⚠️  Warning: Could not save raw articles: {str(e)}\n")
        
        # Step 2: Analyze with LLM#1 (Gemini)
        print("🤖 Step 2: Analyzing articles with LLM#1 (Gemini)...")
        print()
        
        for idx, article in enumerate(articles, 1):
            print_progress(idx - 1, len(articles), f"Analyzing {idx}/{len(articles)}")
            
            # Validate article has required fields
            if not validate_article(article):
                print(f"\n⚠️  Skipping article {idx}: Missing required fields")
                continue
            
            result = {
                "article": article,
                "analysis": None,
                "validation": None,
                "timestamp": get_timestamp(),
                "status": "pending"
            }
            
            try:
                # Analyze with LLM#1
                analysis = analyze_article(article)
                result["analysis"] = analysis.get("analysis")
                result["status"] = "analyzed"
                
                # Add delay to avoid rate limits (5 req/min = 12 sec between requests)
                time.sleep(13)
                
            except LLMAnalysisError as e:
                print(f"\n❌ Analysis failed for article {idx}: {str(e)}")
                result["status"] = "analysis_failed"
                result["error"] = str(e)
            
            results.append(result)
        
        print_progress(len(articles), len(articles), "Analysis complete!")
        print()
        
        # Step 3: Validate with LLM#2 (Gemini with different prompt)
        print("\n🔍 Step 3: Validating analyses with LLM#2 (Gemini Validator)...")
        print()
        
        validated_count = 0
        for idx, result in enumerate(results, 1):
            if result["status"] != "analyzed":
                continue
                
            print_progress(idx - 1, len(results), f"Validating {idx}/{len(results)}")
            
            try:
                validation = validate_analysis(result["article"], {"analysis": result["analysis"]})
                validation["validated_at"] = get_timestamp()
                result["validation"] = validation
                result["status"] = "validated"
                validated_count += 1
                
                # Add delay to avoid rate limits
                time.sleep(13)
                
            except LLMValidationError as e:
                print(f"\n⚠️  Validation failed for article {idx}: {str(e)}")
                result["status"] = "validation_failed"
                result["error"] = str(e)
        
        print_progress(len(results), len(results), "Validation complete!")
        print()
        
        # Step 4: Save Results
        print("\n💾 Step 4: Saving results...")
        
        try:
            # Save analysis results (JSON)
            analysis_path = save_analysis_results(results)
            print(f"✅ Analysis results saved: {analysis_path}")
            
            # Save final report (Markdown)
            report_path = save_final_report(results)
            print(f"✅ Final report saved: {report_path}")
            
        except FileManagerError as e:
            print(f"❌ Failed to save results: {str(e)}")
            return
        
        # Step 5: Summary
        print("\n" + "=" * 70)
        print("PIPELINE SUMMARY")
        print("=" * 70)
        
        total = len(results)
        analyzed = sum(1 for r in results if r["status"] in ["analyzed", "validated"])
        validated = sum(1 for r in results if r["status"] == "validated")
        
        correct = sum(1 for r in results if r.get("validation") and r["validation"].get("verdict") == "correct")
        partial = sum(1 for r in results if r.get("validation") and r["validation"].get("verdict") == "partially_correct")
        incorrect = sum(1 for r in results if r.get("validation") and r["validation"].get("verdict") == "incorrect")
        
        print(f"📊 Total Articles Fetched: {len(articles)}")
        print(f"✅ Successfully Analyzed (LLM#1): {analyzed}")
        print(f"✅ Successfully Validated (LLM#2): {validated}")
        print()
        print("Validation Results:")
        print(f"  ✓ Correct: {correct}")
        print(f"  ~ Partially Correct: {partial}")
        print(f"  ✗ Incorrect: {incorrect}")
        print()
        print("📁 Output Files:")
        print(f"  - output/raw_articles.json")
        print(f"  - output/analysis_results.json")
        print(f"  - output/final_report.md")
        print()
        print("✅ Pipeline completed successfully!")
        print("=" * 70)
        
    except NewsFetcherError as e:
        print(f"❌ Failed to fetch news: {str(e)}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
