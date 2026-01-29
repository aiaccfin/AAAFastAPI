from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
import os

from app.services   import s_ocr
from app.utils import pdf264

router = APIRouter()
@router.get("/test")
def root(): return {"OCR": "IMG"}

@router.post("/img_pdf_bankstatement")
async def pdf_to_text_ghostscript(oUploadFile: UploadFile = File(...)):
    try:
        # Define temporary paths
        in_file_name= f"./tmp/pdf_img/{oUploadFile.filename}"
        out_folder  = f"./tmp/pdf_img"
        os.makedirs(out_folder, exist_ok=True)

        # Save uploaded PDF temporarily
        with open(in_file_name, "wb") as f:
            f.write(await oUploadFile.read())

        # Convert PDF to text using your Ghostscript function
        base64_images= pdf264.pdf_to_base64_images(in_file_name)
        output_json  = s_ocr.img2json(base64_images, in_file_name, out_folder)

        # Read the resulting text file
        with open(output_json, "r") as f:
            extracted_text = f.read()

        # Cleanup temporary files
        # os.remove(in_file_name)
        # os.remove(output_text_path)

        return {"text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))