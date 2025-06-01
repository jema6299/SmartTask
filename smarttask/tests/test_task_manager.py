import sys
import types

# ──────────────────────────────────────────────────────────────────────────────
# Create a dummy tkcalendar module so that `from tkcalendar import Calendar`
# inside task_manager.py does not fail. Provide a stub Calendar class
# with pack() and get_date() so show_calendar() can call both.
# ──────────────────────────────────────────────────────────────────────────────
dummy_tkcalendar = types.ModuleType("tkcalendar")

class DummyCalendar:
    def __init__(self, parent, selectmode=None, date_pattern=None):
        pass
    def pack(self, **kwargs):
        pass
    def get_date(self):
        return "06/01/25"

dummy_tkcalendar.Calendar = DummyCalendar
sys.modules["tkcalendar"] = dummy_tkcalendar
# ──────────────────────────────────────────────────────────────────────────────

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

    assert len(lb.contents) == 3
    assert "A at 2025-06-01 10:00" in lb.contents[0]
    assert "B at 2025-06-02 09:00" in lb.contents[1]
    assert "C at 2025-06-01 15:30" in lb.contents[2]


def test_update_task_list_filtered(sample_tasks):
    lb = DummyListbox()
    filtered = [t for t in sample_tasks if "2025-06-01" in t["date"]]
    update_task_list(sample_tasks, lb, filtered)
    assert len(lb.contents) == 2
    assert all("2025-06-01" in line for line in lb.contents)


@patch("smarttask.src.task_manager.parse_date")
@patch("tkinter.Toplevel")
@patch("tkinter.Listbox")
@patch("tkinter.Label")
@patch("tkinter.Button")
def test_show_calendar_filters(
        mock_button,
        mock_label,
        mock_listbox,
        mock_toplevel,
        mock_parse_date,
        sample_tasks
):
    """
    show_calendar() should open a Toplevel and, upon clicking "Show Tasks for Day",
    filter tasks by selected date. We patch parse_date to produce 2025-06-01 for any input.
    """
    fake_date = datetime.datetime(2025, 6, 1, 0, 0)
    mock_parse_date.return_value = fake_date

    root = FakeRoot()
    show_calendar(root, sample_tasks)


def test_add_and_delete_task(tmp_path, monkeypatch):
    temp_json = tmp_path / "tasks.json"
    monkeypatch.setenv("TASKS_FILE", str(temp_json))
    tasks = []

    root = FakeRoot()
    lb = DummyListbox()

    seq = iter(["Test Task", "2025-06-10 14:00"])
    monkeypatch.setattr("tkinter.simpledialog.askstring", lambda title, prompt: next(seq))
    monkeypatch.setattr("tkinter.messagebox.askyesno", lambda title, prompt: True)

    add_task(tasks, lb, root)
    assert len(tasks) == 1
    assert tasks[0]["task"] == "Test Task"
    assert "2025-06-10 14:00" in tasks[0]["date"]
    assert tasks[0]["repeat"] is True
    assert len(lb.contents) == 1

    monkeypatch.setattr(DummyListbox, "curselection", lambda self: (0,))
    delete_task(tasks, lb)
    assert tasks == []
    assert lb.contents == []
