from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class LLMValidationError(Exception):
    pass

def validate_analysis(article: dict, analysis: dict) -> dict:
    """
    Validates the LLM analysis output for accuracy and quality.
    
    Args:
        article: Original article dict with title, description, content
        analysis: Analysis dict from llm_analyzer
    
    Returns:
        dict with verdict, confidence, and issues found
    """
    prompt = f"""
You are a validation expert. Your job is to validate whether an AI-generated analysis is accurate and high-quality.

ORIGINAL ARTICLE:
Title: {article.get("title")}
Description: {article.get("description")}
Content: {article.get("content")}

AI ANALYSIS TO VALIDATE:
{analysis.get("analysis")}

VALIDATION TASK:
1. Check if the summary accurately reflects the article content
2. Verify the sentiment classification is appropriate
3. Confirm key entities are correctly identified
4. Assess if "why this matters" is reasonable and insightful

Respond ONLY with a JSON object in this exact format:
{{
  "verdict": "correct|partially_correct|incorrect",
  "confidence": 0.0-1.0,
  "issues": ["list of specific issues found, or empty array if none"],
  "strengths": ["list of what the analysis did well"],
  "overall_assessment": "brief overall evaluation"
}}

Do not include any text before or after the JSON.
"""
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
            ),
        )
        
        # Extract and parse JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        validation_result = json.loads(response_text.strip())
        
        # Add metadata
        validation_result["article_title"] = article.get("title")
        validation_result["validated_at"] = None  # Will be added by main.py
        
        return validation_result
        
    except json.JSONDecodeError as e:
        raise LLMValidationError(f"Failed to parse validation response as JSON: {e}\nResponse: {response.text}")
    except Exception as e:
        raise LLMValidationError(f"Validation failed: {str(e)}")
