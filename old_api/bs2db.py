import os, time, logging, shutil, json
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader
from app.db.pg.p_conn import get_session_no_yield
from app.db.pg.crud import c_bs
from app.services import s_bs
from app.llm import ai_bs
from app.db.pg.model import m_bs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_textpdf(file_path: Path) -> bool:
    try:
        # Open the file in binary mode
        with open(file_path, "rb") as file:  # Open the file
            pdf_reader = PdfReader(file)  # Pass the file object to PdfReader
            for page in pdf_reader.pages:
                if page.extract_text().strip():  # If any text exists on the page
                    print('is textpdf?')
                    return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False  # If reading fails, treat as non-text PDF

def bs_textpdf(file_path: str, pdf_name: str, pdf_folder: str) -> Optional[dict]:
    try:
        # Open the file directly
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages)
            output_json = text.split("\n")
        
        ai_res = ai_bs.bs_ai_txt(output_json)
        parsed_json = json.loads(ai_res)
        print(f"Processing PDF: {pdf_name}")

        # Save the output files
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

def my_task():
    logger.info("Task is running...")
    upload_folder = Path("./tmp/v6").resolve()
    finish_folder = Path("./tmp/done").resolve()
    try:
        with get_session_no_yield() as db: 
            # Loop through all files in the upload folder   
            for oFile in upload_folder.iterdir():
                logger.info(f"Trying to open file: {oFile}")
                if oFile.is_file():
                    pdf_name = oFile.name
                    pdf_folder = str(oFile.parent)
                    logger.info(f"2 Trying to open file: {oFile}")
                    # Process the file as text-pdf or img-pdf
                    if is_textpdf(oFile):  # Ensure oFile is a Path object
                        bs_data = bs_textpdf(oFile, pdf_name, pdf_folder)
                        _type = "text-pdf"
                    else:
                        bs_data = s_bs.bs_imgpdf(pdf_name, pdf_folder)
                        _type = "img-pdf"
                    logger.info(f"3 Trying to open file: {_type}")

                    if not bs_data:
                        logger.error(f"Failed to process PDF: {pdf_name}")
                        continue

                    # Save the processed data to the database
                    result = c_bs.save_parsed_bs(bs_data, db)

                    logger.info(f"Processed {pdf_name} as {_type} and saved to DB.")
                    # try:
                    #     shutil.move(str(oFile), os.path.join(finish_folder, pdf_name))
                    #     logger.info(f"Moved {pdf_name} to the 'done' folder.")
                    # except Exception as move_err:
                    #     logger.error(f"Error moving file {pdf_name}: {str(move_err)}")

    except Exception as e:
        logger.error(f"Server error while processing files: {str(e)}")


# This makes sure that the task won't run automatically if this script is imported elsewhere
if __name__ == "__main__":
    my_task()
