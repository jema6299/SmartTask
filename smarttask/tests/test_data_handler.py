# tests/test_data_handler.py
import os
import json
import tempfile


from smarttask.src.data_handler import load_tasks, save_tasks, TASKS_FILE


class TestDataHandler:
    def setup_method(self):
        # Create a temporary JSON file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name

    def teardown_method(self):
        # Remove temporary file
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_load_tasks_file_missing(self, monkeypatch):
        # Simulate TASKS_FILE not existing
        monkeypatch.setattr("smarttask.src.data_handler.TASKS_FILE", self.temp_file)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

        tasks = load_tasks()
        assert isinstance(tasks, list)
        assert tasks == []

    def test_load_tasks_file_exists(self, monkeypatch):
        # Write sample JSON to temp_file and load
        test_data = [{"task": "A", "date": "2025-06-01 09:00", "repeat": False}]
        with open(self.temp_file, "w") as f:
            json.dump(test_data, f)

        monkeypatch.setattr("smarttask.src.data_handler.TASKS_FILE", self.temp_file)
        result = load_tasks()
        assert result == test_data

    def test_save_tasks_and_load(self, monkeypatch):
        # Save tasks into temp_file, then load and verify
        monkeypatch.setattr("smarttask.src.data_handler.TASKS_FILE", self.temp_file)
        data = [{"task": "B", "date": "2025-07-01 10:00", "repeat": True}]
        save_tasks(data)

        with open(self.temp_file, "r") as f:
            raw = json.load(f)

        assert raw == data

        # Now load_tasks should return the same data
        result = load_tasks()
        assert result == data
