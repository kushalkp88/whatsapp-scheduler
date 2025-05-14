"""
streamlit_app.py

Streamlit UI for WhatsApp Scheduler.
Allows users to upload an Excel schedule, preview data, and start scheduling messages.

Author: [Your Name]
Date: 2025-05-14
"""

import os
import shutil
import subprocess
import streamlit as st
import pandas as pd

UPLOAD_DIR = "uploads"
SCHEDULE_FILE = os.path.join(UPLOAD_DIR, "schedule.xlsx")

st.set_page_config(page_title="WhatsApp Scheduler", layout="centered")

st.title("📅 WhatsApp Message Scheduler")

st.markdown(
    """
    Upload an Excel file with columns: **Phone**, **Message**, **Image**, **Scheduled Time**.<br>
    Example:<br>
    <pre>
    | Phone        | Message      | Image         | Scheduled Time        |
    |--------------|--------------|---------------|----------------------|
    | +1234567890  | Hello!       | ./img1.jpg    | 2025-05-15 10:00:00  |
    </pre>
    """,
    unsafe_allow_html=True,
)

# File upload section
uploaded_file = st.file_uploader("Upload your schedule Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Save uploaded file
    with open(SCHEDULE_FILE, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    st.success("File uploaded successfully!")

    # Preview the Excel data
    try:
        df = pd.read_excel(SCHEDULE_FILE)
        st.subheader("Preview of Uploaded Schedule")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    # Start scheduling
    if st.button("Start Scheduling"):
        st.info("Scheduling messages. Please keep this app running and check the terminal for QR scan prompt (first run only).")
        # Call scheduler.py as a subprocess
        try:
            result = subprocess.Popen(
                ["python", "app/scheduler.py", SCHEDULE_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            st.success("Scheduler started. Monitor the logs in your terminal window.")
            st.markdown(
                "If this is your first run, check the terminal for a QR code and scan it with your WhatsApp app."
            )
        except Exception as e:
            st.error(f"Failed to start scheduler: {e}")

    # Display log file if exists
    log_dir = "logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith("_log.txt")]
        if log_files:
            latest_log = sorted(log_files)[-1]
            st.subheader("Latest Log")
            with open(os.path.join(log_dir, latest_log), "r", encoding="utf-8") as logf:
                st.text(logf.read())
        else:
            st.info("No logs available yet.")
else:
    st.info("Please upload an Excel file to begin.")

