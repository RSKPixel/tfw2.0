from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException
from rich.console import Console
import pandas as pd
import numpy as np
import psycopg2
import requests
import os

import time

db_config = {
    "host": "trialnerror.in",
    "port": 5432,
    "database": "tfw",
    "user": "ysadmin",
    "password": "Apple@1239",
}


KITE_API_KEY = "tw96psyyds0yj8vj"
KITE_API_SECRET = "3iewov9onkbytzramkt263r9lvcdzks9"
ACCESS_TOKEN_API_URL = "http://kite.trialnerror.in/accesstoken/"

console = Console()


def backfiller():
    os.system("cls" if os.name == "nt" else "clear")
    console.print("[bold blue]Kite Connect Backfiller[/bold blue]\n")
    api = KiteConnect(api_key=KITE_API_KEY)
    try:
        accesstoken_request = requests.get(ACCESS_TOKEN_API_URL)
        access_token = accesstoken_request.json().get("access_token", "")
        api.set_access_token(access_token)

        profile = api.profile()
        console.print(
            f"{str(profile['user_shortname']).upper()} (ID: {profile['user_id']})"
        )
        conn = psycopg2.connect(**db_config)
    except KiteException as e:
        console.print(f"[red]Kite Exception: {api.login_url()}[/red]")
        console.print(f"[red]Kite Exception: {e}[/red]")
        return
    except Exception as e:
        # catch psycopg2 connection errors

        console.print(f"[red]Exception: {e}[/red]")
        return


def kite_connect() -> tuple[KiteConnect, dict]:
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


if __name__ == "__main__":
    backfiller()
