import os
from datetime import datetime
from io import BytesIO

import httpx
import pandas as pd
import pytz
import soundfile as sf
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Response
from gtts import gTTS

from core.config import Config
from utils.google_sheet import get_task_gg_sheet, update_task_gg_sheet
from utils.netpie import mqtt_send

app = FastAPI()


@app.get("/next_alert")
def check_next_alert():
    next_tasks = pd.read_csv("./temp/next_task.csv")
    if next_tasks.shape[0] <= 0:
        return Response(content="No task exists", status_code=404)
    top_task = next_tasks.iloc[0]
    tts = gTTS(text=top_task["title"], lang="th")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    try:
        data, samplerate = sf.read(mp3_fp)
        wav_fp = BytesIO()
        sf.write(wav_fp, data, samplerate, format="WAV", subtype="PCM_16")
        wav_fp.seek(0)
        return Response(content=wav_fp.getvalue(), media_type="audio/wav")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return Response(content=f"Audio conversion failed: {str(e)}", status_code=500)
    finally:
        next_tasks = next_tasks.iloc[1:]
        update_task_gg_sheet(id=top_task["id"].item(), status="complete")
        mqtt_send(topic="@msg/task", payload={"status": 0})
        if next_tasks.shape[0] > 0:
            mqtt_send(topic="@msg/task", payload={"status": 1})
        next_tasks.to_csv("./temp/next_task.csv", index=False)


@app.get("/")
def check_status() -> dict:
    return {"status": "ok"}


def job_task():
    get_task_gg_sheet()
    df = pd.read_csv("./temp/task.csv")
    now = datetime.now(pytz.timezone("Asia/Bangkok"))
    df["date"] = pd.to_datetime(df["date"])
    target_time = now.replace(second=0, microsecond=0)

    matched_rows = df[
        (df["date"].dt.floor("min") == target_time) & (df["status"] == "uncomplete")
    ]
    if matched_rows.shape[0] == 0:
        return None
    if os.path.exists("./temp/next_task.csv"):
        next_alert_df = pd.read_csv("./temp/next_task.csv")
        union_df = pd.concat([next_alert_df, matched_rows]).drop_duplicates(
            inplace=False, ignore_index=True
        )
        union_df.to_csv("./temp/next_task.csv", index=False)
    else:
        matched_rows.to_csv("./temp/next_task.csv", index=False)
    # send mqtt
    mqtt_send(topic="@msg/task", payload={"status": 1})


async def call_self():
    url = f"{Config.PATH_PING}/"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            print("Ping:", r.text)
        except Exception as e:
            print("Error calling self:", e)


@app.on_event("startup")
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_task, "interval", minutes=0.4)
    scheduler.add_job(call_self, "interval", minutes=Config.TIME_PING)
    scheduler.start()


if __name__ == "__main__":
    get_task_gg_sheet()
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_includes=["."],
    )
