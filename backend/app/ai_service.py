import os
import json
import google.generativeai as genai
from typing import Dict, Any

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def _build_prompt(question: str, schema: Dict[str, Any]) -> str:
    """Build focused prompt for common dataset questions"""
    cols = [c["name"] for c in schema["columns"]]
    sample = json.dumps(schema["sample_rows"][:1], indent=2)
    
    return f"""Analyze this dataset with columns: {cols}
Sample: {sample}

Question: {question}

Return a JSON query plan using ONLY these patterns:
1. For counting with conditions: {{"op": "count", "filter": "Column == value"}}
2. For percentages: {{"op": "percentage", "filter": "Column == value"}}
3. For averages: {{"op": "aggregate", "aggregations": [{{"column": "Column", "func": "mean"}}]}}
4. For comparisons: {{"op": "compare", "column": "target", "by": "group"}}

Examples:
- "Average age of survivors": {{"op": "aggregate", "aggregations": [{{"column": "Age", "func": "mean"}}], "filter": "Survived == 1"}}
- "Count first class": {{"op": "count", "filter": "Pclass == 1"}}
- "Survival rate by gender": {{"op": "compare", "column": "Survived", "by": "Sex"}}
- "Percentage survived": {{"op": "percentage", "filter": "Survived == 1"}}

Return ONLY the JSON plan."""

def plan_from_llm(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analysis plan"""
    q = question.lower()
    
    if "survived" in q and "percentage" in q:
        return {
            "op": "percentage",
            "filter": "Survived == 1"
        }
    
    if "first class" in q or "class 1" in q:
        return {
            "op": "count",
            "filter": "Pclass == 1"
        }
        
    if "average age" in q and "survived" in q:
        return {
            "op": "aggregate",
            "aggregations": [{"column": "Age", "func": "mean"}],
            "filter": "Survived == 1"
        }
        
    if "survival rate" in q and "gender" in q:
        return {
            "op": "compare",
            "column": "Survived",
            "by": "Sex"
        }
    
    try:
        prompt = _build_prompt(question, schema)
        response = model.generate_content(prompt)
        
        if response and response.text:
            plan = safe_json_loads(response.text)
            if plan and isinstance(plan, dict) and "op" in plan:
                return plan
                
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return {
        "op": "clarify",
        "question": "Could you rephrase your question? Try asking about passenger counts, survival rates, or average age."
    }

def safe_json_loads(text: str) -> Dict[str, Any]:
    """Safely parse JSON from text"""
    try:
        return json.loads(text)
    except:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
    return None