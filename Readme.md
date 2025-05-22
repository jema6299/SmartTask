# SmartTask – Digital Personal Assistant

A lightweight desktop app (Python 3.10+) that helps you **add, view, and get reminded of tasks**.

Current MVP features
- Text task entry (dialog)
- Voice task entry (SpeechRecognition + mic)
- One‑time / daily reminders (sound + toast + optional email)
- Calendar view with date filter
- Import / export tasks to Excel (`.xlsx`)
- Local JSON persistence – no server required

---

## 1 Prerequisites
| Requirement | Tested Version | Notes |

| Python      | 3.10+         | <https://python.org> |
| pip         | 23+           | `python -m pip install --upgrade pip` |
| Windows 10/11 | —              | winsound + Win10 toast; on macOS/Linux toast is skipped |
| Microphone  | —              | Needed only for voice input |

---

## 2- Install

```bash
git clone https://github.com/jema6299/SmartTask.git
cd smarttask

# (optional) create and activate a virtual‑env
python -m venv venv
venv\Scripts\activate    # or: source venv/bin/activate

pip install tkcalendar openpyxl pandas pyttsx3 SpeechRecognition pyaudio win10toast

-----

## If PyAudio fails on Windows
..... 
pip install pipwin
pipwin install pyaudio
---------
3- Config – Email Reminders
1-Create a Gmail App Password (4steps):
A- Turn on 2‑Step Verification
https://myaccount.google.com/ → Security → 2‑Step Verification → Get Started

B- Open App Passwords
https://myaccount.google.com/apppasswords

C- Generate
Select Mail, choose Other (Custom) → type SmartTask → Generate

Copy the 16‑character password (e.g. abcd efgh ijkl mnop), remove spaces, and paste into EMAIL_PASSWORD.
--------------------------------------------------------------------------------------------------------
Add Task – type description, date/time, choose repeat

Add by Voice – click Add by Voice, speak, then enter the date

Calendar – Show Calendar → pick a day → Show Tasks for Day

Export / Import – save or load tasks as an Excel file (tasks.xlsx)

Reminders trigger a beep, a toast notification, optional speech, and an email