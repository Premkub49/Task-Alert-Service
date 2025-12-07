import json

import pandas as pd
import requests as req

from core.config import Config


def get_task_gg_sheet():
    response = req.get(f"https://script.google.com/macros/s/{Config.GG_SHEET_KEY}/exec")

    if response.status_code != 200:
        print(response.status_code)
        return None
    # print(f"Response: {response.text}")
    dict_response = json.loads(response.text)
    # print(f"Dict: {dict_response}")
    df = pd.DataFrame(dict_response["data"])
    df.to_csv("temp/task.csv", index=False)
    return df


def update_task_gg_sheet(id: int, title=None, date=None, status=None) -> bool:
    payload = {
        "id": id,
    }
    if title is not None:
        payload["title"] = title
    if date is not None:
        payload["date"] = date
    if status is not None:
        payload["status"] = status
    # print(f"Payload: {payload}")
    response = req.post(
        f"https://script.google.com/macros/s/{Config.GG_SHEET_KEY}/exec?action=put",
        json=payload,
    )

    if response.status_code != 200:
        print(response.status_code)
        return False
    return True
