"""
Module for generating Hebrew keywords for stocks and finance industry using Gemini AI
"""
import json
import google.generativeai as genai
from src.config import KEYWORDS_PER_GENERATION, INDUSTRY_FOCUS, LANGUAGE, GEMINI_MODEL


async def generate_keywords_from_gemini(gemini_api_key: str, num_keywords: int = KEYWORDS_PER_GENERATION) -> list:
    """
    Generate relevant Hebrew keywords for the stocks and finance industry using Gemini AI.

    Args:
        gemini_api_key: API key for Gemini
        num_keywords: Number of keywords to generate

    Returns:
        List of keyword dictionaries with 'keyword' and 'category' fields
    """
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Construct prompt for keyword generation
        prompt = f"""
        You are an expert in financial markets and Hebrew language. Generate {num_keywords} relevant Hebrew keywords
        related to the {INDUSTRY_FOCUS} industry.

        The keywords should cover various aspects such as:
        - Stock market terms (e.g., מניות, מדדים, תיק השקעות)
        - Financial instruments (e.g., אג"ח, אופציות, חוזים עתידיים)
        - Trading concepts (e.g., רווח הון, דיבידנד, תשואה)
        - Market analysis (e.g., ניתוח טכני, יחס מחיר רווח, תנודתיות)
        - Economic indicators (e.g., ריבית, אינפלציה, תמ"ג)
        - Investment strategies (e.g., גיוון, השקעה פאסיבית, מסחר יומי)

        Requirements:
        1. Keywords must be in {LANGUAGE}
        2. Include a mix of basic and advanced financial terms
        3. Each keyword should be commonly used in financial discussions
        4. Categorize each keyword (e.g., "trading", "analysis", "instruments", "strategy", "economic_indicators")

        Please provide your answer in JSON format as an array of objects, where each object has:
        - "keyword": the Hebrew keyword
        - "category": the category it belongs to
        - "description": brief explanation in Hebrew

        Example format:
        [
            {{"keyword": "מניות", "category": "instruments", "description": "ני"ע המייצגים בעלות חלקית בחברה"}},
            {{"keyword": "תשואה", "category": "trading", "description": "הרווח או ההפסד מהשקעה"}},
            ...
        ]

        Generate exactly {num_keywords} keywords.
        """

        print(f"Requesting {num_keywords} keywords from Gemini...")
        response = model.generate_content(prompt)

        # Parse the response
        keywords = parse_gemini_response(response)

        if keywords:
            print(f"Successfully generated {len(keywords)} keywords")
            return keywords
        else:
            print("No keywords were generated")
            return []

    except Exception as e:
        print(f"Error generating keywords from Gemini: {e}")
        return []


def parse_gemini_response(response) -> list:
    """
    Parse Gemini API response and extract keywords.

    Args:
        response: Gemini API response object

    Returns:
        List of keyword dictionaries
    """
    try:
        # Clean the response text
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Remove opening ```json or ```
            response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text[3:]
            # Remove closing ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        keywords = json.loads(response_text)

        if not isinstance(keywords, list):
            print(f"Unexpected response format: expected list, got {type(keywords)}")
            return []

        # Validate each keyword has required fields
        validated_keywords = []
        for kw in keywords:
            if isinstance(kw, dict) and 'keyword' in kw and 'category' in kw:
                validated_keywords.append({
                    'keyword': kw['keyword'],
                    'category': kw.get('category', 'general'),
                    'description': kw.get('description', '')
                })
            else:
                print(f"Skipping invalid keyword entry: {kw}")

        return validated_keywords

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini response: {e}")
        print(f"Response text: {response.text[:500]}...")  # Print first 500 chars for debugging
        return []
    except AttributeError as e:
        print(f"Error accessing response text: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error parsing Gemini response: {e}")
        return []
