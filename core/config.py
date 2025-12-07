import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    GG_SHEET_KEY = os.getenv("GG_SHEET_KEY", "")
    NETPIE_CLIENT_ID = os.getenv("NETPIE_CLIENT_ID", "")
    NETPIE_TOKEN = os.getenv("NETPIE_TOKEN", "")
    NETPIE_SECRET = os.getenv("NETPIE_SECRET", "")

    PATH_PING = os.getenv("PATH_PING", "http://localhost")
    TIME_PING = int(os.getenv("TIME_PING", 5))  # as minutes
