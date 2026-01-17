from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class LLMAnalysisError(Exception):
    pass

def analyze_article(article: dict) -> dict:
    prompt = f"""
You are a news intelligence analyst.
Analyze the following news article and return:
1. A concise summary (3–4 sentences)
2. Sentiment (Positive / Negative / Neutral)
3. Key entities mentioned
4. Why this news matters

Article:
Title: {article.get("title")}
Description: {article.get("description")}
Content: {article.get("content")}
"""
    try:
        # Try different model name formats
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",  # Try with full path
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=512,
            ),
        )
        return {
            "title": article.get("title"),
            "analysis": response.text,
        }
    except Exception as e:
        raise LLMAnalysisError(str(e))
