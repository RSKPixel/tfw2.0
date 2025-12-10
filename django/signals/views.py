from rest_framework.decorators import api_view
from rest_framework.response import Response
from ut import kbd1, kebf
from ut.ssc import SwingPoints2
from ut.tools import asc, weekly_rdata, ddt2, lv
from data.models import Instruments, EOD, IData75m, IData15m
import pandas as pd
from django.db import connection


# Create your views here.
@api_view(["POST"])
def trading_models(request):

    trading_models = ["KBD1", "KEBF"]
    trading_models = {
        "KBD1": "Key Breakout - Dow Theory 1",
        "KEBF": "Key Exhaustion Butter Fly Pattern",
    }

    return Response(
        {
            "status": "success",
            "message": "Available trading models fetched successfully.",
            "data": trading_models,
        }
    )


@api_view(["POST"])
def trading_signals(request):

    data = request.data
    models = data.get("models")
    markets = data.get("markets", [])
    timeframe = data.get("timeframe")

    signals = []

    symbols = (
        Instruments.objects.filter(exchange__in=markets)
        .values_list("name", flat=True)
        .distinct()
    )

    if timeframe == "1d":
        table_model = EOD
        table_name = "tfw_eod"
    elif timeframe == "75m":
        table_model = IData75m
        table_name = "tfw_idata_75m"
    elif timeframe == "15m":
        table_model = IData15m
        table_name = "tfw_idata_15m"

    for symbol in symbols:
        sql = f"""
            SELECT datetime AT TIME ZONE 'Asia/Kolkata' AS local_time, *
            FROM {table_name}
            WHERE symbol = %s
            ORDER BY datetime ASC;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [symbol])

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        df = pd.DataFrame(rows, columns=columns)
        df.drop(columns=["datetime"], inplace=True)
        df.rename(columns={"local_time": "date"}, inplace=True)

        if df.empty:
            print("No data for symbol:", symbol, "\r")
            continue

        df.set_index("date", inplace=True)
        df = SwingPoints2(df)
        df["asc"] = asc(df["close"], lookback=20)
        df["mvf"] = (df["asc"] - df["low"]) / df["asc"] * 100
        df["ldv"] = lv(df["high"], df["low"], df["close"], lookback=4)
        df = weekly_rdata(df)
        df = ddt2(df)
        df.drop(columns=["asc"], inplace=True)

        signals = []
        if "KBD1" in models:
            for d in range(1, len(df)):
                signal = kbd1.signal(df.iloc[:d], symbol)
                if signal is not None:
                    signals.append(signal)

        if "KEBF" in models:
            signal = kebf.signal(df, symbol)
            if signal is not None:
                signals.append(signal)

        print(type(signals))
        signals = pd.DataFrame(signals)
        if not signals.empty:
            signals.sort_values(by="setup_candle", ascending=False, inplace=True)
            signals.reset_index(drop=True, inplace=True)
            signals = signals[
                signals["setup_candle"].dt.date == signals["setup_candle"].dt.date.max()
            ]
    return Response(
        {
            "status": "success",
            "message": "Trading signals fetched successfully.",
            "data": {"signals": signals},
        }
    )
