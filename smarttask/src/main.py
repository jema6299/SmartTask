# smarttask/src/main.py

import tkinter as tk

from smarttask.src.data_handler  import load_tasks, save_tasks
from smarttask.src.task_manager  import (
    add_task,
    delete_task,
    export_to_excel,
    import_from_excel,
    update_task_list,
    show_calendar
)
from smarttask.src.voice_input   import voice_add_task
from smarttask.src.notifications import schedule_reminder


def main():
    root = tk.Tk()
    root.title("Digital Personal Assistant")
    root.geometry("600x600")

    # Listbox for showing tasks
    task_list = tk.Listbox(root, width=70, height=15)
    task_list.pack(pady=10)

    # Frame for buttons
    btns = tk.Frame(root)
    btns.pack()
    tk.Button(btns, text="Add Task",         command=lambda: add_task(tasks, task_list, root))   .grid(row=0,column=0,padx=5)
    tk.Button(btns, text="Add by Voice",     command=lambda: voice_add_task(tasks, task_list, root)).grid(row=0,column=1,padx=5)
    tk.Button(btns, text="Delete Task",      command=lambda: delete_task(tasks, task_list))     .grid(row=0,column=2,padx=5)
    tk.Button(btns, text="Export to Excel",  command=lambda: export_to_excel(tasks, task_list, root)).grid(row=0,column=3,padx=5)
    tk.Button(btns, text="Import from Excel",command=lambda: import_from_excel(tasks, task_list, root)).grid(row=0,column=4,padx=5)
    tk.Button(btns, text="Show Calendar",    command=lambda: show_calendar(root, tasks))        .grid(row=1,column=1,columnspan=2,pady=10)

    # ---- INIT: load existing tasks and schedule reminders ----
    global tasks
    tasks = load_tasks()
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

    root.mainloop()


if __name__ == "__main__":
    main()
