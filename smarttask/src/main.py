from smarttask.src.data_handler   import load_tasks
from smarttask.src.task_manager   import (
    add_task,
    delete_task,
    export_to_excel,
    import_from_excel,
    update_task_list,
    show_calendar
)
from smarttask.src.voice_input    import voice_add_task
from smarttask.src.notifications  import schedule_reminder

# ---- GUI SETUP ----
root = tk.Tk()
root.title("Digital Personal Assistant")
root.geometry("600x600")

task_list = tk.Listbox(root, width=70, height=15)
task_list.pack(pady=10)

btns = tk.Frame(root)
btns.pack()
tk.Button(btns, text="Add Task",          command=lambda: add_task(tasks, task_list, root)).grid(row=0,column=0,padx=5)
tk.Button(btns, text="Add by Voice",      command=lambda: voice_add_task(tasks, task_list, root)).grid(row=0,column=1,padx=5)
tk.Button(btns, text="Delete Task",       command=lambda: delete_task(tasks, task_list)).grid(row=0,column=2,padx=5)
tk.Button(btns, text="Export to Excel",   command=lambda: export_to_excel(tasks)).grid(row=0,column=3,padx=5)
tk.Button(btns, text="Import from Excel", command=lambda: import_from_excel(tasks, task_list, root)).grid(row=0,column=4,padx=5)
tk.Button(btns, text="Show Calendar",     command=lambda: show_calendar(root, tasks)).grid(row=1,column=1,columnspan=2,pady=10)

# ---- INIT ----
tasks = load_tasks()
update_task_list(tasks, task_list)

for t in tasks:
    schedule_reminder(t["task"], t["date"], t.get("repeat", False), root, tasks, load_tasks.__self__ if False else None, update_task_list)
    # Note: the `save_tasks` reference is passed implicitly inside task_manager/voice_input calls

root.mainloop()
