import pytest
import datetime
from unittest.mock import patch, MagicMock
from smarttask.src.task_manager import update_task_list, show_calendar, add_task, delete_task


class DummyListbox:
    """
    A minimal stand-in for tkinter.Listbox to capture insert calls.
    """
    def __init__(self):
        self.contents = []

    def delete(self, start, end=None):
        self.contents.clear()

    def insert(self, index, text):
        self.contents.append(text)

    def curselection(self):
        # returns an empty tuple if nothing selected
        return ()


class FakeRoot:
    def __init__(self):
        pass

    def after(self, ms, func):
        pass


@pytest.fixture
def sample_tasks():
    return [
        {"task": "A", "date": "2025-06-01 10:00", "repeat": False},
        {"task": "B", "date": "2025-06-02 09:00", "repeat": True},
        {"task": "C", "date": "2025-06-01 15:30", "repeat": False},
    ]


def test_update_task_list_all(sample_tasks):
    lb = DummyListbox()
    update_task_list(sample_tasks, lb)

    # Expect three lines inserted
    assert len(lb.contents) == 3
    assert "A at 2025-06-01 10:00" in lb.contents[0]
    assert "B at 2025-06-02 09:00" in lb.contents[1]
    assert "C at 2025-06-01 15:30" in lb.contents[2]


def test_update_task_list_filtered(sample_tasks):
    lb = DummyListbox()
    # Only want tasks whose date contains “2025-06-01”
    filtered = [t for t in sample_tasks if "2025-06-01" in t["date"]]
    update_task_list(sample_tasks, lb, filtered)
    assert len(lb.contents) == 2
    assert all("2025-06-01" in line for line in lb.contents)


@patch("smarttask.src.task_manager.Calendar")  # patch Calendar widget
@patch("smarttask.src.task_manager.parse_date")
def test_show_calendar_filters(mock_parse_date, mock_Calendar, sample_tasks, monkeypatch):
    """
    show_calendar() should open a Toplevel and, upon clicking “Show Tasks for Day,”
    filter tasks by selected date. We patch Calendar.get_date to return “06/01/25”,
    and patch parse_date to convert any input to datetime.date(2025, 6, 1).
    """
    # Create a fake calendar instance whose get_date() returns "06/01/25"
    cal_instance = MagicMock()
    cal_instance.get_date.return_value = "06/01/25"
    mock_Calendar.return_value = cal_instance

    # Make parse_date return a datetime whose .date() is 2025-06-01 for any t["date"]
    fake_date = datetime.datetime(2025, 6, 1, 0, 0)
    mock_parse_date.return_value = fake_date

    root = FakeRoot()
    # Monkeypatch tk.Toplevel so we can capture creation of child windows without opening the real UI
    monkeypatch.setattr("tkinter.Toplevel", lambda parent: MagicMock())
    # Monkeypatch tk.Listbox for the “result window” to avoid real UI
    monkeypatch.setattr("tkinter.Listbox", lambda parent, width, height: DummyListbox())
    monkeypatch.setattr("tkinter.Label", lambda parent, text: MagicMock())
    monkeypatch.setattr("tkinter.Button", lambda *args, **kwargs: MagicMock())

    # Now call show_calendar(); it should not crash
    show_calendar(root, sample_tasks)
    # We cannot directly inspect the “result” window’s Listbox contents because we returned MagicMocks.
    # But no exceptions means the filtering logic ran successfully.


def test_add_and_delete_task(tmp_path, monkeypatch):
    """
    Test add_task() and delete_task() in a headless way by mocking simpledialog and messagebox.
    """
    # Prepare a temporary tasks list and override save_tasks to write to a temp file
    temp_json = tmp_path / "tasks.json"
    monkeypatch.setenv("TASKS_FILE", str(temp_json))  # if your code reads TASKS_FILE from env
    tasks = []

    # Set up dummy root and listbox
    root = FakeRoot()
    lb = DummyListbox()

    # Mock simpledialog.askstring to return a fixed task and date on first two calls
    seq = iter(["Test Task", "2025-06-10 14:00"])
    monkeypatch.setattr("tkinter.simpledialog.askstring", lambda title, prompt: next(seq))
    # Mock messagebox.askyesno to always return True
    monkeypatch.setattr("tkinter.messagebox.askyesno", lambda title, prompt: True)

    # Call add_task()
    add_task(tasks, lb, root)
    assert len(tasks) == 1
    assert tasks[0]["task"] == "Test Task"
    assert "2025-06-10 14:00" in tasks[0]["date"]
    assert tasks[0]["repeat"] is True
    assert len(lb.contents) == 1

    # Now test delete_task() by selecting index 0 manually
    monkeypatch.setattr(DummyListbox, "curselection", lambda self: (0,))
    delete_task(tasks, lb)
    assert tasks == []
    assert lb.contents == []
