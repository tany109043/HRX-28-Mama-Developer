# api.py
import json
import subprocess
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

SCRIPT = "student_affect_monitor.py"   # Make sure this script is in the same folder
POLL_INTERVAL = 0.25                   # Interval to check for new output

app = FastAPI()

# Allow browser requests from anywhere (relax this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_process = None
_latest_output = {}

def read_stdout():
    global _latest_output, _process
    for line in _process.stdout:
        line = line.strip()
        try:
            _latest_output = json.loads(line)
        except json.JSONDecodeError:
            print(f"[WARN] Invalid JSON: {line}")
            continue

def start_script():
    global _process
    if _process and _process.poll() is None:
        return  # Already running

    _process = subprocess.Popen(
        ["python", SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    threading.Thread(target=read_stdout, daemon=True).start()

def stop_script():
    global _process
    if _process and _process.poll() is None:
        _process.terminate()
        _process.wait(timeout=5)

@app.post("/start")
async def start():
    start_script()
    return {"status": "started"}

@app.post("/stop")
async def stop():
    stop_script()
    return {"status": "stopped"}

@app.get("/latest")
async def latest():
    if not (_process and _process.poll() is None):
        raise HTTPException(status_code=400, detail="Emotion analysis not running. Start first.")
    return _latest_output
