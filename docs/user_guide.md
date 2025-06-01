# User Guide – SmartTask

## Overview
SmartTask is a personal assistant desktop app that helps you manage your daily tasks with a graphical interface. It supports text and voice input, calendar selection, reminder notifications (email, toast, sound), and Excel-based task export.

## Launching the App
After setup, run:
```bash
python -m smarttask.src.main
```

## Key Features

### 1. Add Task
- Enter task description and date/time
- Optional: mark as repeating
- Click “Add Task” to save

### 2. View All Tasks
- All scheduled tasks are listed in the main window
- Repeating tasks are shown accordingly

### 3. Calendar Filter
- Click “Calendar” to choose a date
- Click “Show Tasks for Day” to filter by selected date

### 4. Voice Input
- Click “Voice Add Task”
- Say the task and time (e.g., “Doctor appointment at 5 PM”)
- Confirm parsed result to add it

### 5. Delete Task
- Select any task in the list
- Click “Delete Task” to remove it

### 6. Export to Excel
- Click “Export to Excel” to save your tasks in `.xlsx` format

### 7. Reminder Notifications
- Email: Sent if configured in `notifications.py`
- Sound alert: Plays when task is due
- Windows toast: Notification pops up on desktop

## Notes
- All tasks are saved in `tasks.json`
- The app requires an active internet connection for email notifications
- To enable email reminders, update your sender credentials in `notifications.py`
