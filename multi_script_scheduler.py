import subprocess
import datetime
import time
import os
import signal

# --- CONFIG ---
START_HOUR = 9
START_MINUTE = 5

STOP_HOUR = 15
STOP_MINUTE = 35

CHECK_INTERVAL = 30  # seconds

dhan_process = None
multi_process = None


def is_weekday():
    return datetime.datetime.now().weekday() < 5  # 0=Mon, 4=Fri


def current_time():
    now = datetime.datetime.now()
    return now.hour, now.minute


def start_processes():
    global dhan_process, multi_process

    print("Starting both socket processes...")

    # Activate venv not needed if using full python path
    dhan_process = subprocess.Popen(
        ["/home/ubuntu/workspace/Nifties-API/.venv/bin/python3",
         "/home/ubuntu/workspace/Nifties-API/dhan_soc.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    multi_process = subprocess.Popen(
        ["/home/ubuntu/workspace/Nifties-API/.venv/bin/python3",
         "/home/ubuntu/workspace/Nifties-socket/Multi_index_socket.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def stop_processes():
    global dhan_process, multi_process

    print("Stopping both socket processes...")

    if dhan_process:
        dhan_process.kill()
        dhan_process = None

    if multi_process:
        multi_process.kill()
        multi_process = None


def should_start():
    hour, minute = current_time()
    return hour == START_HOUR and minute == START_MINUTE


def should_stop():
    hour, minute = current_time()
    return hour == STOP_HOUR and minute == STOP_MINUTE


print("Market Scheduler Started...")

while True:
    try:
        if is_weekday():

            if should_start():
                if dhan_process is None and multi_process is None:
                    start_processes()
                    time.sleep(60)  # prevent duplicate start

            if should_stop():
                if dhan_process or multi_process:
                    stop_processes()
                    time.sleep(60)  # prevent duplicate stop

        time.sleep(CHECK_INTERVAL)

    except Exception:
        time.sleep(10)