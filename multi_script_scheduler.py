import time
import subprocess
from datetime import datetime

# ================== CONFIG ==================

TARGET_TIME = "09:10"   # Daily start time

TASKS = [
    {
        "script": "/home/ubuntu/workspace/Nifties-opt/Main.py",
        "venv": "/home/ubuntu/workspace/Nifties-opt/.venv/bin/activate"
    },
    {
        "script": "/home/ubuntu/workspace/Nifties-socket/index_socket.py",
        "venv": "/home/ubuntu/workspace/Nifties-API/.venv/bin/activate"
    },
    {
        "script": "/home/ubuntu/workspace/Nifties-API/dhan_soc.py",
        "venv": "/home/ubuntu/workspace/Nifties-API/.venv/bin/activate"
    }
]

LOG_FILE = "/home/ubuntu/workspace/Nifties-API/multi_script_run.log"

# ================== END CONFIG ==================


def write_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")


def run_task_in_background(script_path, venv_path):
    write_log(f"LAUNCHING (nohup): {script_path}")

    cmd = (
        f"bash -c \"source {venv_path} && "
        f"nohup python3 {script_path} >/dev/null 2>&1 &\""
    )

    subprocess.run(cmd, shell=True)

    write_log(f"STARTED in background: {script_path}")


write_log("===== SCHEDULER STARTED =====")

while True:
    now = datetime.now().strftime("%H:%M")

    if now == TARGET_TIME:
        write_log(">>> 9:10 AM reached. Launching all scripts in background...")

        for task in TASKS:
            run_task_in_background(task["script"], task["venv"])

        write_log(">>> All 3 scripts launched successfully for today.")

        time.sleep(60)  # prevent double trigger

    time.sleep(10)
