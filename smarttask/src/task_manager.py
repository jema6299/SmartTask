import datetime
import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkcalendar import Calendar
from smarttask.src.data_handler   import load_tasks, save_tasks
from smarttask.src.notifications  import parse_date, schedule_reminder

def add_task(tasks, task_list, root):
    task_desc = simpledialog.askstring("New Task", "Enter task description:")
    date_str  = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD or YYYY/MM/DD HH:MM):")
    repeat    = messagebox.askyesno("Repeat Daily?", "Repeat this task every day?")
    if not task_desc or not date_str:
        return

    try:
        parse_date(date_str)
    except ValueError:
        messagebox.showerror("Invalid Format", "Use YYYY-MM-DD HH:MM or YYYY/MM/DD HH:MM")
        return

    tasks.append({"task": task_desc, "date": date_str, "repeat": repeat})
    save_tasks(tasks)
    update_task_list(tasks, task_list)
    schedule_reminder(task_desc, date_str, repeat, root, tasks, save_tasks, update_task_list)

def delete_task(tasks, task_list):
    sel = task_list.curselection()
    if not sel:
        return
    del tasks[sel[0]]
    save_tasks(tasks)
    update_task_list(tasks, task_list)

def export_to_excel(tasks):
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
    path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if not path:
        return
    try:
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
            schedule_reminder(t["task"], t["date"], t.get("repeat", False), root, tasks, save_tasks, update_task_list)
        messagebox.showinfo("Imported", "Tasks imported successfully.")
    except Exception as e:
        messagebox.showerror("Import failed", str(e))

def update_task_list(tasks, task_list, filtered=None):
    task_list.delete(0, tk.END)
    for t in (filtered if filtered else tasks):
        task_list.insert(
            tk.END,
            f"{t['task']} at {t['date']} | Repeat: {'Yes' if t['repeat'] else 'No'}"
        )

def show_calendar(root, tasks):
    """
    Opens a small calendar widget.  When the user clicks
    “Show Tasks for Day,” a brand-new window will pop up
    showing only the tasks that fall on the selected date.
    """
    cal_win = tk.Toplevel(root)
    cal_win.title("Select a Date")
    cal_win.geometry("300x300")

    cal = Calendar(cal_win, selectmode="day", date_pattern="mm/dd/yy")
    cal.pack(pady=10)

    def filter_and_show():
        try:
            # parse the selected date (mm/dd/yy) into a datetime.date
            sel_date = datetime.datetime.strptime(cal.get_date(), "%m/%d/%y").date()
        except Exception:
            messagebox.showerror("Error", "Could not parse selected date.")
            return

        # collect all tasks whose date (parsed) matches:
        filtered = []
        for t in tasks:
            try:
                d = parse_date(t["date"]).date()
                if d == sel_date:
                    filtered.append(t)
            except Exception:
                continue

        # now open a new window to list those “filtered” tasks
        result_win = tk.Toplevel(root)
        result_win.title(f"Tasks on {sel_date.strftime('%Y-%m-%d')}")
        result_win.geometry("400x300")

        if not filtered:
            lbl = tk.Label(result_win, text="No tasks for this date.")
            lbl.pack(pady=20)
            return

        # If there are tasks, show them in a Listbox (or Labels)
        lb = tk.Listbox(result_win, width=60, height=15)
        lb.pack(pady=10, padx=10, fill="both", expand=True)

        for t in filtered:
            lb.insert(
                tk.END,
                f"{t['task']}  @  {t['date']}  |  Repeat: {'Yes' if t['repeat'] else 'No'}"
            )

    btn = tk.Button(cal_win, text="Show Tasks for Day", command=filter_and_show)
    btn.pack(pady=10)