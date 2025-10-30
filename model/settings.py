import os

# We will store images uploaded by the user on this folder
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# REDIS
# Queue name
REDIS_QUEUE = "service_queue"
# Port
REDIS_PORT = 6379
# DB Id
REDIS_DB_ID = 0
# Host IP
REDIS_IP = os.getenv("REDIS_IP", "redis")
# Sleep parameters which manages the
# interval between requests to our redis queue
SERVER_SLEEP = 0.05

# BATCH PROCESSING CONFIGURATION (Optional Part 3)
# Maximum number of images to process in a single batch
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
# Maximum time (seconds) to wait for collecting a batch
BATCH_TIMEOUT = float(os.getenv("BATCH_TIMEOUT", "2.0"))
