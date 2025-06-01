import pytest
from unittest.mock import patch, MagicMock

from smarttask.src.voice_input import voice_add_task


class DummyListbox:
    def __init__(self):
        self.contents = []

    def delete(self, start, end=None):
        self.contents.clear()

    def insert(self, index, text):
        self.contents.append(text)


class FakeRoot:
    def after(self, ms, func):
        pass


@pytest.fixture
def tasks_list(tmp_path, monkeypatch):
    temp_json = tmp_path / "tasks.json"
    monkeypatch.setenv("TASKS_FILE", str(temp_json))
    return []


@patch("smarttask.src.voice_input.sr.Recognizer")
@patch("smarttask.src.voice_input.sr.Microphone")
@patch("smarttask.src.voice_input.speak")
@patch("smarttask.src.voice_input.parse_date")
@patch("smarttask.src.voice_input.schedule_reminder")
def test_voice_add_task_success(
        mock_schedule,
        mock_parse_date,
        mock_speak,
        mock_microphone,
        mock_recognizer,
        tasks_list,
        monkeypatch
):
    """
    Simulate a successful voice input:
      - Recognizer().listen() yields audio
      - recognize_google(audio) returns "Hello Task"
      - simpledialog.askstring returns a valid date string
      - messagebox.askyesno returns False
    """
    # 1) Set up Recognizer().listen() → audio data (not actually used)
    recog_instance = MagicMock()
    mock_recognizer.return_value = recog_instance
    recog_instance.listen.return_value = "dummy audio"
    recog_instance.recognize_google.return_value = "Hello Task"

    # 2) Patch simpledialog.askstring to return a date string
    seq = iter(["2025-07-01 11:00"])
    monkeypatch.setattr(
        "tkinter.simpledialog.askstring",
        lambda title, prompt: next(seq)
    )
    # 3) Patch messagebox.askyesno to return False (no repeat)
    monkeypatch.setattr(
        "tkinter.messagebox.askyesno",
        lambda title, prompt: False
    )

    # 4) Also patch parse_date so it doesn’t raise error
    mock_parse_date.return_value = None

    # 5) Dummy Listbox and root
    dummy_lb = DummyListbox()
    root = FakeRoot()

    # Call voice_add_task
    voice_add_task(tasks_list, dummy_lb, root)

    # Verify tasks_list now has 1 entry
    assert len(tasks_list) == 1
    assert tasks_list[0]["task"] == "Hello Task"
    assert "2025-07-01 11:00" in tasks_list[0]["date"]
    assert tasks_list[0]["repeat"] is False

    # schedule_reminder must have been called once
    mock_schedule.assert_called_once()


@patch("smarttask.src.voice_input.sr.Recognizer")
@patch("smarttask.src.voice_input.sr.Microphone")
def test_voice_add_task_recognition_error(
        mock_microphone,
        mock_recognizer,
        tasks_list,
):
    """
    Simulate recognize_google throwing an exception – should pop up a messagebox.
    """
    recog_instance = MagicMock()
    mock_recognizer.return_value = recog_instance
    recog_instance.listen.return_value = "dummy audio"
    recog_instance.recognize_google.side_effect = Exception("Recognition Failed")

    # Patch messagebox.showerror to capture error
    called = {"msg": None}
    def fake_showerror(title, message):
        called["msg"] = message

    import tkinter.messagebox as mb
    mb_showerror = mb.showerror
    mb.showerror = fake_showerror

    # Dummy Listbox and root
    dummy_lb = DummyListbox()
    root = FakeRoot()

    # Call voice_add_task
    voice_add_task(tasks_list, dummy_lb, root)

    # Tasks list must still be empty, and showerror called
    assert tasks_list == []
    assert "Recognition Failed" in called["msg"]

    # Restore original showerror
    mb.showerror = mb_showerror
