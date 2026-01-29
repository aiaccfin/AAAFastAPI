import os, json, pytesseract  
import subprocess, platform
from fastapi import UploadFile, HTTPException
from PyPDF2  import PdfReader
from pymongo import MongoClient

from app.config import settings
from app.llm   import ai_api
from app.utils import pdf264

def img2json(base64_images, original_filename, output_directory ):
    
    output_directory = os.path.abspath(output_directory)
    all_pages_converted_to_json = []
    
    for index, base64_image in enumerate(base64_images, start=1):
        print(f"Processing page {index} of {len(base64_images)}...")
        try:
            one_page_json_string = ai_api.b64_2_json(base64_image=base64_image)
            one_page_json_object = json.loads(one_page_json_string)
            all_pages_converted_to_json.append(one_page_json_object)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError on page {index}: {e}")
            continue  # Skip to the next image
        except Exception as e:
            print(f"An unexpected error occurred on page {index}: {e}")
            continue  # Skip to the next image

    if not all_pages_converted_to_json:
        print("No pages were successfully processed.")
        return None  
    
    # Construct the output file path
    output_filename = original_filename.replace('.pdf', '_extracted.json')
    
    try:
        # Save the entire list of processed pages as a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_pages_converted_to_json, f, ensure_ascii=False, indent=4)
        print(f"JSON file saved successfully to {output_filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return None  # Return None if saving fails

    return output_filename


def is_text_pdf(file: UploadFile) -> bool:
    try:
        pdf_reader = PdfReader(file.file)
        for page in pdf_reader.pages:
          
            if page.extract_text().strip():  # If any text exists on the page
                print(1112)
                return True
        return False
    except Exception as e:
        return False  # If reading fails, treat as non-text PDF



def convert_text_pdf(local_input_filename, output_directory):
    # Detect the operating system
    if platform.system() == "Windows":
        gs_command = "gswin64c"  # Use the Windows executable for Ghostscript
    else:
        gs_command = "gs"  # Use the Linux path for Ghostscript

    os.makedirs(output_directory, exist_ok=True)

    # Construct the output file path
    local_output_filename = os.path.join(output_directory, os.path.basename(local_input_filename).replace('.pdf', '_text.txt'))


    subprocess.call([gs_command,
                     "-q",
                     "-dNOPAUSE",
                     "-dBATCH",
                     "-sDEVICE=txtwrite",
                     f"-sOutputFile={local_output_filename}",
                     f"{local_input_filename}"])
    return local_output_filename


async def pdf_to_text_ghostscript(pdf: UploadFile):
    try:

        # Convert PDF to text using your Ghostscript function
        output_text_path = convert_text_pdf(input_pdf_path, output_dir)

        # Read the resulting text file
        with open(output_text_path, "r") as f:
            extracted_text = f.read()


        return {"text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def perform_ocr_on_image_pdf(file: UploadFile) -> str:
    # Convert PDF to images (assuming pdf264 has the logic)
    file.seek(0)  # Reset file pointer for OCR
    images = pdf264.pdf_to_base64_images(file.file)
    ocr_text = ""
    for image in images:
        ocr_text += pytesseract.image_to_string(image)  # OCR on each image
    return ocr_text



def img_pdf(in_file_name: str, out_folder: str):
    try:
        # Convert PDF to text using your Ghostscript function
        base64_images= pdf264.pdf_to_base64_images(in_file_name)
        output_json  = img2json(base64_images, in_file_name, out_folder)

        # Read the resulting text file
        with open(output_json, "r") as f:
            extracted_text = f.read()

        return {"img_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def save2db():
    file_path = './tmp/ds.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract the raw text from the JSON
    details = "\n".join(data.get("details", []))

    res = ai_api.save2db_response(details)
    parsed_data = json.loads(res)

    output_filename = './resparse.json'
    
    try:
        # Save the entire list of processed pages as a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)
        print(f"JSON file saved successfully to {output_filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return None  # Return None if saving fails

    

    # Connect to MongoDB
    client = MongoClient(settings.CFG['MONGO_DB_URI'])
    db = client['db_ocr']
    collection = db['bank_statements']

    # Insert the parsed data
    collection.insert_one(parsed_data)

    print("Data inserted successfully.")


def pdf_reader(oUploadFile: UploadFile, pdf_name, pdf_folder):
    pdf_reader = PdfReader(oUploadFile.file)
    text = "\n".join(page.extract_text() for page in pdf_reader.pages)
    
    output_json = {
        "details": text.split("\n")  # Splitting by lines for a structured approach
    }

    ai_res = ai_api.save2db_response(output_json)
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


# def inv_ai_textpdf(oUploadFile: UploadFile, pdf_name, pdf_folder):
#     pdf_reader = PdfReader(oUploadFile.file)
    
#     text = "\n".join(page.extract_text() for page in pdf_reader.pages)
#     output_json = text.split("\n")
    
#     # output_json = {
#     #     "details": text.split("\n")  # Splitting by lines for a structured approach
#     # }
#     ai_res = ai_inv.inv_txtpdf_2_json(output_json)
#     parsed_json = json.loads(ai_res)

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

#     return parsed_json
