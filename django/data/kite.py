from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
import requests

KITE_API_KEY = "tw96psyyds0yj8vj"
KITE_API_SECRET = "3iewov9onkbytzramkt263r9lvcdzks9"
ACCESS_TOKEN_API_URL = "http://kite.trialnerror.in/accesstoken/"


def kite_connect() -> KiteConnect:
    api_key = KITE_API_KEY
    api_secret = KITE_API_SECRET
    access_token_api_url = ACCESS_TOKEN_API_URL

    request = requests.get(access_token_api_url)
    access_token = request.json().get("access_token", "")
    status = "success"
    message = "Access token retrieved successfully."

    kite = KiteConnect(api_key=api_key)
    try:
        kite.set_access_token(access_token)
        profile = kite.profile()
    except Exception as e:
        print("Error setting access token:", e)
        status = "error"
        message = "Error setting access token. " + str(e)

        loginurl = kite.login_url()
        kite = None
        return None, {"status": status, "message": message, "login_url": loginurl}

    return kite, {"status": status, "message": message, "data": profile}


def eod_via_kite(
    instrument: dict, start_date: str, end_date: str, kite: KiteConnect = None
):

    instrument_token = instrument["instrument_token"]
    instrument_name = instrument["name"]

    data = kite.historical_data(
        instrument_token,
        start_date,
        end_date,
        "day",
        continuous=True,
        oi=True,
    )
    df = pd.DataFrame(data)

    if df.empty:
        return pd.DataFrame()

    df["symbol"] = instrument_name
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["datetime"] = df["date"]
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)
    df = df[["symbol", "datetime", "open", "high", "low", "close", "volume", "oi"]]
    df.drop_duplicates(subset=["datetime", "symbol"], keep="last", inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.sort_values(by="datetime", inplace=True)

    return df
