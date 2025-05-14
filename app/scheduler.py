"""
scheduler.py

This script reads an Excel file containing WhatsApp message schedules, processes each entry, and schedules messages to be sent at specified times.
It uses pandas for data handling, APScheduler for scheduling, and subprocess to invoke a Node.js script (using @open-wa/wa-automate) for message delivery.
A random delay (15–45 seconds) is applied before each message is sent to mimic human behavior.

Folder structure reference:
- Place this script in the `app/` directory.
- Node.js script (send_message.cjs) should be in `node_whatsapp/`.
- Uploaded Excel files should be placed in `uploads/`.

Author: [Kushal K P]
Date: 2025-05-14
"""

import os
import sys
import time
import random
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime
import argparse
import math

def read_schedule_from_excel(file_path):
    """
    Reads the Excel file and returns a DataFrame with required columns.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: DataFrame with columns ['Phone', 'Message', 'Image', 'Scheduled Time'].
    """
    df = pd.read_excel(file_path)
    expected_columns = {'Phone', 'Message', 'Image', 'Scheduled Time'}
    if not expected_columns.issubset(set(df.columns)):
        raise ValueError(f"Excel file must contain columns: {expected_columns}")
    # Clean up: Replace NaN in Image column with empty string
    df['Image'] = df['Image'].fillna('')
    return df

def is_valid_image(image):
    """
    Checks if the image value is a valid, non-empty string.

    Args:
        image: The image value.

    Returns:
        bool: True if valid, False otherwise.
    """
    if image is None:
        return False
    if isinstance(image, float) and math.isnan(image):
        return False
    if isinstance(image, str):
        if not image.strip() or image.strip().lower() == 'nan':
            return False
    return True

def send_whatsapp_message(phone, message, image):
    """
    Calls the Node.js script to send a WhatsApp message.

    Args:
        phone (str): Recipient phone number in international format.
        message (str): Message text.
        image (str): Image path or URL (can be empty).
    """
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    node_script = os.path.join(PROJECT_ROOT, 'node_whatsapp', 'send_message.cjs')

    args = ['node', node_script, phone, message]
    if is_valid_image(image):
        args.append(str(image))
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] Message sent to {phone}")
        else:
            print(f"[{datetime.now()}] Failed to send message to {phone}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[{datetime.now()}] Exception sending message to {phone}: {e}")

def schedule_message(scheduler, send_time, phone, message, image, min_delay=15, max_delay=45):
    """
    Schedules a WhatsApp message with a random delay (default 15–45 seconds) before sending.

    Args:
        scheduler (BackgroundScheduler): APScheduler instance.
        send_time (datetime): Time to send the message.
        phone (str): Recipient phone number.
        message (str): Message text.
        image (str): Image path or URL.
        min_delay (int): Minimum random delay in seconds.
        max_delay (int): Maximum random delay in seconds.
    """
    def job():
        delay = random.randint(min_delay, max_delay)
        print(f"[{datetime.now()}] Waiting {delay} seconds before sending to {phone}")
        time.sleep(delay)
        send_whatsapp_message(phone, message, image)
    scheduler.add_job(job, 'date', run_date=send_time)
    print(f"[{datetime.now()}] Scheduled message to {phone} at {send_time}")

def main():
    """
    Main function to read the Excel schedule, set up the scheduler, and keep the script running.
    Adds a --now flag to send all messages immediately for testing.
    """
    parser = argparse.ArgumentParser(description="WhatsApp Scheduler")
    parser.add_argument("excel_file", help="Path to the Excel schedule file")
    parser.add_argument("--now", action="store_true", help="Send all messages immediately (for testing)")
    args = parser.parse_args()

    excel_file = args.excel_file
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        sys.exit(1)

    df = read_schedule_from_excel(excel_file)

    if args.now:
        print(f"[{datetime.now()}] --now flag detected. Sending all messages immediately (with random delay).")
        for _, row in df.iterrows():
            phone = str(row['Phone'])
            message = str(row['Message']).strip() if 'Message' in row else ''
            if not message:
                message = "hi"
            image = row['Image'] if 'Image' in row else ''
            delay = random.randint(15, 45)
            print(f"[{datetime.now()}] Waiting {delay} seconds before sending to {phone}")
            time.sleep(delay)
            send_whatsapp_message(phone, message, image)
        print(f"[{datetime.now()}] All messages sent.")
    else:
        scheduler = BackgroundScheduler()
        scheduler.start()
        any_scheduled = False

        for _, row in df.iterrows():
            phone = str(row['Phone'])
            message = str(row['Message']).strip() if 'Message' in row else ''
            if not message:
                message = "hi"
            image = row['Image'] if 'Image' in row else ''
            send_time = pd.to_datetime(row['Scheduled Time'])
            if send_time > datetime.now():
                schedule_message(scheduler, send_time, phone, message, image)
                any_scheduled = True
            else:
                print(f"[{datetime.now()}] Skipping past time for {phone}: {send_time}")

        if any_scheduled:
            print(f"[{datetime.now()}] Scheduler started. Press Ctrl+C to exit.")
            try:
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                scheduler.shutdown()
                print("Scheduler stopped.")
        else:
            print(f"[{datetime.now()}] No future messages to schedule. Exiting.")

if __name__ == "__main__":
    main()
