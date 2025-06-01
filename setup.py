from setuptools import setup, find_packages

setup(
    name="SmartTask",
    version="0.1.0",
    author="Michael Mirhom",
    author_email="micharby73@gmail.com",
    description="SmartTask: Digital Personal Assistant (Phase I)",
    packages=find_packages(where="smarttask"),
    package_dir={"": "smarttask"},
    install_requires=[
        "tkcalendar==1.6.1",
        "pandas==1.3.0",
        "openpyxl==3.0.7",
        "SpeechRecognition==3.8.1",
        "pyttsx3==2.90",
        "win10toast==0.9",
        "pyaudio>=0.2.11",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "smarttask = src.main:main",  # if you refactor `main.py` to have a main() function
        ],
    },
)
