import os, json
from typing import Optional
from fastapi import UploadFile, HTTPException
from PyPDF2  import PdfReader

from app.config import settings
from app.llm   import ai_bs
from app.utils import pdf264
from app.db.pg.model  import m_bs_ai
from app.db.pg.model.m_bs import BSDetailCreate, BSSummaryCreate


def bs_imgpdf(in_file_name: str, out_folder: str):
    try:
        # Convert PDF to text using your Ghostscript function
        b64_image   = pdf264.pdf_to_one_b64(in_file_name)
        ai_res = bs_b64_one_2_json(b64_image, in_file_name, out_folder)
        
        print(f"Parsed ai_res JSON: {ai_res}")
        return ai_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# def bs_textpdf(oUploadFile: UploadFile, pdf_name, pdf_folder):
#     pdf_reader = PdfReader(oUploadFile.file)
    
#     text = "\n".join(page.extract_text() for page in pdf_reader.pages)
#     output_json = text.split("\n")
    
#     ai_res = ai_bs.bs_ai_txt(output_json)
#     parsed_json = json.loads(ai_res)
#     validated_data = m_bs_ai.BankStatementAI(**parsed_json)

#     output_filename = pdf_name.replace('.pdf', '_txt.json')
#     parsed_filename = pdf_name.replace('.pdf', '_txt_parsed.json')
    
#     try:
#         # Save the entire list of processed pages as a JSON file
#         with open(output_filename, 'w', encoding='utf-8') as f:
#             json.dump(output_json, f, ensure_ascii=False, indent=4)
#         with open(parsed_filename, 'w', encoding='utf-8') as f:
#             json.dump(parsed_json, f, ensure_ascii=False, indent=4)
#         print(f"JSON file saved successfully to {output_filename}")
#     except Exception as e:
#         print(f"Error saving JSON file: {e}")
#         return None  # Return None if saving fails

#     return validated_data


def bs_b64_one_2_json(base64_image, original_filename, output_directory):
    output_directory = os.path.abspath(output_directory)
    os.makedirs(output_directory, exist_ok=True)

    try:
        print("Processing image...")
        one_page_json_string = ai_bs.bs_ai_b64(base64_image=base64_image)
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

def bs_image(in_file_name: str, out_folder: str):
    try:
        # Convert PDF to text using your Ghostscript function
        b64_image   = pdf264.pdf_to_one_b64(in_file_name)
        ai_res = bs_b64_one_2_json(b64_image, in_file_name, out_folder)
        
        print(f"Parsed ai_res JSON: {ai_res}")
        return ai_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def bs_text(in_file_name: str, out_folder: str):
    try:
        # Convert PDF to text using your Ghostscript function
        b64_image   = pdf264.pdf_to_one_b64(in_file_name)
        ai_res = bs_b64_one_2_json(b64_image, in_file_name, out_folder)
        
        print(f"Parsed ai_res JSON: {ai_res}")
        return ai_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def bs_textpdf(oUploadFile: UploadFile, pdf_name: str, pdf_folder: str) -> Optional[BSSummaryCreate]:
    try:
        pdf_reader = PdfReader(oUploadFile.file)
        text = "\n".join(page.extract_text() for page in pdf_reader.pages)
        output_json = text.split("\n")
        
        ai_res = ai_bs.bs_ai_txt(output_json)
        parsed_json = json.loads(ai_res)
        print(f"Processing PDF: {pdf_name}")
        # parsed_json = {
        #     "summary": {
        #         "account_number": "237031234760",
        #         "account_name": "TEA HILL, LLC",
        #         "bank_name": "Bank of America, N.A.",
        #         "statement_period_start": "2023-03-01",
        #         "statement_period_end": "2023-03-31",
        #         "opening_balance": 63528.7,
        #         "closing_balance": 60607.05,
        #         "currency": "USD"
        #     },
        #     "transactions": [
        #         {
        #         "date": "2023-03-02",
        #         "description": "MERCHANT BNKCD DES:DEPOSIT ID:266465843883 INDN:TEA HILL CO ID:FXXXXXXXXX CCD",
        #         "amount": 5401.9,
        #         "transaction_type": "credit",
        #         "reference": "null",
        #         "balance_after": 69030.6
        #         },
        #         {
        #         "date": "2023-03-02",
        #         "description": "Zelle payment to Wintime Food Corp for 'Supplies'; Conf# dcrfsubv7",
        #         "amount": 3260.0,
        #         "transaction_type": "debit",
        #         "reference": "dcrfsubv7",
        #         "balance_after": 65770.6
        #         },
        #         {
        #         "date": "2023-03-31",
        #         "description": "MERCHANT BNKCD DES:DEPOSIT ID:266465843883 INDN:TEA HILL CO ID:FXXXXXXXXX CCD",
        #         "amount": 2070.15,
        #         "transaction_type": "credit",
        #         "reference": "null",
        #         "balance_after": 64531.73
        #         },
        #     ]
        #     }

        # Save debug files
        output_filename = os.path.join(pdf_folder, pdf_name.replace('.pdf', '_txt.json'))
        parsed_filename = os.path.join(pdf_folder, pdf_name.replace('.pdf', '_txt_parsed.json'))
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)
        with open(parsed_filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)

        return parsed_json

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None