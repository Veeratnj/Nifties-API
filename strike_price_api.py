from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Tuple
import asyncio
import requests
import os

from dhanhq import DhanContext, MarketFeed
import uvicorn

from fastapi import FastAPI, BackgroundTasks
import time

app = FastAPI()

def long_running_task(task_id: int):
    print(f"🔄 Task {task_id} started")
    time.sleep(5)  # simulate heavy work
    print(f"✅ Task {task_id} completed")

@app.post("/run-task/{task_id}")
async def run_task(task_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task, task_id)
    return {
        "status": "accepted",
        "task_id": task_id
    }

# -------------------- Main --------------------
if __name__ == "__main__":
    uvicorn.run("strike_price_api:app", host="0.0.0.0", port=8001, reload=True)
