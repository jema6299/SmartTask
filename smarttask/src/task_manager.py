# smarttask/src/task_manager.py

import os
import datetime
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkcalendar import Calendar

from smarttask.src.data_handler  import load_tasks, save_tasks
from smarttask.src.notifications  import parse_date, schedule_reminder

# ---- TASK OPERATIONS ----

def add_task(tasks, task_list, root):
    """
    Prompt the user for a new task, due date, and whether to repeat daily.
    Save it, update the listbox, and schedule the reminder.
    """
    task_text = simpledialog.askstring("New Task", "Enter task description:")
    date_str  = simpledialog.askstring(
        "Due Date",
        "Enter due date (YYYY-MM-DD or YYYY/MM/DD HH:MM):"
    )
    repeat = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
    if not task_text or not date_str:
        return

    try:
        parse_date(date_str)
    except ValueError:
        messagebox.showerror("Invalid Format", "Use YYYY-MM-DD HH:MM or YYYY/MM/DD HH:MM")
        return

    tasks.append({"task": task_text, "date": date_str, "repeat": repeat})
    save_tasks(tasks)
    update_task_list(tasks, task_list)

    # Pass in all required arguments so 'schedule_reminder' never sees task_list=None
    schedule_reminder(
        task=task_text,
        date_str=date_str,
        repeat=repeat,
        root=root,
        tasks=tasks,
        save_tasks=save_tasks,
        update_task_list=lambda t, tb=task_list: update_task_list(t, tb)
    )


def delete_task(tasks, task_list):
    """
    Remove the selected task from tasks[], save, and update the listbox.
    """
    sel = task_list.curselection()
    if not sel:
        return
    del tasks[sel[0]]
    save_tasks(tasks)
    update_task_list(tasks, task_list)


def export_to_excel(tasks, task_list, root):
    """
    Open a file-save dialog and dump tasks to an .xlsx.
    """
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


def import_from_excel(tasks, task_list, root):
    """
    Open a file-open dialog, read tasks from the .xlsx, add to tasks[], save and reschedule.
    """
    path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if not path:
        return

    df = pd.read_excel(path)
    for _, row in df.iterrows():
        tasks.append({
            "task":   row["task"],
            "date":   row["date"],
            "repeat": bool(row["repeat"])
        })

    save_tasks(tasks)
    update_task_list(tasks, task_list)

    for t in tasks:
        schedule_reminder(
            task=t["task"],
            date_str=t["date"],
            repeat=t.get("repeat", False),
            root=root,
            tasks=tasks,
            save_tasks=save_tasks,
            update_task_list=lambda tlist, tb=task_list: update_task_list(tlist, tb)
        )

    messagebox.showinfo("Imported", "Tasks imported successfully.")


def update_task_list(tasks, task_list, filtered=None):
    """
    Clear and repopulate the given Listbox with either all tasks (if filtered=None)
    or the provided filtered list.
    """
    if task_list is None:
        return

    task_list.delete(0, tk.END)
    for t in (filtered if filtered else tasks):
        task_list.insert(
            tk.END,
            f"{t['task']} at {t['date']} | Repeat: {'Yes' if t['repeat'] else 'No'}"
        )


def show_calendar(root, tasks):
    """
    Opens a small calendar widget. When the user clicks “Show Tasks for Day,”
    a new window (Toplevel) pops up listing only that day’s tasks.
    """
    cal_win = tk.Toplevel(root)
    cal_win.title("Select a Date")
    cal_win.geometry("300x300")

    cal = Calendar(cal_win, selectmode="day", date_pattern="mm/dd/yy")
    cal.pack(pady=10)

    def filter_by_date():
        try:
            sel_date = datetime.datetime.strptime(cal.get_date(), "%m/%d/%y").date()
            filtered = []
            for t in tasks:
                try:
                    task_date = parse_date(t["date"]).date()
                    if task_date == sel_date:
                        filtered.append(t)
                except Exception:
                    pass
            # Show filtered results in a brand-new Toplevel
            result_win = tk.Toplevel(root)
            result_win.title(f"Tasks on {sel_date}")
            lb = tk.Listbox(result_win, width=50, height=10)
            lb.pack(pady=10)
            update_task_list(tasks, lb, filtered)
        except Exception:
            messagebox.showerror("Error", "Could not parse selected date.")

    tk.Button(cal_win, text="Show Tasks for Day", command=filter_by_date).pack(pady=10)
