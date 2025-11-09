import pandas as pd
import sqlite3
import os
from typing import Tuple, Dict, Any

def load_file_to_df(path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load CSV or SQLite file into DataFrame"""
    lower = path.lower()
    
    if lower.endswith(".csv"):
        df = pd.read_csv(path)
        meta = {"type": "csv", "filename": os.path.basename(path)}
        return df, meta

    elif lower.endswith(".sqlite") or lower.endswith(".db"):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        meta = {"type": "sqlite", "tables": tables}
        
        if not tables:
            conn.close()
            raise ValueError("No user tables found in SQLite file")
        
        table = tables[0]
        df = pd.read_sql_query(f"SELECT * FROM '{table}' LIMIT 5000;", conn)
        meta["selected_table"] = table
        
        conn.close()
        return df, meta

    else:
        raise ValueError("Unsupported file type. Please upload CSV or SQLite (.db/.sqlite)")

def dataset_summary(df: pd.DataFrame, meta: Dict[str, Any]) -> Dict[str, Any]:
    """Create dataset summary"""
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        is_numeric = dtype in ['int64', 'float64']
        is_categorical = dtype == 'object' or (is_numeric and df[col].nunique() < 10)
        
        columns.append({
            "name": col,
            "dtype": dtype,
            "is_numeric": is_numeric,
            "is_categorical": is_categorical,
            "unique_values": df[col].nunique(),
            "missing_values": df[col].isnull().sum()
        })
    
    return {
        "meta": meta,
        "columns": columns,
        "sample_rows": df.head(2).fillna("").to_dict('records'),
        "n_rows": len(df),
        "column_names": list(df.columns)
    }