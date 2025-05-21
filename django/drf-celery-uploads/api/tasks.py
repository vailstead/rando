from celery import shared_task
import time
import logging
from django.core.cache import cache
logger = logging.getLogger(__name__)

LOCK_EXPIRE = 60 * 10  # 10 minutes lock expiration, adjust as needed

@shared_task(bind=True, queue='isolated')
def process_csv(self, file_path):
    # Placeholder: simulate file processing
    lock_id = "lock:process_csv"
    # Try to add the lock key, only if it does NOT exist
    have_lock = cache.add(lock_id, "true", LOCK_EXPIRE)
    logger.info(f"[INFO] {self.request.id} - Lock acquired: {have_lock}")
    logger.info(f"[INFO] {self.request.id} - Lock will be released when task if finished or in {LOCK_EXPIRE} minutes")
    if not have_lock:
        # Another task is running
        logger.info(f"[INFO] Unable to obtain {self.request.id} Lock: {have_lock}. Retrying...")
        self.retry(countdown=10, max_retries=3)
        return

    try:
        # Do your processing here
        for i in range(60):
            logger.info(f"Processing {file_path}: {i+1}%")
            # Simulate some processing time
            time.sleep(1)
    finally:
        # Release the lock
        logger.info(f"[INFO] {self.request.id} - Lock release")
        cache.delete(lock_id)

    
@shared_task(bind=True, queue='default')
def long_running_task(self):
    # Placeholder: simulate a long-running task
    for i in range(60):
        logger.info(f"{self.request.id} running a long task: {i+1}%")
        # Simulate some processing time
        time.sleep(10)
