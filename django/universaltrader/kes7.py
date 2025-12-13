import numpy as np
import pandas as pd


def signal(df: pd.DataFrame, symbol: str = ""):

    signal = {
        "model": "KBS7",
        "symbol": symbol,
        "signal": None,
        "setup_candle": None,
        "entry_date": None,
        "entry_price": None,
        "entry_day_sl": None,
    }
    df = df.copy()
    if df.iloc[-1]["swing"] not in ["high", "low"]:
        return
    df = df[df["swing_point"].notna()].tail(8)

    if len(df) < 8:
        return

    # Reverse so index 0 = MOST RECENT swing
    swing_points = df["swing_point"][::-1].to_list()
    swings = df["swing"][::-1].to_list()
    swing_dates = df.index[::-1].to_list()

    buy_p = swings == ["low", "high", "low", "high", "low", "high", "low", "high"]
    sell_p = swings == ["high", "low", "high", "low", "high", "low", "high", "low"]

    bf_buy = (
        buy_p
        and (
            swing_points[2] < swing_points[4]
            and swing_points[4] < swing_points[6]
            and swing_points[3] < swing_points[5]
            and swing_points[5] < swing_points[7]
        )
        and (swing_points[0] > swing_points[2] and swing_points[1] < swing_points[3])
    )

    bf_sell = (
        sell_p
        and (
            swing_points[2] > swing_points[4]
            and swing_points[4] > swing_points[6]
            and swing_points[3] > swing_points[5]
            and swing_points[5] > swing_points[7]
        )
        and (swing_points[0] < swing_points[2] and swing_points[1] > swing_points[3])
    )

    if bf_buy or bf_sell:
        signal = {
            "model": "KBS7",
            "symbol": symbol,
            "signal": "buy" if bf_buy else "sell",
            "setup_candle": swing_dates[0],
            "entry_date": swing_dates[0],
            "entry_price": swing_points[0],
            "entry_day_sl": 0,
        }

        return signal
    return None
