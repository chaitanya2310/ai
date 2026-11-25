import subprocess

api = subprocess.Popen(
    ["uvicorn", "api:app", "--reload"]
)

ui = subprocess.Popen(
    ["streamlit", "run", "ui.py"]
)

api.wait()
ui.wait()