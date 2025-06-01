import sys
import types

# ──────────────────────────────────────────────────────────────────────────────
# Create dummy speech_recognition and pyaudio modules so that
# `import speech_recognition as sr` and `with sr.Microphone()` inside
# voice_input.py do not fail.
# We supply:
#   - sr.Recognizer() having listen() and recognize_google()
#   - sr.Microphone() context manager stub
# ──────────────────────────────────────────────────────────────────────────────
dummy_sr = types.ModuleType("speech_recognition")
class DummyRecognizer:
    def listen(self, src):
        return "dummy_audio"
    def recognize_google(self, audio):
        return "Hello Task"
dummy_sr.Recognizer = DummyRecognizer

class DummyMicrophone:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        pass
dummy_sr.Microphone = DummyMicrophone

# Insert dummy module before voice_input imports it
sys.modules["speech_recognition"] = dummy_sr

# Also stub out pyaudio, since speech_recognition often imports it
sys.modules["pyaudio"] = types.ModuleType("pyaudio")
# ──────────────────────────────────────────────────────────────────────────────

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


@patch("smarttask.src.voice_input.speak")
@patch("smarttask.src.voice_input.parse_date")
@patch("smarttask.src.voice_input.schedule_reminder")
def test_voice_add_task_success(
        mock_schedule,
        mock_parse_date,
        mock_speak,
        tasks_list,
        monkeypatch
):
    """
    Simulate a successful voice input:
      - Recognizer().listen() returns dummy audio
      - recognize_google(audio) returns "Hello Task"
      - simpledialog.askstring returns a valid date string
      - messagebox.askyesno returns False (no repeat)
    """
    # Patch simpledialog.askstring to return a date string
    seq = iter(["2025-07-01 11:00"])
    monkeypatch.setattr(
        "tkinter.simpledialog.askstring",
        lambda title, prompt: next(seq)
    )
    # Patch messagebox.askyesno to return False (no repeat)
    monkeypatch.setattr(
        "tkinter.messagebox.askyesno",
        lambda title, prompt: False
    )

    # Ensure parse_date does not raise
    mock_parse_date.return_value = None

    dummy_lb = DummyListbox()
    root = FakeRoot()

    # Call voice_add_task
    voice_add_task(tasks_list, dummy_lb, root)

    # Verify one task was appended
    assert len(tasks_list) == 1
    assert tasks_list[0]["task"] == "Hello Task"
    assert "2025-07-01 11:00" in tasks_list[0]["date"]
    assert tasks_list[0]["repeat"] is False

    # schedule_reminder must have been called once
    mock_schedule.assert_called_once()


@patch("smarttask.src.voice_input.sr.Recognizer")
def test_voice_add_task_recognition_error(
        mock_recognizer,
        tasks_list,
):
    """
    Simulate recognize_google throwing an exception – voice_add_task should
    catch it and call messagebox.showerror without appending any task.
    """
    recog_instance = MagicMock()
    mock_recognizer.return_value = recog_instance
    recog_instance.listen.return_value = "dummy audio"
    recog_instance.recognize_google.side_effect = Exception("Recognition Failed")

    # Patch messagebox.showerror to capture the error message
    called = {"msg": None}
    def fake_showerror(title, message):
        called["msg"] = message

    import tkinter.messagebox as mb
    mb_showerror = mb.showerror
    mb.showerror = fake_showerror

    dummy_lb = DummyListbox()
    root = FakeRoot()

    voice_add_task(tasks_list, dummy_lb, root)

    # No tasks should be added, and showerror should have been called
    assert tasks_list == []
    assert "Recognition Failed" in called["msg"]

    # Restore original showerror
    mb.showerror = mb_showerror
