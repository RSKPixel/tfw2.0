from rest_framework.decorators import api_view
from rest_framework.response import Response
from ut import kbd1, kebf, kes7, kesb
from ut.ssc import SwingPoints2
from ut.tools import asc, weekly_rdata, ddt2, lv, atr
from universaltrader import ut
from data.models import Instruments, EOD, IData75m, IData15m
import pandas as pd
from django.db import connection
from datetime import datetime


# Create your views here.
@api_view(["POST"])
def trading_models(request):

    trading_models = ["KBD1", "KEBF"]
    trading_models = {
        "KBD1": "Key Breakout - Dow Theory 1",
        "KEBF": "Key Exhaustion Butter Fly Pattern",
        "KES7": "Key Exhaustion 5 Waves Down 2 Waves Up Pattern",
        "KESB": "Key Exhaustion Swing Break",
    }

    return Response(
        {
            "status": "success",
            "message": "Available trading models fetched successfully.",
            "data": trading_models,
        }
    )


@api_view(["POST"])
def trading_signals2(request):

    data = request.data
    models = data.get("models")
    markets = data.get("markets", [])
    timeframe = data.get("timeframe")

    signals = []
    all_signals = pd.DataFrame()

    symbols = (
        Instruments.objects.filter(exchange__in=markets)
        .values_list("name", flat=True)
        .distinct()
        .order_by("name")
    )

    tables = {
        "1d": "tfw_eod",
        "75m": "tfw_idata_75m",
        "15m": "tfw_idata_15m",
    }
    table_name = tables.get(timeframe, "tfw_eod")
    signals = pd.DataFrame()
    for symbol in symbols:
        sql = f"""
            SELECT datetime AT TIME ZONE 'Asia/Kolkata' AS local_time, *
            FROM {table_name}
            WHERE symbol = %s and DATE(datetime AT TIME ZONE 'Asia/Kolkata') >= '2023-01-01'
            ORDER BY datetime ASC;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [symbol])

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        df = pd.DataFrame(rows, columns=columns)
        df.drop(columns=["datetime"], inplace=True)
        df.rename(columns={"local_time": "date"}, inplace=True)
        df["datetime"] = pd.to_datetime(df["date"])
        df = df[
            ["datetime", "date", "symbol", "open", "high", "low", "close", "volume"]
        ]

        if df.empty:
            print("No data for symbol:", symbol, "\r")
            continue

        df.set_index("date", inplace=True)

        try:
            df = ut.signals(ohlc=df, models=models)

            if len(df[df["signal"] == True]) == 0:
                continue

            all_signals = pd.concat(
                [all_signals, df[df["signal"] == True]], ignore_index=True
            )
        except Exception as e:
            print("Error processing symbol:", symbol, "Error:", e)
            continue

    all_signals.to_clipboard()
    all_signals = all_signals.fillna("")

    return Response(
        {
            "status": "success",
            "message": "Trading signals fetched successfully.",
            "data": {
                "signals": all_signals.to_dict(orient="records"),
            },
        }
    )


@api_view(["POST"])
def trading_signals(request):

    data = request.data
    models = data.get("models")
    markets = data.get("markets", [])
    timeframe = data.get("timeframe")

    signals = []
    all_signals = pd.DataFrame()

    symbols = (
        Instruments.objects.filter(exchange__in=markets)
        .values_list("name", flat=True)
        .distinct()
    )

    tables = {
        "1d": "tfw_eod",
        "75m": "tfw_idata_75m",
        "15m": "tfw_idata_15m",
    }
    table_name = tables.get(timeframe, "tfw_eod")

    for symbol in symbols:
        sql = f"""
            SELECT datetime AT TIME ZONE 'Asia/Kolkata' AS local_time, *
            FROM {table_name}
            WHERE symbol = %s and DATE(datetime AT TIME ZONE 'Asia/Kolkata') >= '2023-01-01'
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
        df["mvf"] = (
            (asc(df["close"], lookback=20) - df["low"])
            / asc(df["close"], lookback=20)
            * 100
        )
        df["ldv"] = lv(df["high"], df["low"], df["close"], lookback=4)
        df["atr"] = atr(df["high"], df["low"], df["close"], lookback=20)

        if timeframe == "1d":
            df = weekly_rdata(df)

        df = ddt2(df)
        df = df[-200:]  # Limit to last 200 rows for performance

        signals = []
        if df.empty:
            continue

        for d in range(1, len(df)):
            if "KBD1" in models:
                signal = kbd1.signal(df.iloc[:d], symbol)
                if signal is not None:
                    signals.append(signal)
            if "KEBF" in models:
                signal = kebf.signal(df.iloc[:d], symbol)
                if signal is not None:
                    signals.append(signal)
            if "KES7" in models:
                signal = kes7.signal(df.iloc[:d], symbol)
                if signal is not None:
                    signals.append(signal)
            if "KESB" in models:
                signal = kesb.signal(df.iloc[:d], symbol)
                if signal is not None:
                    signals.append(signal)

        signals = pd.DataFrame(signals)
        if not signals.empty:
            signals.sort_values(by="setup_candle", ascending=False, inplace=True)
            signals.reset_index(drop=True, inplace=True)
            all_signals = pd.concat([all_signals, signals], ignore_index=True)

    if timeframe != "1d":
        all_signals = all_signals[
            all_signals["setup_candle"].dt.date == datetime.now().date()
        ]
    all_signals.to_clipboard()
    return Response(
        {
            "status": "success",
            "message": "Trading signals fetched successfully.",
            "data": {
                "signals": all_signals.sort_values(
                    by="setup_candle", ascending=False
                ).to_dict(orient="records")
            },
        }
    )
