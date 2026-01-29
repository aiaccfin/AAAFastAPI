from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
import os, uuid, pytesseract

from pdf2image import convert_from_path

router = APIRouter()
@router.get("/test")
def root(): return {"OCR": "IMG"}

@router.post("/tesserat")
async def pdf_to_text_tesseract(oUploadFile: UploadFile = File(...)):
    try:
        # Define temp paths
        tmp_dir = "./tmp/pdf_img"
        os.makedirs(tmp_dir, exist_ok=True)

        pdf_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{oUploadFile.filename}")
        with open(pdf_path, "wb") as f:
            f.write(await oUploadFile.read())

        # Convert PDF pages to images
        images = convert_from_path(pdf_path)

        # Run OCR on each page
        extracted_text = ""
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            extracted_text += f"\n\n--- Page {i + 1} ---\n{text}"

        # Clean up
        os.remove(pdf_path)

        return {"text": extracted_text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/tesserat_w_confidence_score")
async def pdf_to_text_with_confidence(oUploadFile: UploadFile = File(...)):
    try:
        # Setup
        tmp_dir = "./tmp/pdf_img"
        os.makedirs(tmp_dir, exist_ok=True)
        pdf_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{oUploadFile.filename}")

        # Save uploaded PDF
        with open(pdf_path, "wb") as f:
            f.write(await oUploadFile.read())

        # Convert PDF to images
        images = convert_from_path(pdf_path)

        result = []

        for page_num, img in enumerate(images, start=1):
            # OCR with data
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)

            # Drop rows where no text was detected
            ocr_data = ocr_data.dropna(subset=["text"])

            page_results = []
            for _, row in ocr_data.iterrows():
                word_info = {
                    "text": row["text"],
                    "conf": float(row["conf"]),
                }
                page_results.append(word_info)

            result.append({
                "page": page_num,
                "words": page_results
            })

        # Cleanup
        os.remove(pdf_path)

        return {"ocr_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
