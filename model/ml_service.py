import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import (
    decode_predictions,
    preprocess_input,
)
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
    host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID
)

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    class_name = None
    pred_probability = None
    # TODO: Implement the code to predict the class of the image_name

    # Load image
    img = image.load_img(
        os.path.join(settings.UPLOAD_FOLDER, image_name),
        target_size=(224, 224),
    )

    # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Get predictions using model methods and decode predictions using resnet50 decode_predictions
    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=1)[0]
    _, class_name, pred_probability = decoded_predictions[0]

    # Convert probabilities to float and round it
    pred_probability = round(float(pred_probability), 4)

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Take a new job from Redis
        job_data = db.brpop(settings.REDIS_QUEUE, timeout=1)

        if job_data is not None:
            # Decode the JSON data for the given job
            job_info = json.loads(job_data[1])

            # Important! Get and keep the original job ID
            job_id = job_info["id"]

            # Run the loaded ml model (use the predict() function)
            class_name, pred_probability = predict(job_info["image_name"])

            # Prepare a new JSON with the results
            result = {"prediction": class_name, "score": pred_probability}

            # Store the job results on Redis using the original
            # job ID as the key
            db.set(job_id, json.dumps(result))

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


# ============================================================================
# BATCH PROCESSING FUNCTIONS (Optional Part 3)
# ============================================================================


def predict_batch(image_names):
    """
    Predict multiple images in a single batch for better performance.

    This function processes multiple images simultaneously, which is more
    efficient than processing them one by one because:
    - GPU/CPU can parallelize operations
    - Reduced overhead per image
    - Better utilization of model resources

    Parameters
    ----------
    image_names : list of str
        List of image filenames to process.

    Returns
    -------
    results : list of tuple(str, float)
        List of (class_name, pred_probability) for each image in the same order.
    """
    if not image_names:
        return []

    # Load and preprocess all images
    batch_images = []
    for image_name in image_names:
        try:
            img = image.load_img(
                os.path.join(settings.UPLOAD_FOLDER, image_name),
                target_size=(224, 224),
            )
            img_array = image.img_to_array(img)
            img_array = preprocess_input(img_array)
            batch_images.append(img_array)
        except Exception as e:
            print(f"Error loading image {image_name}: {e}")
            # Add a placeholder for failed images
            batch_images.append(np.zeros((224, 224, 3)))

    # Create batch tensor: (batch_size, 224, 224, 3)
    batch_tensor = np.array(batch_images)

    # Single prediction call for all images - THIS IS THE KEY OPTIMIZATION!
    batch_predictions = model.predict(batch_tensor, verbose=0)

    # Decode results for each image
    results = []
    for idx, predictions in enumerate(batch_predictions):
        try:
            # Expand dimensions for decode_predictions
            pred_expanded = np.expand_dims(predictions, axis=0)
            decoded = decode_predictions(pred_expanded, top=1)[0]
            _, class_name, pred_probability = decoded[0]
            pred_probability = round(float(pred_probability), 4)
            results.append((class_name, pred_probability))
        except Exception as e:
            print(f"Error decoding prediction for image {idx}: {e}")
            results.append(("error", 0.0))

    return results


def classify_process_batch():
    """
    Loop indefinitely processing jobs in batches for better performance.

    This function collects multiple jobs from Redis and processes them together,
    which significantly improves throughput compared to individual processing.

    Configuration:
    - BATCH_SIZE: Maximum number of images to process together
    - BATCH_TIMEOUT: Maximum time to wait for collecting a batch
    """
    # Batch configuration from settings
    BATCH_SIZE = settings.BATCH_SIZE
    BATCH_TIMEOUT = settings.BATCH_TIMEOUT

    print(
        f"Launching ML service with BATCH processing (size={BATCH_SIZE}, timeout={BATCH_TIMEOUT}s)..."
    )

    while True:
        jobs_batch = []
        start_time = time.time()

        # Collect jobs for the batch
        while len(jobs_batch) < BATCH_SIZE:
            # Calculate remaining time for this batch
            elapsed = time.time() - start_time
            remaining_time = BATCH_TIMEOUT - elapsed

            # If timeout reached, process what we have
            if remaining_time <= 0:
                break

            # Try to get a job from Redis
            timeout = max(1, int(remaining_time))
            job_data = db.brpop(settings.REDIS_QUEUE, timeout=timeout)

            if job_data is not None:
                try:
                    job_info = json.loads(job_data[1])
                    jobs_batch.append(
                        {
                            "id": job_info["id"],
                            "image_name": job_info["image_name"],
                        }
                    )
                except Exception as e:
                    print(f"Error parsing job data: {e}")
            else:
                # No more jobs available, process what we have
                break

        # Process batch if we have any jobs
        if jobs_batch:
            batch_start = time.time()
            image_names = [job["image_name"] for job in jobs_batch]

            # Single batch prediction for all images
            batch_results = predict_batch(image_names)

            batch_time = time.time() - batch_start

            # Store individual results in Redis
            for job, (class_name, pred_probability) in zip(
                jobs_batch, batch_results
            ):
                result = {"prediction": class_name, "score": pred_probability}
                db.set(job["id"], json.dumps(result))

            print(
                f"Batch processed {len(jobs_batch)} jobs in {batch_time:.3f}s "
                f"({batch_time / len(jobs_batch):.3f}s per image)"
            )

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Choose processing mode based on environment variable
    import sys

    # Check if batch mode is requested
    use_batch = (
        os.environ.get("USE_BATCH_PROCESSING", "false").lower() == "true"
    )

    if use_batch or "--batch" in sys.argv:
        print("=" * 60)
        print("BATCH PROCESSING MODE ENABLED")
        print("=" * 60)
        classify_process_batch()
    else:
        print("=" * 60)
        print("INDIVIDUAL PROCESSING MODE (default)")
        print("=" * 60)
        print("Launching ML service...")
        classify_process()
