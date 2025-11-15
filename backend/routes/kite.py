from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
from config import kite_connect

router = APIRouter(prefix="/kite")
kite = kite_connect()


@router.get("/eod")
async def get_eod_data(
    symbol: str = "",
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    no_of_candles: int = 2000,
):

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
