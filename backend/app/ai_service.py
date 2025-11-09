import os
import json
import google.generativeai as genai
from typing import Dict, Any

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

TITANIC_COLUMNS = {
    'PassengerId': 'Unique identifier',
    'Survived': 'Survival (0 = No, 1 = Yes)',
    'Pclass': 'Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)',
    'Name': 'Passenger name',
    'Sex': 'Gender',
    'Age': 'Age in years',
    'SibSp': 'Number of siblings/spouses aboard',
    'Parch': 'Number of parents/children aboard',
    'Ticket': 'Ticket number',
    'Fare': 'Passenger fare',
    'Cabin': 'Cabin number',
    'Embarked': 'Port of embarkation'
}

def plan_from_llm(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analysis plan specifically for Titanic dataset"""
    q = question.lower()
    
    # Direct pattern matching for survival rate by gender
    if ("gender" in q or "sex" in q) and ("survival" in q or "survived" in q):
        return {
            "op": "compare",
            "column": "Survived",
            "by": "Sex",
            "description": "survival rate by gender"
        }
    
    # Handle embarkation questions
    if "embarked" in q or "embarkation" in q:
        if "southampton" in q:
            return {
                "op": "count",
                "filter": "Embarked == 'S'"
            }
        elif "cherbourg" in q:
            return {
                "op": "count",
                "filter": "Embarked == 'C'"
            }
        elif "queenstown" in q:
            return {
                "op": "count",
                "filter": "Embarked == 'Q'"
            }
    
    # Common Titanic dataset questions
    if "survived" in q:
        if "percentage" in q or "survival rate" in q:
            if "class" in q:
                return {
                    "op": "compare",
                    "column": "Survived",
                    "by": "Pclass"
                }
            elif "gender" in q or "sex" in q:
                return {
                    "op": "compare",
                    "column": "Survived",
                    "by": "Sex"
                }
            else:
                return {
                    "op": "percentage",
                    "filter": "Survived == 1"
                }
    
    if "average age" in q:
        if "survived" in q:
            return {
                "op": "aggregate",
                "aggregations": [{"column": "Age", "func": "mean"}],
                "filter": "Survived == 1"
            }
        else:
            return {
                "op": "aggregate",
                "aggregations": [{"column": "Age", "func": "mean"}]
            }
    
    if "first class" in q or "class 1" in q:
        return {
            "op": "count",
            "filter": "Pclass == 1"
        }
        
    if "female" in q:
        if "first class" in q:
            return {
                "op": "count",
                "filter": "Sex == 'female' and Pclass == 1"
            }
        else:
            return {
                "op": "percentage",
                "filter": "Sex == 'female'"
            }

    # Use Gemini for other questions
    try:
        prompt = f"""Analyze this Titanic dataset question: "{question}"

Available columns:
{', '.join(f'{k}: {v}' for k, v in TITANIC_COLUMNS.items())}

Generate a JSON query plan using these patterns:
1. Count: {{"op": "count", "filter": "Column == value"}}
2. Percentage: {{"op": "percentage", "filter": "Column == value"}}
3. Average: {{"op": "aggregate", "aggregations": [{{"column": "Column", "func": "mean"}}]}}
4. Compare: {{"op": "compare", "column": "target", "by": "group"}}

Return ONLY the JSON plan."""

        response = model.generate_content(prompt)
        if response and response.text:
            plan = safe_json_loads(response.text)
            if plan and isinstance(plan, dict) and "op" in plan:
                return plan
                
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return {
        "op": "clarify",
        "question": "Could you rephrase your question? Try asking about passenger survival rates, ages, or class distribution."
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