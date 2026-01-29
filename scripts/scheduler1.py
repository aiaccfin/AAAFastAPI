import os, time, logging, shutil
from fastapi import HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app import db
from app.db.pg.crud import c_bs
from app.services import s_bs1
from app.utils import u_is_textpdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your periodic task
def my_task():
    logger.info("Task is running every 1 minutes...")
    upload_folder = os.path.abspath("./tmp/v61")
    finish_folder = os.path.abspath("./tmp/v61done")
    try:
        # Loop through all files in the upload folder   
        for oFile in upload_folder.iterdir():
            if oFile.is_file():
                pdf_name = oFile.name
                pdf_folder = str(oFile.parent)

                # Process the file as text-pdf or img-pdf
                if u_is_textpdf.is_textpdf(oFile):
                    bs_data = s_bs1.bs_textpdf(oFile, pdf_name, pdf_folder)
                    _type = "text-pdf"
                else:
                    bs_data = s_bs1.bs_imgpdf(pdf_name, pdf_folder)
                    _type = "img-pdf"

                # If processing failed, raise an HTTPException
                if not bs_data:
                    logger.error(f"Failed to process PDF: {pdf_name}")
                    continue

                # Save the processed data to the database
                result = c_bs.save_parsed_bs(bs_data, db)

                logger.info(f"Processed {pdf_name} as {_type} and saved to DB.")
                try:
                    shutil.move(str(oFile), os.path.join(finish_folder, pdf_name))
                    logger.info(f"Moved {pdf_name} to the 'done' folder.")
                except Exception as move_err:
                    logger.error(f"Error moving file {pdf_name}: {str(move_err)}")

    except HTTPException as http_err:
        logger.error(f"HTTPException: {http_err.detail}")
    except Exception as e:
        logger.error(f"Server error while processing files: {str(e)}")

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Add the periodic task to the scheduler (every 10 minutes)
scheduler.add_job(my_task, 'interval', minutes=1)

# Start the scheduler
scheduler.start()

# This is important to keep the script running
try:
    while True:
        time.sleep(1)  # Keeps the script alive while the background job runs
except (KeyboardInterrupt, SystemExit):
    # Graceful shutdown when the script is stopped
    print("Shutting down scheduler...")
    scheduler.shutdown()
