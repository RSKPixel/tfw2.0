from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from data.kite import eod_via_kite, kite_connect

DATA_DIR = settings.DATA_DIR


@api_view(["GET"])
def get_instruments(request):
    output_file = f"{DATA_DIR}/instruments.csv"
    kite = kite_connect()
    if not kite:
        return Response(
            {
                "status": "error",
                "message": "Kite connection could not be established.",
                "data": [],
            },
        )

    # Check if instruments are already saved
    try:
        instruments = pd.read_csv(output_file)
        # check_file_date
        file_date = datetime.fromtimestamp(os.path.getmtime(output_file)).date()
        if file_date == datetime.now().date():
            return Response(
                {
                    "status": "success",
                    "message": "Instruments retrieved successfully.",
                    "data": instruments.to_dict(orient="records"),
                },
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

    return Response(
        {
            "status": "success",
            "message": "Instruments fetched successfully.",
            "data": instruments_list.to_dict(orient="records"),
        }
    )


@api_view(["GET"])
async def get_eod_data(
    symbol: str = "",
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    no_of_candles: int = 2000,
):
    instrument_file = f"{DATA_DIR}/instruments.csv"
    kite = kite_connect()

    if not kite:
        return Response(
            {
                "status": "error",
                "message": "Kite connection could not be established.",
                "data": [],
            },
        )

    if not symbol:
        return Response(
            {
                "status": "error",
                "message": "Symbol parameter is required.",
                "data": [],
            },
        )

    symbol = symbol.upper()
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=no_of_candles)
    ).strftime("%Y-%m-%d")

    instruments = pd.read_csv(instrument_file)
    instruments["expiry"] = pd.to_datetime(instruments["expiry"])
    instrument = instruments[instruments["name"] == symbol]
    if instrument.empty:
        return Response(
            {
                "status": "error",
                "message": f"Instrument with symbol {symbol} not found.",
                "data": [],
            },
        )

    instrument = instrument.iloc[0]

    df = eod_via_kite(
        instrument=instrument, start_date=start_date, end_date=end_date, kite=kite
    )

    return Response(
        {
            "status": "success",
            "message": "EOD data retrieved successfully.",
            "data": df.to_dict(orient="records"),
        },
    )
