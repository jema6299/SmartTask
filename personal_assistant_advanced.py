import os
import json
import datetime
import threading
import winsound
import pyttsx3
import speech_recognition as sr
import pandas as pd
import smtplib

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkcalendar import Calendar
from win10toast import ToastNotifier
from email.message import EmailMessage

# ---- CONFIG ----
TASKS_FILE     = "tasks.json"
EMAIL_SENDER   = "Your Email "
EMAIL_RECEIVER = "micharby73@gmail.com"
EMAIL_PASSWORD = "your password "  # your app password

toaster = ToastNotifier()

# ---- LOAD / SAVE ----
def load_tasks():
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

# ---- HELPERS ----
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

# ---- TASK OPERATIONS ----
def add_task():
    task = simpledialog.askstring("New Task", "Enter task description:")
    date = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD or YYYY/MM/DD HH:MM):")
    repeat = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
    if not task or not date:
        return
    try:
        parse_date(date)
    except ValueError:
        messagebox.showerror("Invalid Format", "Use YYYY-MM-DD HH:MM or YYYY/MM/DD HH:MM")
        return

    tasks.append({'task': task, 'date': date, 'repeat': repeat})
    save_tasks(tasks)
    update_task_list()
    schedule_reminder(task, date, repeat)

def delete_task():
    sel = task_list.curselection()
    if not sel:
        return
    del tasks[sel[0]]
    save_tasks(tasks)
    update_task_list()

def export_to_excel():
    path = filedialog.asksaveasfilename(
        title="Save tasks as…",
        initialdir=os.getcwd(),
        defaultextension=".xlsx",
        initialfile="tasks.xlsx",
        filetypes=[("Excel files","*.xlsx"),("All files","*.*")]
    )
    if not path:
        return
    if not path.lower().endswith(".xlsx"):
        path += ".xlsx"
    try:
        pd.DataFrame(tasks).to_excel(path, index=False)
    except Exception as e:
        messagebox.showerror("Export failed", str(e))
    else:
        messagebox.showinfo("Exported", f"Tasks saved to:\n{path}")

def import_from_excel():
    path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if not path:
        return
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        tasks.append({
            'task':   row['task'],
            'date':   row['date'],
            'repeat': bool(row['repeat'])
        })
    save_tasks(tasks)
    update_task_list()
    for t in tasks:
        schedule_reminder(t['task'], t['date'], t.get('repeat', False))
    messagebox.showinfo("Imported", "Tasks imported successfully.")

def update_task_list(filtered=None):
    task_list.delete(0, tk.END)
    for t in (filtered if filtered else tasks):
        task_list.insert(
            tk.END,
            f"{t['task']} at {t['date']} | Repeat: {'Yes' if t['repeat'] else 'No'}"
        )

def schedule_reminder(task, date_str, repeat):
    try:
        due = parse_date(date_str)
    except ValueError:
        return

    delay = (due - datetime.datetime.now()).total_seconds()
    if delay <= 0:
        return

    def remind():
        # 1) play your beep
        play_sound_alert()

        # 2) show a popup on the main thread
        root.after(0, lambda: messagebox.showinfo("Reminder", f"Reminder: {task}"))

        # 3) speak the task out loud
        speak(task)

        # 4) send email (optional)
        send_email_reminder(task)

        # 5) if repeating, schedule next
        if repeat:
            nxt   = due + datetime.timedelta(days=1)
            ndate = nxt.strftime("%Y-%m-%d %H:%M")
            tasks.append({'task': task, 'date': ndate, 'repeat': True})
            save_tasks(tasks)
            update_task_list()
            schedule_reminder(task, ndate, True)

    threading.Timer(delay, remind).start()

def voice_add_task():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as src:
            speak("Say your task")
            audio = r.listen(src)
            spoken = r.recognize_google(audio)
        date = simpledialog.askstring(
            "Due Date",
            f"Enter due date for '{spoken}' (YYYY-MM-DD or YYYY/MM/DD HH:MM):"
        )
        repeat = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
        if not date:
            return
        parse_date(date)
        tasks.append({'task': spoken, 'date': date, 'repeat': repeat})
        save_tasks(tasks)
        update_task_list()
        schedule_reminder(spoken, date, repeat)
    except Exception as e:
        messagebox.showerror("Voice Error", str(e))

def show_calendar():
    win = tk.Toplevel(root)
    win.title("Calendar")
    cal = Calendar(win, selectmode='day')
    cal.pack(pady=10)
    def filter_by_date():
        sel = cal.get_date()
        filtered = [t for t in tasks if sel in t['date']]
        update_task_list(filtered)
    tk.Button(win, text="Show Tasks for Day", command=filter_by_date).pack(pady=10)

# ---- GUI SETUP ----
root = tk.Tk()
root.title("Digital Personal Assistant")
root.geometry("600x600")

task_list = tk.Listbox(root, width=70, height=15)
task_list.pack(pady=10)

btns = tk.Frame(root)
btns.pack()
tk.Button(btns, text="Add Task",         command=add_task)           .grid(row=0,column=0,padx=5)
tk.Button(btns, text="Add by Voice",     command=voice_add_task)     .grid(row=0,column=1,padx=5)
tk.Button(btns, text="Delete Task",      command=delete_task)        .grid(row=0,column=2,padx=5)
tk.Button(btns, text="Export to Excel",  command=export_to_excel)    .grid(row=0,column=3,padx=5)
tk.Button(btns, text="Import from Excel",command=import_from_excel)  .grid(row=0,column=4,padx=5)
tk.Button(btns, text="Show Calendar",    command=show_calendar)      .grid(row=1,column=1,columnspan=2,pady=10)

# ---- INIT ----
tasks = load_tasks()
update_task_list()
for t in tasks:
    schedule_reminder(t['task'], t['date'], t.get('repeat', False))

root.mainloop()
