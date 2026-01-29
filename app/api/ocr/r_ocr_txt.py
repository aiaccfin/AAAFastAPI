import os, openai, json
import dotenv
CFG = dotenv.dotenv_values(".env")

client = openai.OpenAI(api_key = CFG['OPENAI_API_KEY'])
model = "gpt-4o"

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.utils.u_ghost_script import convert_text_pdf
from app.llm.ai_api import txtpdf_json
router = APIRouter()

@router.get("/test")
def root(): return {"OCR": "Text"}


@router.post("/txt_pdf_bankstatement")
async def pdf_to_text_ghostscript(pdf: UploadFile = File(...)):
    try:
        # Define temporary paths
        input_pdf_path = f"./tmp/pdf_text/{pdf.filename}"
        output_dir = "./tmp/pdf_text"
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded PDF temporarily
        with open(input_pdf_path, "wb") as f:
            f.write(await pdf.read())

        # Convert PDF to text using your Ghostscript function
        output_text_path = convert_text_pdf(input_pdf_path, output_dir)

        # Read the resulting text file
        with open(output_text_path, "r") as f:
            extracted_text = f.read()

        # Cleanup temporary files
        # os.remove(input_pdf_path)
        # os.remove(output_text_path)

        return {"text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/txt_pdf_json")
async def txtpdf_to_json(pdf: UploadFile = File(...)):
    try:
        # Define temporary paths
        input_pdf_path = f"./tmp/pdf_text/{pdf.filename}"
        output_dir = "./tmp/pdf_text"
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded PDF temporarily
        with open(input_pdf_path, "wb") as f:
            f.write(await pdf.read())

        # Convert PDF to text using your Ghostscript function
        output_text_path = convert_text_pdf(input_pdf_path, output_dir)

        # Read the resulting text file
        with open(output_text_path, "r") as f:
            extracted_text = f.read()

        json_result = txtpdf_json(extracted_text)
        # response = client.chat.completions.create(
        #     model=model,
        #     response_format={ "type": "json_object" },
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a tool that converts plain text into JSON format."
        #         },
        #         {
        #             "role": "user",
        #             "content": extracted_text
        #         }
        #     ]
        # )
        # json_result = response.choices[0].message.content
        output_filename = os.path.join(output_dir, os.path.basename(input_pdf_path).replace('.pdf', '_ai.json'))
        
        # Save the entire_invoice list as a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=4)
        
        return {"text": json_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))