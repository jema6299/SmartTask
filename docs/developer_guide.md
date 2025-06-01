# Developer Guide – SmartTask

## Overview
SmartTask is a modular, Python 3.10+ desktop application for task management. It includes features like task creation, deletion, date filtering, calendar-based selection, Excel import/export, voice-based task entry, and multi-channel reminders (email, sound, toast). The app uses a GUI built with `tkinter`.

## Project Structure
- `smarttask/src/main.py`: Launches the application.
- `smarttask/src/data_handler.py`: Handles JSON and Excel operations.
- `smarttask/src/task_manager.py`: Core logic for task operations and calendar.
- `smarttask/src/notifications.py`: Sends email, sound, and toast reminders.
- `smarttask/src/voice_input.py`: Captures tasks via voice input.
- `smarttask/tests/`: Contains unit tests for each module.
- `tasks.json`: Default file where tasks are stored.

## Setup Instructions
1. Install Python 3.10+
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
## Install dependencies:
    ```bash
    pip install -r requirements.txt
## Running the Application:
    ```bash
    python -m smarttask.src.main
## Running Tests"
    ```bash
    pytest --maxfail=1 --disable-warnings -q