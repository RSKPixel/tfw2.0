from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from data.kite_framework import eod_via_kite, kite_connect
from .models import EOD
from django.db import connection
from django.db import connection
from psycopg2.extras import execute_values
import time


DATA_DIR = settings.DATA_DIR


@api_view(["GET"])
def get_instruments(request):
    output_file = f"{DATA_DIR}/instruments.csv"
    kite, kite_response = kite_connect()
    if kite_response["status"] == "error":
        return Response(kite_response)

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
def get_eod_data(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    from_date = request.GET.get(
        "from_date", (datetime.now() - timedelta(days=2000)).strftime("%Y-%m-%d")
    )
    to_date = request.GET.get("to_date", datetime.now().strftime("%Y-%m-%d"))

    instrument_file = f"{DATA_DIR}/instruments.csv"
    kite, kite_response = kite_connect()

    if kite_response["status"] == "error":
        return Response(kite_response)

    if not symbol:
        return Response(
            {
                "status": "error",
                "message": "Symbol parameter is required.",
                "data": [],
            },
        )

    symbol = symbol.upper()
    ohlvc_data = (
        EOD.objects.filter(symbol=symbol, datetime__range=[from_date, to_date])
        .order_by("datetime")
        .values("symbol", "datetime", "open", "high", "low", "close", "volume", "oi")
    )
    ohlvc_data = pd.DataFrame(ohlvc_data)

    return Response(
        {
            "status": "success",
            "message": "EOD data fetched successfully.",
            "data": ohlvc_data.to_dict(orient="records"),
        },
    )


@api_view(["POST"])
def fetch_n_save(request):
    symbol = request.data.get("symbol", "").upper()
    end_date = request.data.get("end_date", datetime.now().strftime("%Y-%m-%d"))
    no_of_candles = int(request.data.get("no_of_candles", 2000))
    year = int(request.data.get("year", "0"))

    instrument_file = f"{DATA_DIR}/instruments.csv"
    kite, kite_response = kite_connect()

    if kite_response["status"] == "error":
        return Response(kite_response)

    symbol = symbol.upper()

    if year:
        start_date = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = datetime.strptime(f"{year}-12-31", "%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
    else:
        start_date = (
            datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=no_of_candles)
        ).strftime("%Y-%m-%d")

    instruments = pd.read_csv(instrument_file)
    if symbol:
        instruments = instruments[instruments["name"] == symbol]

    response_data = []
    error_data = []
    start_time = time.time()
    api_time = 0
    sql_time = 0
    for _, instrument in instruments.iterrows():
        ohlcv_data = pd.DataFrame()
        api_time_start = time.time()
        try:
            ohlcv_data = eod_via_kite(
                instrument=instrument,
                start_date=start_date,
                end_date=end_date,
                kite=kite,
            )

        except Exception as e:
            print(f"Error fetching data for {instrument['tradingsymbol']}: {e}")
            error_data.append(
                f"Error fetching data for {instrument['tradingsymbol']}: {e}"
            )
            continue
        api_time += time.time() - api_time_start

        if ohlcv_data.empty:
            continue

        sql_time_start = time.time()
        ohlcv_data["symbol"] = instrument["tradingsymbol"]
        ohlcv_data = ohlcv_data[
            ["symbol", "datetime", "open", "high", "low", "close", "volume", "oi"]
        ]
        ohlcv_data = ohlcv_data.copy()
        rows = ohlcv_data.to_numpy().tolist()

        sql = """
            INSERT INTO tfw_eod
            (symbol, datetime, open, high, low, close, volume, oi)
            VALUES %s
            ON CONFLICT (symbol, datetime)
            DO UPDATE SET
                open   = EXCLUDED.open,
                high   = EXCLUDED.high,
                low    = EXCLUDED.low,
                close  = EXCLUDED.close,
                volume = EXCLUDED.volume,
                oi     = EXCLUDED.oi;
        """

        with connection.cursor() as cursor:
            execute_values(cursor, sql, rows, page_size=1000)

        sql_time += time.time() - sql_time_start

        response_data.append(
            {
                "symbol": instrument["tradingsymbol"],
                "from_date": ohlcv_data["datetime"].min(),
                "to_date": ohlcv_data["datetime"].max(),
                "no_of_records": len(ohlcv_data),
            }
        )

    return Response(
        {
            "status": "success",
            "message": f"EOD data from {start_date} to {end_date} fetched and saved successfully. Total Time Taken: {time.time() - start_time:.2f} seconds with Error Count: {len(error_data)}.",
            "data": [response_data, error_data],
        },
    )


# Save to database using orm is not possible because of id field not existing in the data model
# records = []
# for _, row in ohlcv_data.iterrows():
#     record = EOD(
#         symbol=row["symbol"],
#         datetime=row["datetime"],
#         open=row["open"],
#         high=row["high"],
#         low=row["low"],
#         close=row["close"],
#         volume=row["volume"],
#         oi=row["oi"],
#     )
#     records.append(record)

# EOD.objects.bulk_create(
#     records,
#     update_conflicts=True,
#     update_fields=["open", "high", "low", "close", "volume", "oi"],
#     unique_fields=["symbol", "datetime"],
# )

# rows = [
#     (
#         row["symbol"],
#         row["datetime"],
#         row["open"],
#         row["high"],
#         row["low"],
#         row["close"],
#         row["volume"],
#         row["oi"],
#     )
#     for _, row in ohlcv_data.iterrows()
# ]
