from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException
from rich.console import Console
from rich.live import Live
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from psycopg2.extras import execute_values
import requests
from datetime import datetime, timedelta
import os
from time import sleep

db_config = {
    "host": "trialnerror.in",
    "port": 5432,
    "database": "tfw",
    "user": "sysadmin",
    "password": "Apple@1239",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

KITE_API_KEY = "tw96psyyds0yj8vj"
KITE_API_SECRET = "3iewov9onkbytzramkt263r9lvcdzks9"
ACCESS_TOKEN_API_URL = "http://kite.trialnerror.in/accesstoken/"

console = Console()


def backfiller():
    os.system("cls" if os.name == "nt" else "clear")
    api = KiteConnect(api_key=KITE_API_KEY)
    try:
        accesstoken_request = requests.get(ACCESS_TOKEN_API_URL)
        access_token = accesstoken_request.json().get("access_token", "")
        api.set_access_token(access_token)

        profile = api.profile()
        conn = psycopg2.connect(**db_config)
    except KiteException as e:
        console.print(f"[red]Kite Exception: {api.login_url()}[/red]")
        console.print(f"[red]Kite Exception: {e}[/red]")
        return
    except OperationalError as e:
        console.print(f"[red]Operational Error: {e}[/red]")
        return
    except DatabaseError as e:
        console.print(f"[red]Database Exception: {e}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Exception: {e}[/red]")
        return

    instruments_df = instruments(api, conn)
    instruments_df = instruments_df.reset_index(drop=True)
    instruments_df.to_clipboard()

    if len(instruments_df) == 0:
        console.print("[red]No instruments found to backfill.[/red]")
        return

    first_run = True
    period = 1
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        # center screen title
        console.print(
            f"[bold blue]Kite Connect Backfiller[/bold blue] - [bold green]{str(profile['user_shortname']).upper()} (ID: {profile['user_id']})[/bold green] \n"
        )
        console.print(
            f"[green]Total Instruments to backfill: {len(instruments_df)}[/green]"
        )

        if first_run:
            period = 0
            first_run = False
        else:
            period = 1

        historicals(period=period, interval="15minute", api=api, conn=conn)

        wait_until_next(waiting_minutes=1)


def historicals(
    period, interval, api: KiteConnect, conn: psycopg2.extensions.connection
):
    if period == 0:
        period_msg = "Previous Expiry Date + 1 to Current Date"
    elif period == 1:
        period_msg = f"{period} day"
    console.print(
        f"[bold blue]Fetching historical data for, period: [bold yellow]{period_msg}[/bold yellow], interval: [bold yellow]{interval}[/bold yellow][/bold blue]\n"
    )
    # Placeholder for historical data fetching logic
    # This function would contain the logic to fetch and store historical data
    pass


def wait_until_next(waiting_minutes=1, seconds=1):
    now = datetime.now()

    next_minute = ((now.minute // waiting_minutes) + 1) * waiting_minutes

    if next_minute >= 60:
        next_run = now.replace(
            hour=(now.hour + 1) % 24,
            minute=0,
            second=seconds,
            microsecond=0,
        )
    else:
        next_run = now.replace(
            minute=next_minute,
            second=seconds,
            microsecond=0,
        )

    wait_seconds = int((next_run - now).total_seconds())

    if wait_seconds <= 0:
        return

    try:
        with Live(console=console, refresh_per_second=4) as live:
            for remaining in range(wait_seconds, 0, -1):
                mins, secs = divmod(remaining, 60)
                live.update(f"⏳ Sleeping... {mins:02d}m {secs:02d}s remaining")
                sleep(1)

    except KeyboardInterrupt:
        console.print("\n⛔️ Interrupted by user.")
        raise SystemExit(0)

    console.print("✅ Woke up for next run!\n")


def instruments(api: KiteConnect, conn: psycopg2.extensions.connection) -> pd.DataFrame:
    output_file = f"{DATA_DIR}/instruments-backfill.csv"

    # Check if instruments are already saved
    original_data = pd.DataFrame()
    try:
        instruments = pd.read_csv(output_file)
        original_data = instruments.copy()
        # check_file_date
        file_date = datetime.fromtimestamp(os.path.getmtime(output_file)).date()
        if file_date == datetime.now().date():
            sql = """
                WITH ordered AS (
                    SELECT
                        instrument_token,
                        exchange_token,
                        tradingsymbol,
                        name,
                        expiry,
                        lot_size,
                        tick_size,
                        instrument_type,
                        segment,
                        exchange,
                        LAG(tradingsymbol) OVER (
                            PARTITION BY name
                            ORDER BY expiry
                        ) AS prev_symbol,
                        LAG(expiry) OVER (
                            PARTITION BY name
                            ORDER BY expiry
                        ) AS prev_expiry
                    FROM tfw_instruments
                )
                SELECT
                    name,
                    instrument_token      AS instrument_token,
                    exchange_token        AS exchange_token,
                    tradingsymbol         AS tradingsymbol,
                    expiry                AS expiry,
                    lot_size              AS lot_size,
                    tick_size             AS tick_size,
                    instrument_type       AS instrument_type,
                    segment               AS segment,
                    exchange              AS exchange,
                    prev_symbol           AS previous_tradingsymbol,
                    prev_expiry           AS previous_expiry
                FROM ordered o
                WHERE expiry = (
                    SELECT MIN(expiry)
                    FROM tfw_instruments t
                    WHERE t.name = o.name
                    AND t.expiry >= CURRENT_DATE
                )
                ORDER BY name;
            """
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()

            columns = [
                "name",
                "instrument_token",
                "exchange_token",
                "tradingsymbol",
                "expiry",
                "lot_size",
                "tick_size",
                "instrument_type",
                "segment",
                "exchange",
                "previous_tradingsymbol",
                "previous_expiry",
            ]
            instruments = pd.DataFrame(rows, columns=columns)
            instruments["previous_expiry"] = pd.to_datetime(
                np.where(
                    instruments["previous_expiry"].isnull(),
                    pd.to_datetime(instruments["expiry"]) - timedelta(days=30),
                    instruments["previous_expiry"],
                )
            )
            return instruments
    except FileNotFoundError:
        console.print("Instruments file not found. Fetching from Kite...")
        pass

    instruments = pd.DataFrame(api.instruments())
    instruments["expiry"] = pd.to_datetime(instruments["expiry"]).dt.strftime(
        "%Y-%m-%d"
    )
    instruments = instruments.sort_values(by=["segment", "tradingsymbol"])
    instruments = instruments.replace([np.inf, -np.inf], None)
    instruments = instruments.where(pd.notnull(instruments), None)

    mcx = instruments[
        (instruments["exchange"] == "MCX")
        & (instruments["instrument_type"] == "FUT")
        & (instruments["segment"] == "MCX-FUT")
    ].sort_values(["expiry"])

    nfo = instruments[
        (instruments["exchange"] == "NFO")
        & (instruments["instrument_type"] == "FUT")
        & (instruments["segment"] == "NFO-FUT")
    ].sort_values(["expiry"])

    instruments_list = pd.concat([mcx, nfo]).reset_index(drop=True)
    instruments_list = (
        pd.concat([original_data, instruments_list])
        .drop_duplicates()
        .reset_index(drop=True)
    )
    instruments_list.to_csv(output_file, index=False)

    instruments_list = instruments_list[
        [
            "instrument_token",
            "exchange_token",
            "tradingsymbol",
            "name",
            "last_price",
            "expiry",
            "strike",
            "tick_size",
            "lot_size",
            "instrument_type",
            "segment",
            "exchange",
        ]
    ]
    instruments_records = instruments_list.to_numpy().tolist()
    sql = """
        INSERT INTO tfw_instruments (
            instrument_token,
            exchange_token,
            tradingsymbol,
            name,
            last_price,
            expiry,
            strike,
            tick_size,
            lot_size,
            instrument_type,
            segment,
            exchange
            )
            VALUES %s
            ON CONFLICT (tradingsymbol, exchange) DO NOTHING;"""

    with conn:
        with conn.cursor() as cursor:
            execute_values(cursor, sql, instruments_records)

    return instruments_list


if __name__ == "__main__":
    backfiller()
