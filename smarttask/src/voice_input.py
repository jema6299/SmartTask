# smarttask/src/voice_input.py

import speech_recognition as sr
from tkinter import messagebox, simpledialog

from smarttask.src.notifications import speak, parse_date, schedule_reminder
from smarttask.src.data_handler  import save_tasks
from smarttask.src.task_manager  import update_task_list


def voice_add_task(tasks, task_list, root):
    """
    Use the microphone to capture a spoken task, then prompt for a due date.
    Save it, update the Listbox, and schedule a reminder.
    """
    try:
        r = sr.Recognizer()
        with sr.Microphone() as src:
            speak("Say your task")
            audio = r.listen(src)
            spoken = r.recognize_google(audio)

        date_str = simpledialog.askstring(
            "Due Date",
            f"Enter due date for '{spoken}' (YYYY-MM-DD or YYYY/MM/DD HH:MM):"
        )
        repeat = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
        if not date_str:
            return

        parse_date(date_str)  # raises ValueError if invalid

        tasks.append({"task": spoken, "date": date_str, "repeat": repeat})
        save_tasks(tasks)
        update_task_list(tasks, task_list)

        # Pass in the real Listbox so reminder thread can update it later
        schedule_reminder(
            task=spoken,
            date_str=date_str,
            repeat=repeat,
            root=root,
            tasks=tasks,
            save_tasks=save_tasks,
            update_task_list=lambda tlist, tb=task_list: update_task_list(tlist, tb)
        )

    except Exception as e:
        messagebox.showerror("Voice Error", str(e))
