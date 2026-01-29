import os, json, pytesseract  
import subprocess, platform
from fastapi import UploadFile, HTTPException
from PyPDF2  import PdfReader
from pymongo import MongoClient

from app.config import settings
from app.llm   import ai_receipt
from app.utils import pdf264

def inv_imgpdf(in_file_name: str, out_folder: str):
    try:
        # Convert PDF to text using your Ghostscript function
        b64_image   = pdf264.pdf_to_one_b64(in_file_name)
        ai_res = inv_b64_one_2_json(b64_image, in_file_name, out_folder)
        
        print(f"Parsed ai_res JSON: {ai_res}")
        return ai_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def inv_textpdf(oUploadFile: UploadFile, pdf_name, pdf_folder):
    pdf_reader = PdfReader(oUploadFile.file)
    
    text = "\n".join(page.extract_text() for page in pdf_reader.pages)
    output_json = text.split("\n")
    
    ai_res = ai_receipt.inv_ai_txt(output_json)
    parsed_json = json.loads(ai_res)

    output_filename = pdf_name.replace('.pdf', '_txt.json')
    parsed_filename = pdf_name.replace('.pdf', '_txt_parsed.json')
    
    try:
        # Save the entire list of processed pages as a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)
        with open(parsed_filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)
        print(f"JSON file saved successfully to {output_filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return None  # Return None if saving fails

    return parsed_json


def inv_b64_one_2_json(base64_image, original_filename, output_directory):
    output_directory = os.path.abspath(output_directory)
    os.makedirs(output_directory, exist_ok=True)

    try:
        print("Processing image...")
        one_page_json_string = ai_receipt.inv_ai_b64(base64_image=base64_image)
        parsed_json = json.loads(one_page_json_string)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    output_filename = os.path.splitext(original_filename)[0] + "_extracted.json"
    output_path = os.path.join(output_directory, output_filename)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)
            print(f"JSON saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None

    return parsed_json