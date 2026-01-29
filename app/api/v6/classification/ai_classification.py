from fastapi import APIRouter, UploadFile, File, HTTPException
from app.llm.ai_api import classify_b64_file
from app.utils import pdf264
from app.services import s_file_system
import base64
import os

router = APIRouter()

@router.post("/classify")
async def classify_document(file: UploadFile = File(...)):
    try:
        # Save the uploaded file using your existing helper
        file_name, file_folder = await s_file_system.save_upload_file(file)
        file_path = os.path.join(file_folder, file_name)

        # Convert to base64 for OpenAI
        if file_name.lower().endswith('.pdf'):
            b64_file = pdf264.pdf_to_one_b64(file_path)
        else:
            with open(file_path, "rb") as f:
                b64_file = base64.b64encode(f.read()).decode('utf-8')

        # Optionally, clean up the file after processing
        os.remove(file_path)

        classification = classify_b64_file(b64_file)
        return {"classification": classification.strip().lower()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI classification failed: {str(e)}")