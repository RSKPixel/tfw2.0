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
import time
from time import sleep
from rich.progress import Progress, SpinnerColumn, TextColumn

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

        historicals(
            instruments=instruments_df,
            period=period,
            interval="15minute",
            api=api,
            conn=conn,
        )

        wait_until_next(waiting_minutes=15, seconds=1)


def historicals(
    instruments: pd.DataFrame,
    period: int,
    interval: str,
    api: KiteConnect,
    conn: psycopg2.extensions.connection,
):
    if period == 0:
        period_msg = "Previous Expiry Date + 1 to Current Date"
    elif period == 1:
        period_msg = f"{period} day"
    console.print(
        f"[bold blue]Fetching historical data for, period: [bold yellow]{period_msg}[/bold yellow], interval: [bold yellow]{interval}[/bold yellow][/bold blue]\n"
    )

    SYMBOL_WIDTH = 50
    total = len(instruments)
    request_count = 0
    req_rate = 0

    complete_data = pd.DataFrame()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:

        task = progress.add_task("", total=total)
        start_time = time.time()
        for _, instrument in instruments.iterrows():
            symbol = instrument["tradingsymbol"]

            try:
                previous_expiry = instrument["previous_expiry"]
                expiry = instrument["expiry"]
                instrument_token = instrument["instrument_token"]

                if period == 0:
                    start_date = previous_expiry + timedelta(days=1)
                else:
                    start_date = datetime.now() - timedelta(days=period)

                start_date = start_date.strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
                request_count += 1
                idata = api.historical_data(
                    instrument_token,
                    start_date,
                    end_date,
                    interval,
                    continuous=False,
                    oi=False,
                )
                idata = pd.DataFrame(idata)
                if idata.empty:
                    continue

                idata["symbol"] = symbol[:-8]
                idata = idata[
                    ["symbol", "date", "open", "high", "low", "close", "volume"]
                ]
                idata.rename(columns={"date": "datetime"}, inplace=True)
                idata["datetime"] = pd.to_datetime(idata["datetime"])
                idata = idata.replace([np.inf, -np.inf], None)
                idata = idata.where(pd.notnull(idata), None)

                save_data(
                    data=idata,
                    interval=f"{interval}",
                    conn=conn,
                )
            except Exception as e:
                console.print(f"[red]Error {symbol}: {e}[/red]")
            finally:
                completed = int(progress.tasks[task].completed) + 1

                progress.update(
                    task,
                    advance=1,
                    description=(
                        f"⏳ Fetching "
                        f"[bold green]{symbol:<{SYMBOL_WIDTH}}[/bold green] {start_date} - {end_date} @ {req_rate:.2f} req/s "
                        f"({completed:>3}/{total})"
                    ),
                )
            elapsed = time.time() - start_time
            req_rate = request_count / elapsed if elapsed > 0 else 0
            if req_rate > 10:
                sleep(0.1)
        time_elapsed = time.time() - start_time
        progress.update(
            task, description=f"✅ Fetching completed in {time_elapsed:.2f} seconds!"
        )


def save_data(
    data: pd.DataFrame,
    interval: str,
    conn: psycopg2.extensions.connection,
):

    if interval == "15minute":
        table_name = "tfw_idata_15m"
    elif interval == "75minute":
        table_name = "tfw_idata_75m"
    else:
        console.print(f"[red]Invalid interval: {interval}[/red]")
        return

    rows = data.to_numpy().tolist()
    sql = f"""
        INSERT INTO {table_name} (
        SYMBOL,
        DATETIME,
        OPEN,
        HIGH,
        LOW,
        CLOSE,
        VOLUME
        )
        VALUES %s
        ON CONFLICT (symbol, datetime) DO UPDATE SET
            open   = EXCLUDED.open,
            high   = EXCLUDED.high,
            low    = EXCLUDED.low,
            close  = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """

    with conn:
        with conn.cursor() as cursor:
            execute_values(cursor, sql, rows)


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

    def fetch_instruments() -> pd.DataFrame:
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
                datetime(day=30, month=11, year=2025),
                instruments["previous_expiry"],
            )
        )
        return instruments

    output_file = f"{DATA_DIR}/instruments-backfill.csv"

    # Check if instruments are already saved
    original_data = pd.DataFrame()
    try:
        instruments = pd.read_csv(output_file)
        original_data = instruments.copy()
        # check_file_date
        file_date = datetime.fromtimestamp(os.path.getmtime(output_file)).date()
        if file_date == datetime.now().date():
            instruments = fetch_instruments()
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

    instruments = fetch_instruments()
    return instruments


if __name__ == "__main__":
    backfiller()
