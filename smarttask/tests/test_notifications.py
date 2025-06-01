# tests/test_notifications.py
import pytest
import datetime
from unittest.mock import patch, MagicMock

# Adjust imports to My project path
from smarttask.src.notifications import parse_date, send_email_reminder, schedule_reminder

class TestNotifications:
    @pytest.mark.parametrize("date_str,expected", [
        ("2025-06-01 10:00", datetime.datetime(2025, 6, 1, 10, 0)),
        ("2025/06/01 10:00", datetime.datetime(2025, 6, 1, 10, 0))
    ])
    def test_parse_date_valid(self, date_str, expected):
        result = parse_date(date_str)
        assert result == expected

    @pytest.mark.parametrize("bad_str", [
        "06-01-2025 10:00",
        "2025-06-01",
        "abcd",
        "2025/06/01"
    ])
    def test_parse_date_invalid(self, bad_str):
        with pytest.raises(ValueError):
            parse_date(bad_str)

    @patch("smarttask.src.notifications.smtplib.SMTP_SSL")
    def test_send_email_reminder_success(self, mock_smtp):
        """
        Mock SMTP_SSL so no real email is sent. Just assert no exception is raised.
        """
        # Prepare a dummy SMTP instance
        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        # Call send_email_reminder with a sample task
        send_email_reminder("Test Task")
        smtp_instance.login.assert_called()  # login must have been called
        smtp_instance.send_message.assert_called()

    @patch("smarttask.src.notifications.messagebox.showinfo")
    @patch("smarttask.src.notifications.play_sound_alert")
    @patch("smarttask.src.notifications.speak")
    @patch("smarttask.src.notifications.send_email_reminder")
    def test_schedule_reminder_immediate_and_repeat_false(
            self,
            mock_email,
            mock_speak,
            mock_beep,
            mock_showinfo,
    ):
        """
        Test scheduling with a due time 1 second in the future, repeat=False.
        We fast-forward time by patching datetime.datetime now() to be just before the scheduled.
        """
        # Create a “fake” root with an .after() we can ignore
        class FakeRoot:
            def after(self, ms, func):
                func()

        fake_root = FakeRoot()
        tasks = []
        save_tasks = lambda x: None
        update_task_list = lambda x, y: None

        # Build a due-time 1 second from “now”
        future = datetime.datetime.now() + datetime.timedelta(seconds=1)
        date_str = future.strftime("%Y-%m-%d %H:%M")

        # We patch parse_date inside schedule_reminder so that parse_date(date_str) returns “future”
        with patch("smarttask.src.notifications.parse_date", return_value=future):
            schedule_reminder(
                task="Task!",
                date_str=date_str,
                repeat=False,
                root=fake_root,
                tasks=tasks,
                save_tasks=save_tasks,
                update_task_list=update_task_list
            )
            # Wait 1.5 seconds so that the Timer has a chance to fire
            import time; time.sleep(1.5)

            # Now our mocks should have been called once
            mock_beep.assert_called_once()
            mock_showinfo.assert_called_once_with("Reminder", "Reminder: Task!")
            mock_speak.assert_called_once_with("Task!")
            mock_email.assert_called_once_with("Task!")
