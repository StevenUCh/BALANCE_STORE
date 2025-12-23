import webbrowser
import threading
import subprocess
import sys
import time
import os

def open_browser():
    time.sleep(2)
    webbrowser.open_new("http://127.0.0.1:5716")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Thread(target=open_browser, daemon=True).start()

    subprocess.call([sys.executable, "app.py"])
