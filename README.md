# WhatsApp Scheduler

A cross-platform WhatsApp message scheduler that reads an Excel file, schedules messages, and sends them via WhatsApp using Node.js automation.  
Includes a Streamlit web interface for easy uploads and scheduling.

## Features

- Upload Excel files with schedule (Phone, Message, Image, Scheduled Time)
- Schedule messages or send immediately
- Supports images and text
- Random delay to mimic human behavior
- Streamlit web UI

## Folder Structure

Whatsapp Project/
├── app/
│ ├── scheduler.py
│ └── streamlit_app.py
├── node_whatsapp/
│ └── send_message.cjs
├── uploads/
│ └── [your Excel files]


## Requirements

- Python 3.8+
- Node.js 18+
- WhatsApp account (scan QR code on first run)

## Setup

1. Clone this repository (private).
2. Install Python dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Install Node.js dependencies:
    ```
    cd node_whatsapp
    npm install
    ```
4. Run the Streamlit app:
    ```
    streamlit run app/streamlit_app.py
    ```

## Usage

- Upload your Excel schedule via the web UI.
- Use the `--now` flag to send all messages immediately:
    ```
    python app/scheduler.py uploads/schedule.xlsx --now
    ```

## License

Private repository. For internal or invited collaborator use only.
