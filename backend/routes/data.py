from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
import pandas as pd
from datetime import datetime, timedelta
from config import kite_connect, postgres_engine, DATA_DIR
from kiteconnect import KiteConnect
import numpy as np
import os
import json
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, MetaData
import time
from psycopg2.extras import execute_values

router = APIRouter(prefix="/data")

metadata = MetaData()


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


@router.get("/instruments")
async def get_instruments():
    output_file = f"{DATA_DIR}/instruments.csv"
    kite = kite_connect()
    if not kite:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Kite connection could not be established.",
                "data": [],
            },
            status_code=200,
        )

    # Check if instruments are already saved
    try:
        instruments = pd.read_csv(output_file)
        # check_file_date
        file_date = datetime.fromtimestamp(os.path.getmtime(output_file)).date()
        if file_date == datetime.now().date():
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Instruments retrieved successfully.",
                    "data": instruments.to_dict(orient="records"),
                },
                status_code=200,
            )
    except FileNotFoundError:
        pass

    instruments = pd.DataFrame(kite.instruments())
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

    mcx = mcx.loc[mcx.groupby("name")["expiry"].idxmin()].sort_values("name")

    nfo = instruments[
        (instruments["exchange"] == "NFO")
        & (instruments["instrument_type"] == "FUT")
        & (instruments["segment"] == "NFO-FUT")
    ].sort_values(["expiry"])
    nfo = nfo.loc[nfo.groupby("name")["expiry"].idxmin()].sort_values("name")

    currency_names = [
        "USDINR",
        "EURINR",
        "GBPINR",
        "JPYINR",
    ]
    monthly_expiry = [
        "JANFUT",
        "FEBFUT",
        "MARFUT",
        "APRFUT",
        "MAYFUT",
        "JUNFUT",
        "JULFUT",
        "AUGFUT",
        "SEPFUT",
        "OCTFUT",
        "NOVFUT",
        "DECFUT",
    ]

    cds = instruments[
        (instruments["exchange"] == "CDS")
        & (instruments["instrument_type"] == "FUT")
        & (instruments["segment"] == "CDS-FUT")
        & (instruments["name"].isin(currency_names))
        & (instruments["tradingsymbol"].str[-6:].isin(monthly_expiry))
    ].sort_values(["expiry"])

    cds = cds.loc[cds.groupby("name")["expiry"].idxmin()].sort_values("name")

    instruments_list = pd.concat([mcx, nfo, cds]).reset_index(drop=True)
    instruments_list.to_clipboard(index=False)
    instruments_list.to_csv(output_file, index=False)

    return JSONResponse(
        content={
            "status": "success",
            "message": "Instruments fetched successfully.",
            "data": instruments_list.to_dict(orient="records"),
        },
        status_code=200,
    )


@router.get("/eod")
async def get_eod_data(
    symbol: str = "",
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    no_of_candles: int = 2000,
):
    instrument_file = f"{DATA_DIR}/instruments.csv"
    kite = kite_connect()

    if not kite:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Kite connection could not be established.",
                "data": [],
            },
            status_code=500,
        )

    if not symbol:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Symbol parameter is required.",
                "data": [],
            },
            status_code=400,
        )

    symbol = symbol.upper()
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=no_of_candles)
    ).strftime("%Y-%m-%d")

    instruments = pd.read_csv(instrument_file)
    instruments["expiry"] = pd.to_datetime(instruments["expiry"])
    instrument = instruments[instruments["name"] == symbol]
    if instrument.empty:
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Instrument with symbol {symbol} not found.",
                "data": [],
            },
            status_code=200,
        )

    instrument = instrument.iloc[0]

    df = eod_via_kite(
        instrument=instrument, start_date=start_date, end_date=end_date, kite=kite
    )

    return JSONResponse(
        content={
            "status": "success",
            "message": "EOD data retrieved successfully.",
            "data": df.to_dict(orient="records"),
        },
        status_code=200,
    )


@router.get("/fetch-save-eod")
async def fetch_save_eod(
    symbol: str = "",
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    no_of_candles: int = 7,
):

    kite = kite_connect()
    engine = postgres_engine()
    no_of_candles = 2000 if int(no_of_candles) > 2000 else int(no_of_candles)

    eod_table = Table("eod", metadata, autoload_with=engine)

    try:
        instruments = pd.read_csv(f"{DATA_DIR}/instruments.csv")
    except FileNotFoundError:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Instruments file not found. Please fetch instruments first.",
                "data": [],
            },
            status_code=500,
        )

    if not kite or not engine:
        return JSONResponse(
            content={
                "status": "error",
                "message": "Kite connection or database engine could not be established.",
                "data": [],
            },
            status_code=500,
        )

    if symbol:
        instruments = instruments[instruments["name"] == symbol.upper()]

    data = []
    for _, instrument in instruments.iterrows():
        to_date = end_date
        from_date = (
            datetime.strptime(to_date, "%Y-%m-%d")
            - timedelta(days=2000 if no_of_candles == 0 else no_of_candles)
        ).strftime("%Y-%m-%d")

        while True:
            df = eod_via_kite(
                instrument=instrument,
                start_date=from_date,
                end_date=to_date,
                kite=kite,
            )

            data.append(
                {
                    "symbol": instrument["name"],
                    "start_date": from_date,
                    "end_date": to_date,
                    "records_fetched": len(df),
                }
            )

            if df.empty:
                break

            records = [
                (
                    row["datetime"],
                    row["symbol"],
                    Decimal(str(row["open"])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    Decimal(str(row["high"])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    Decimal(str(row["low"])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    Decimal(str(row["close"])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    int(row["volume"]),
                    int(row["oi"]),
                )
                for _, row in df.iterrows()
            ]

            query = (
                f
            ) = """
                INSERT INTO eod (datetime, symbol, open, high, low, close, volume, oi)
                VALUES %s
                ON CONFLICT (datetime, symbol) DO UPDATE SET
                    open   = EXCLUDED.open,
                    high   = EXCLUDED.high,
                    low    = EXCLUDED.low,
                    close  = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    oi     = EXCLUDED.oi
            """

            raw_conn = engine.raw_connection()
            try:
                cursor = raw_conn.cursor()
                execute_values(cursor, query, records, page_size=10000)
                raw_conn.commit()
            finally:
                cursor.close()
                raw_conn.close()

            if no_of_candles == 0:
                to_date = from_date
                from_date = (
                    datetime.strptime(from_date, "%Y-%m-%d") - timedelta(days=2000)
                ).strftime("%Y-%m-%d")
                time.sleep(0.05)  # to avoid hitting rate limits
                continue

            break

    return JSONResponse(
        content={
            "status": "success",
            "message": "EOD data fetched for NSE / MCX / CDS and saved to database successfully.",
            "data": data,
        },
        status_code=200,
    )
