import pandas as pd
from typing import Dict, Any

def execute_plan(plan: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
    """Execute the analysis plan on the dataframe"""
    try:
        op = plan.get("op", "").lower()
        
        if op == "count":
            return _execute_count(df, plan)
        elif op == "percentage":
            return _execute_percentage(df, plan)
        elif op == "aggregate":
            return _execute_aggregate(df, plan)
        elif op == "compare":
            return _execute_compare(df, plan)
        else:
            return {
                "answer": None,
                "explain": f"Unsupported operation: {op}",
                "plan_used": plan
            }
            
    except Exception as e:
        return {
            "answer": None,
            "explain": f"Error executing plan: {str(e)}",
            "plan_used": plan
        }

def _execute_count(df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Execute count operation with filter"""
    filter_str = plan.get("filter", "")
    
    try:
        if filter_str:
            # Handle string values in filter
            if "Embarked" in filter_str:
                # Replace 'Southampton' with 'S', 'Cherbourg' with 'C', 'Queenstown' with 'Q'
                if "Southampton" in filter_str:
                    filter_str = filter_str.replace("Southampton", "'S'")
                elif "Cherbourg" in filter_str:
                    filter_str = filter_str.replace("Cherbourg", "'C'")
                elif "Queenstown" in filter_str:
                    filter_str = filter_str.replace("Queenstown", "'Q'")
            
            filtered_df = df.query(filter_str)
            count = len(filtered_df)
            return {
                "answer": count,
                "explain": f"Count of records matching: {filter_str}",
                "plan_used": plan
            }
        else:
            return {
                "answer": len(df),
                "explain": "Total number of records",
                "plan_used": plan
            }
    except Exception as e:
        return {
            "answer": None,
            "explain": f"Error in count operation: {str(e)}",
            "plan_used": plan
        }

def _execute_percentage(df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Execute percentage calculation"""
    filter_str = plan.get("filter", "")
    try:
        if filter_str:
            total = len(df)
            filtered = len(df.query(filter_str))
            percentage = (filtered / total) * 100
            return {
                "answer": round(percentage, 2),
                "explain": f"Percentage of records matching {filter_str}: {round(percentage, 2)}%",
                "plan_used": plan
            }
    except Exception as e:
        return {
            "answer": None,
            "explain": f"Error calculating percentage: {str(e)}",
            "plan_used": plan
        }

def _execute_aggregate(df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Execute aggregation operations"""
    aggs = plan.get("aggregations", [])
    filter_str = plan.get("filter", "")
    
    try:
        if filter_str:
            df = df.query(filter_str)
            
        results = {}
        for agg in aggs:
            col = agg["column"]
            func = agg["func"]
            val = df[col].agg(func)
            results[f"{col}_{func}"] = round(float(val), 2)
            
        return {
            "answer": results,
            "explain": f"Calculated {func} for {col}" + (f" where {filter_str}" if filter_str else ""),
            "plan_used": plan
        }
    except Exception as e:
        return {
            "answer": None,
            "explain": f"Error in aggregation: {str(e)}",
            "plan_used": plan
        }

def _execute_compare(df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Execute comparison between groups"""
    try:
        target_col = plan.get("column")
        group_col = plan.get("by")
        
        if not (target_col and group_col):
            return {
                "answer": None,
                "explain": "Missing column specifications for comparison"
            }
        
        # Calculate survival rates by group
        grouped = df.groupby(group_col)[target_col].mean() * 100
        result = grouped.round(2).to_dict()
        
        # Format the explanation
        rates = [f"{group}: {rate:.2f}%" for group, rate in result.items()]
        explanation = f"Survival rates by {group_col}: " + ", ".join(rates)
        
        # Determine which group had higher rate
        highest_group = max(result.items(), key=lambda x: x[1])
        answer = f"{highest_group[0]} had the highest survival rate at {highest_group[1]:.2f}%"
        
        return {
            "answer": answer,
            "explain": explanation,
            "plan_used": plan
        }
        
    except Exception as e:
        return {
            "answer": None,
            "explain": f"Error in comparison: {str(e)}"
        }