# import os
# from pymongo import MongoClient
# import logging
# import time

# # Replace with your MongoDB connection string
# MONGO_URI= os.getenv("MONGO_URI")
# print(MONGO_URI)

# # MongoDB connection with pymongo (synchronous)
# client = MongoClient(MONGO_URI)
# db = client['db_xai']  # Use a database for heartbeat
# heartbeat_collection = db['bankstatements']  # Use a collection for heartbeat data

# # Logging setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def is_textpdf(file_path: Path) -> bool:
#     try:
#         # Open the file in binary mode
#         with open(file_path, "rb") as file:  # Open the file
#             pdf_reader = PdfReader(file)  # Pass the file object to PdfReader
#             for page in pdf_reader.pages:
#                 if page.extract_text().strip():  # If any text exists on the page
#                     print('is textpdf?')
#                     return True
#         return False
#     except Exception as e:
#         print(f"Error: {e}")
#         return False  # If reading fails, treat as non-text PDF
    

# def bs_textpdf(file_path: str, pdf_name: str, pdf_folder: str) -> Optional[dict]:
#     try:
#         # Open the file directly
#         with open(file_path, 'rb') as file:
#             pdf_reader = PdfReader(file)
#             text = "\n".join(page.extract_text() for page in pdf_reader.pages)
#             output_json = text.split("\n")
        
#         ai_res = ai_bs1.bs_ai_txt(output_json)
#         parsed_json = json.loads(ai_res)
#         print(f"Processing PDF: {pdf_name}")

#         # Save the output files
#         output_filename = os.path.join(pdf_folder, pdf_name.replace('.pdf', '_txt.json'))
#         parsed_filename = os.path.join(pdf_folder, pdf_name.replace('.pdf', '_txt_parsed.json'))
        
#         with open(output_filename, 'w', encoding='utf-8') as f:
#             json.dump(output_json, f, ensure_ascii=False, indent=4)
#         with open(parsed_filename, 'w', encoding='utf-8') as f:
#             json.dump(parsed_json, f, ensure_ascii=False, indent=4)

#         return parsed_json

#     except Exception as e:
#         print(f"Error processing PDF: {str(e)}")
#         return None    


# # Heartbeat function to send "hello" message to MongoDB every minute
# def send_heartbeat():
#     try:
#         # Insert a document with the "hello" message and current timestamp
#         heartbeat_collection.insert_one({"message": "hello", "timestamp": time.time()})
#         logger.info("Heartbeat sent to MongoDB.")
#     except Exception as e:
#         logger.error(f"Error sending heartbeat: {str(e)}")

# # Initialize the scheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# scheduler = BackgroundScheduler()

# # Add the periodic task to the scheduler (every minute)
# scheduler.add_job(send_heartbeat, 'interval', minutes=1)

# # Start the scheduler
# scheduler.start()

# # This is important to keep the script running
# try:
#     while True:
#         time.sleep(1)
# except (KeyboardInterrupt, SystemExit):
#     print("Shutting down scheduler...")
#     scheduler.shutdown()
