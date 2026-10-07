from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from core.ingest import file_to_text
from core.pipeline import check_text

router = APIRouter()


@router.post("/check-file")
async def check_file(file: UploadFile = File(...), lang: Optional[str] = Form(None)):
    data = await file.read()
    try:
        text = await file_to_text(data, file.content_type or "", file.filename or "file")
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except Exception as e:
        print("ingest error:", e)
        raise HTTPException(status_code=503, detail="The AI service is busy. Please try again in a minute.")
    if not text:
        raise HTTPException(status_code=422, detail="Could not read any text from this file")
    result = await check_text(text, lang)
    result["extracted_text"] = text
    return result
