"""
utils.py

Utility functions for WhatsApp Scheduler project.
Includes Excel reading, input validation, and logging helpers.

Author: [Kushal K P]
Date: 2025-05-14
"""

import os
import pandas as pd
from datetime import datetime

def validate_excel_columns(df, required_columns):
    """
    Validates that the DataFrame contains the required columns.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
        required_columns (set): Set of required column names.

    Raises:
        ValueError: If any required column is missing.
    """
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Excel file is missing columns: {missing}")

def read_excel_schedule(file_path):
    """
    Reads the schedule Excel file and returns a DataFrame.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: DataFrame with schedule data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    df = pd.read_excel(file_path)
    required_columns = {'Phone', 'Message', 'Image', 'Scheduled Time'}
    validate_excel_columns(df, required_columns)
    return df

def log_status(log_dir, status, phone, send_time, message, image, error_msg=None):
    """
    Logs the status of a message attempt to a log file.

    Args:
        log_dir (str): Directory where log files are stored.
        status (str): 'sent', 'failed', or other status.
        phone (str): Recipient phone number.
        send_time (datetime): Scheduled send time.
        message (str): Message text.
        image (str): Image path or URL.
        error_msg (str, optional): Error message, if any.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"{datetime.now().date()}_log.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        log_entry = (
            f"{datetime.now().isoformat()} | "
            f"STATUS: {status} | "
            f"PHONE: {phone} | "
            f"TIME: {send_time} | "
            f"MESSAGE: {message} | "
            f"IMAGE: {image}"
        )
        if error_msg:
            log_entry += f" | ERROR: {error_msg}"
        f.write(log_entry + "\n")

def is_valid_phone(phone):
    """
    Basic validation for phone number format (international).

    Args:
        phone (str): Phone number string.

    Returns:
        bool: True if valid, False otherwise.
    """
    return isinstance(phone, str) and phone.startswith('+') and phone[1:].isdigit() and 8 < len(phone) < 16

def parse_datetime(dt_str):
    """
    Parses a datetime string into a datetime object.

    Args:
        dt_str (str): The datetime string.

    Returns:
        datetime: Parsed datetime object.

    Raises:
        ValueError: If parsing fails.
    """
    try:
        return pd.to_datetime(dt_str)
    except Exception as e:
        raise ValueError(f"Could not parse datetime '{dt_str}': {e}")
