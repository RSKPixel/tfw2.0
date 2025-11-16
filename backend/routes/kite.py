from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
import pandas as pd
from datetime import datetime, timedelta
from config import kite_connect
import numpy as np

router = APIRouter(prefix="/kite")


@router.get("/instruments")
async def get_instruments():
    kite = kite_connect()
    if not kite:
        return JSONResponse(
            content={"message": "Kite connection could not be established."},
            status_code=500,
        )

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
    instruments_list.to_csv("data/instruments.csv", index=False)
    return JSONResponse(
        content=instruments_list.to_dict(orient="records"), status_code=200
    )


@router.get("/eod")
async def get_eod_data(
    symbol: str = "",
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    no_of_candles: int = 2000,
):
    kite = kite_connect()

    if not kite:
        return JSONResponse(
            content={"message": "Kite connection could not be established."},
            status_code=500,
        )

    if not symbol:
        return JSONResponse(
            content={"message": "Symbol parameter is required."}, status_code=400
        )

    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=no_of_candles)
    ).strftime("%Y-%m-%d")

    instruments = pd.DataFrame(kite.instruments())
    instruments["expiry"] = pd.to_datetime(instruments["expiry"])
    instrument = instruments[instruments["tradingsymbol"] == symbol].iloc[0]
    instrument_token = instrument["instrument_token"]
    data = kite.historical_data(
        instrument_token, start_date, end_date, "day", continuous=True, oi=True
    )
    df = pd.DataFrame(data)

    if df.empty:
        return JSONResponse(
            content={"message": "No data found for the given parameters."},
            status_code=404,
        )
    df["symbol"] = instrument["name"]
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["datetime"] = df["date"]
    df = df[["symbol", "datetime", "open", "high", "low", "close", "volume", "oi"]]

    return JSONResponse(content=df.to_dict(orient="records"), status_code=200)
