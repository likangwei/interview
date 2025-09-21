from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
import os
import time

from fastapi.staticfiles import StaticFiles
import os

# 确保目录存在
os.makedirs("./videos", exist_ok=True)

from concurrent.futures import ThreadPoolExecutor
import subprocess

executor = ThreadPoolExecutor(max_workers=4)  # 或更多，根据机器


TASKS = {}
def export_video_task(stream_id, task_id, event_ts):
    STREAMS = {
        "K0123": "rtsp://host.docker.internal:8554/mystream",
    }
    rtsp_url = STREAMS.get(stream_id)
    if not rtsp_url:
        TASKS[task_id]["status"] = "failed"
        return

    video_filename = f"{task_id}.mp4"
    output_path = f"./videos/{video_filename}"

    # 标记任务为运行中
    TASKS[task_id]["status"] = "running"

    # FFmpeg 命令
    cmd = f"ffmpeg -rtsp_transport tcp -probesize 5000000 -analyzeduration 5000000 -i {rtsp_url} -t 30 -c copy {output_path}"
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        TASKS[task_id]["status"] = "done"
        TASKS[task_id]["video_url"] = f"http://localhost:8000/videos/{video_filename}"
    else:
        TASKS[task_id]["status"] = "failed"


app = FastAPI()

# 挂载静态目录
app.mount("/videos", StaticFiles(directory="./videos"), name="videos")

class EventIn(BaseModel):
    stream_id: str
    event_ts: int


@app.post("/event")
def post_event(evt: EventIn):
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": "pending", "video_url": None}

    # 提交到线程池异步执行
    executor.submit(export_video_task, evt.stream_id, task_id, evt.event_ts)

    return {
        "task_id": task_id,
        "status": "accepted",
        "detailUrl": f"/event/{task_id}"
    }


@app.get("/event/{task_id}")
def get_event(task_id: str):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
