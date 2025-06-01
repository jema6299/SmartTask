import datetime
import threading
import winsound
import pyttsx3
import smtplib
from email.message import EmailMessage
from tkinter import messagebox

EMAIL_SENDER   = "micharby73@gmail.com"
EMAIL_RECEIVER = "micharby73@gmail.com"
EMAIL_PASSWORD = "kdrelaysmeaazugs"

def play_sound_alert():
    winsound.Beep(1000, 500)

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def send_email_reminder(task):
    try:
        msg = EmailMessage()
        msg.set_content(f"Reminder: {task}")
        msg["Subject"] = "Digital Assistant Task Reminder"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def parse_date(date_str):
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError("Date must be YYYY-MM-DD HH:MM or YYYY/MM/DD HH:MM")

def schedule_reminder(task, date_str, repeat, root, tasks, save_tasks, update_task_list):
    try:
        due = parse_date(date_str)
    except ValueError:
        return

    delay = (due - datetime.datetime.now()).total_seconds()
    if delay <= 0:
        return

    def _remind():
        play_sound_alert()
        root.after(0, lambda: messagebox.showinfo("Reminder", f"Reminder: {task}"))
        speak(task)
        send_email_reminder(task)

        if repeat:
            nxt = due + datetime.timedelta(days=1)
            ndate = nxt.strftime("%Y-%m-%d %H:%M")
            tasks.append({"task": task, "date": ndate, "repeat": True})
            save_tasks(tasks)
            update_task_list(tasks, None)  # will re‐populate full list
            schedule_reminder(task, ndate, True, root, tasks, save_tasks, update_task_list)

    threading.Timer(delay, _remind).start()
