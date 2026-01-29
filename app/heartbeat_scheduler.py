# app/heartbeat_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import asyncio

from app.db.x_mg_conn import item_collection, bs_collection
from app.db import x_mg_conn  # assume you have a MongoDB collection


logger = logging.getLogger(__name__)

# Initialize the scheduler
scheduler = BackgroundScheduler()

# ----------- HEARTBEAT JOB ----------- 
async  def heartbeat_job():
    heartbeat_data = {
        "item_id": "heartbeat",
        "name": "heartbeat_item",
        "description": "This is a heartbeat entry",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # Insert heartbeat into MongoDB collection
    await x_mg_conn.bs_collection.insert_one(heartbeat_data)
    await x_mg_conn.item_collection.insert_one(heartbeat_data)
    logger.info(f"Heartbeat written -----------------------------------------------")
def start_heartbeat_scheduler():
    # Schedule the heartbeat job to run every 2 minutes (or your preferred interval)
    scheduler.add_job(run_heartbeat_job, 'interval', minutes=2)
    scheduler.start()

def stop_heartbeat_scheduler():
    scheduler.shutdown()

# Wrapper function to ensure async heartbeat job runs in the main event loop
def run_heartbeat_job():
    loop = asyncio.get_event_loop()

    # Ensure the job is executed in the correct event loop
    if loop.is_running():
        # If the event loop is running, run the job safely in the current loop
        asyncio.run_coroutine_threadsafe(heartbeat_job(), loop)
    else:
        # If not running in the main loop, run it until completion
        loop.run_until_complete(heartbeat_job())  # Block until the async task completes