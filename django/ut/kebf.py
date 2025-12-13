import numpy as np
import pandas as pd
from datetime import datetime


def signal(df: pd.DataFrame, symbol: str = ""):

    signal = {
        "model": "KBD1",
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
    df = df[df["swing_point"].notna()].tail(6)

    if len(df) < 6:
        return

    # Reverse so index 0 = MOST RECENT swing
    swing_points = df["swing_point"][::-1].to_list()
    swings = df["swing"][::-1].to_list()
    swing_dates = df.index[::-1].to_list()

    buy_pattern = swings == ["low", "high", "low", "high", "low", "high"]
    sell_pattern = swings == ["high", "low", "high", "low", "high", "low"]

    # 0 = latest, 5 = oldest

    bf_buy = (
        buy_pattern
        and swing_points[0] < swing_points[2]
        and swing_points[0] < swing_points[4]
        and swing_points[1] < swing_points[3]
        and swing_points[2] > swing_points[4]
        and swing_points[3] < swing_points[5]
    )

    s4_3 = swing_points[3] - swing_points[4]
    s0_3 = swing_points[3] - swing_points[0]

    try:
        bf_buy_confirm = bf_buy and (s4_3 / s0_3 > 1.25) and (s4_3 < 1.5)
    except ZeroDivisionError:
        bf_buy_confirm = False

    bf_sell = (
        sell_pattern
        and swing_points[0] > swing_points[2]
        and swing_points[0] > swing_points[4]
        and swing_points[1] > swing_points[3]
        and swing_points[2] < swing_points[4]
        and swing_points[3] > swing_points[5]
    )

    s4_3 = swing_points[4] - swing_points[3]
    s0_3 = swing_points[0] - swing_points[3]

    try:
        bf_sell_confirm = bf_sell and (s4_3 / s0_3 > 1.25) and (s4_3 < 1.5)
    except ZeroDivisionError:
        bf_sell_confirm = False

    if bf_buy_confirm or bf_sell_confirm:
        if symbol == "SAIL":
            print(
                swing_dates,
                swing_points,
                swings,
            )

        signal = {
            "model": "KBD1",
            "symbol": symbol,
            "signal": "buy" if bf_buy else "sell",
            "setup_candle": swing_dates[0],
            "entry_date": swing_dates[0],
            "entry_price": swing_points[0],
            "entry_day_sl": 0,
        }

        return signal
    return None
