from pymongo import MongoClient
import logging
import time

# Replace with your MongoDB connection string
MONGO_URI = "mongodb+srv://aiaccfin:fgXMg0LHwgLSpzAR@aiacccluster.gvoyp.mongodb.net/?retryWrites=true&w=majority&appName=aiaccCluster"

# MongoDB connection with pymongo (synchronous)
client = MongoClient(MONGO_URI)
db = client['heartbeat_db']  # Use a database for heartbeat
heartbeat_collection = db['heartbeat']  # Use a collection for heartbeat data

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Heartbeat function to send "hello" message to MongoDB every minute
def send_heartbeat():
    try:
        # Insert a document with the "hello" message and current timestamp
        heartbeat_collection.insert_one({"message": "hello", "timestamp": time.time()})
        logger.info("Heartbeat sent to MongoDB.")
    except Exception as e:
        logger.error(f"Error sending heartbeat: {str(e)}")

# Initialize the scheduler
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

# Add the periodic task to the scheduler (every minute)
scheduler.add_job(send_heartbeat, 'interval', minutes=1)

# Start the scheduler
scheduler.start()

# This is important to keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    print("Shutting down scheduler...")
    scheduler.shutdown()
