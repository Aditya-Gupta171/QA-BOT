from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import hashlib

from app.data_handler import load_file_to_df, dataset_summary
from app.ai_service import plan_from_llm
from app.query_executor import execute_plan

router = APIRouter()

def save_temp_file(content: bytes, filename: str) -> str:
    """Save uploaded content to temp file and return path"""
    temp_dir = tempfile.gettempdir()
    upload_dir = os.path.join(temp_dir, "qa_bot_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_hash = hashlib.md5(content).hexdigest()[:10]
    file_extension = os.path.splitext(filename)[1]
    temp_path = os.path.join(upload_dir, f"{file_hash}{file_extension}")
    
    with open(temp_path, 'wb') as f:
        f.write(content)
    
    return temp_path

@router.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        temp_path = save_temp_file(content, file.filename)
        
        df, meta = load_file_to_df(temp_path)
        summary = dataset_summary(df, meta)
        
        plan = plan_from_llm(question=question, schema=summary)
        if not plan:
            raise HTTPException(status_code=500, detail="Failed to generate analysis plan")
        
        result = execute_plan(plan, df)
        
        return JSONResponse(content={
            "question": question,
            "answer": result.get("answer"),
            "explanation": result.get("explain"),
            "analysis_type": result.get("type", "unknown"),
            "dataset_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "file_type": meta.get("type", "unknown")
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass