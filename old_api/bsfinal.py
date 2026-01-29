import os, time, logging, shutil, json
from pathlib import Path
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from PyPDF2 import PdfReader

from typing import Optional
from PyPDF2 import PdfReader
from app.llm import ai_bs

# MONGO_URI= os.getenv("MONGO_AIACCFIN")
MONGO_URI = "mongodb+srv://aiaccfin:fgXMg0LHwgLSpzAR@aiacccluster.gvoyp.mongodb.net/?retryWrites=true&w=majority&appName=aiaccCluster"
# client = AsyncIOMotorClient(MONGO_URI)
# db     = client.db_xai

# MongoDB connection setup
# MONGO_URI = os.getenv("MONGO_URI")  # Ensure this is set in your environment
client = MongoClient(MONGO_URI)
db = client['db_xai']  # Use a database for heartbeat
heartbeat_collection = db['bankstatements']  # Collection for processed data

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PDF Processing Functions (Same as your provided logic)
def is_textpdf(file_path: Path) -> bool:
    try:
        # Open the file in binary mode
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                if page.extract_text().strip():
                    logger.info(f"{file_path.name} is a text PDF.")
                    return True
        return False
    except Exception as e:
        logger.error(f"Error in is_textpdf: {str(e)}")
        return False

def bs_textpdf(file_path: str, pdf_name: str, pdf_folder: str) -> Optional[dict]:
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages)
            output_json = text.split("\n")

        ai_res = ai_bs.bs_ai_txt(output_json)
        parsed_json = json.loads(ai_res)
        logger.info(f"2----------------Processing PDF: {pdf_name}")
        
        # Insert processed JSON data into MongoDB (bankstatements collection)
        heartbeat_collection.insert_one({
            "pdf_name": pdf_name,
            "processed_data": parsed_json,
            "timestamp": time.time()
        })

        logger.info(f"3----------------Saved data for {pdf_name} to MongoDB.")
        return parsed_json
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_name}: {str(e)}")
        return None



def my_task():
    logger.info("1. Task is running...")

    # Set up directories for file processing
    upload_folder = Path("./tmp/v7").resolve()
    finish_folder = Path("./tmp/v7done").resolve()
    error_folder = Path("./tmp/error").resolve()

    try:
        # Loop through all files in the upload folder
        for oFile in upload_folder.iterdir():
            logger.info(f"Trying to open file: {oFile}")
            
            if oFile.is_file():
                try:
                    # Skip non-PDF files
                    if oFile.suffix.lower() != '.pdf':
                        logger.info(f"Skipping non-PDF file: {oFile.name}")
                        continue
                    
                    pdf_name = oFile.name
                    pdf_name_without_pdf = pdf_name.rsplit('.', 1)[0]
                    pdf_folder = str(oFile.parent)

                    # Process the file as text-pdf or image-pdf
                    if is_textpdf(oFile):
                        bs_data = bs_textpdf(oFile, pdf_name, pdf_folder)
                        logger.info(f"1------- Processed text PDF: {oFile.name} {bs_data}")
                        _type = "text-pdf"
                    else:
                        logger.info(f"Skipping image-based PDF: {oFile.name}")
                        continue  # Optionally, handle image PDFs if needed

                    if not bs_data:
                        logger.error(f"Failed to process PDF: {pdf_name}")
                        shutil.move(str(oFile), os.path.join(error_folder, pdf_name))
                        continue
                    
                    # Move the processed PDF to the "done" folder
                    shutil.move(str(oFile), os.path.join(finish_folder, pdf_name))
                    logger.info(f"Moved {pdf_name} to 'done' folder.")

                except Exception as e:
                    logger.error(f"Error with file {oFile.name}: {e}")
                    shutil.move(str(oFile), os.path.join(error_folder, oFile.name))
                    continue

    except Exception as e:
        logger.error(f"Server error while processing files: {str(e)}")

# Initialize the scheduler
scheduler = BackgroundScheduler()

scheduler.add_job(my_task, 'interval', minutes=12)

# Start the scheduler
scheduler.start()

# Keep the script running to allow periodic jobs to execute
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
