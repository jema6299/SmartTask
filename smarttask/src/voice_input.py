import speech_recognition as sr
from tkinter import messagebox, simpledialog

from smarttask.src.notifications  import speak, parse_date, schedule_reminder
from smarttask.src.data_handler   import save_tasks
from smarttask.src.task_manager   import update_task_list

def voice_add_task(tasks, task_list, root):
    try:
        r = sr.Recognizer()
        with sr.Microphone() as src:
            speak("Say your task")
            audio   = r.listen(src)
            spoken  = r.recognize_google(audio)
        date_str = simpledialog.askstring(
            "Due Date",
            f"Enter due date for '{spoken}' (YYYY-MM-DD or YYYY/MM/DD HH:MM):"
        )
        repeat = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
        if not date_str:
            return
        parse_date(date_str)
        tasks.append({"task": spoken, "date": date_str, "repeat": repeat})
        save_tasks(tasks)
        update_task_list(tasks, task_list)
        schedule_reminder(spoken, date_str, repeat, root, tasks, save_tasks, update_task_list)
    except Exception as e:
        messagebox.showerror("Voice Error", str(e))
