import json
import os
from datetime import datetime
from typing import List, Dict

class ReportWriterError(Exception):
    pass

def save_json_report(results: List[Dict], output_dir: str = "output") -> str:
    """
    Save analysis results as JSON file.
    
    Args:
        results: List of analysis results
        output_dir: Directory to save the report
    
    Returns:
        Path to saved JSON file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Create structured output
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_articles": len(results),
                "correct_analyses": sum(1 for r in results if r.get("validation", {}).get("verdict") == "correct"),
                "partially_correct": sum(1 for r in results if r.get("validation", {}).get("verdict") == "partially_correct"),
                "incorrect_analyses": sum(1 for r in results if r.get("validation", {}).get("verdict") == "incorrect"),
            },
            "results": results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        raise ReportWriterError(f"Failed to save JSON report: {str(e)}")

def save_markdown_report(results: List[Dict], output_dir: str = "output") -> str:
    """
    Save analysis results as human-readable Markdown report.
    
    Args:
        results: List of analysis results
        output_dir: Directory to save the report
    
    Returns:
        Path to saved Markdown file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Calculate statistics
        total = len(results)
        correct = sum(1 for r in results if r.get("validation", {}).get("verdict") == "correct")
        partial = sum(1 for r in results if r.get("validation", {}).get("verdict") == "partially_correct")
        incorrect = sum(1 for r in results if r.get("validation", {}).get("verdict") == "incorrect")
        
        # Avoid division by zero
        if total == 0:
            total = 1
        
        # Build markdown content
        md_content = f"""# News Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Summary Statistics

- **Total Articles Analyzed:** {total}
- **Correct Analyses:** {correct} ({correct/total*100:.1f}%)
- **Partially Correct:** {partial} ({partial/total*100:.1f}%)
- **Incorrect Analyses:** {incorrect} ({incorrect/total*100:.1f}%)

---

## Detailed Results

"""
        
        for i, result in enumerate(results, 1):
            article = result.get("article", {})
            analysis = result.get("analysis", "No analysis available")
            validation = result.get("validation", {})
            
            verdict = validation.get("verdict", "unknown")
            confidence = validation.get("confidence", 0)
            issues = validation.get("issues", [])
            strengths = validation.get("strengths", [])
            
            # Verdict emoji
            verdict_emoji = {
                "correct": "✅",
                "partially_correct": "⚠️",
                "incorrect": "❌"
            }.get(verdict, "❓")
            
            md_content += f"""### {i}. {article.get('title', 'Untitled')}

**Validation:** {verdict_emoji} {verdict.upper()} (Confidence: {confidence:.2f})

**Source:** [{article.get('source', {}).get('name', 'Unknown')}]({article.get('url', '#')})

**Published:** {article.get('publishedAt', 'Unknown')}

#### Analysis
{analysis}

#### Validation Results

"""
            
            if strengths:
                md_content += "**Strengths:**\n"
                for strength in strengths:
                    md_content += f"- {strength}\n"
                md_content += "\n"
            
            if issues:
                md_content += "**Issues Found:**\n"
                for issue in issues:
                    md_content += f"- {issue}\n"
                md_content += "\n"
            
            if validation.get("overall_assessment"):
                md_content += f"**Overall Assessment:** {validation.get('overall_assessment')}\n"
            
            md_content += "\n---\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
        
    except Exception as e:
        raise ReportWriterError(f"Failed to save Markdown report: {str(e)}")
