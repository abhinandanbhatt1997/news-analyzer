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
Analyze the following news article and provide:

1. **Gist**: A concise 1-2 sentence summary of the main news
2. **Sentiment**: Classify as Positive, Negative, or Neutral
3. **Tone**: Identify the tone (choose one: urgent, analytical, satirical, balanced, alarming, optimistic, critical, neutral)
4. **Key Entities**: List important people, organizations, or locations mentioned
5. **Why This Matters**: Brief explanation of significance

Article:
Title: {article.get("title")}
Description: {article.get("description", "N/A")}
Content: {article.get("content")}

Format your response clearly with these exact headings:
GIST:
SENTIMENT:
TONE:
KEY ENTITIES:
WHY THIS MATTERS:
"""
    try:
        response = client.models.generate_content(
            model="models/gemini-2.0-flash",  # ✅ Updated to available model
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
