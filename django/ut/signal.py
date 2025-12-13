import pandas as pd
from tools import atr, ddt2, lv, weekly_rdata, asc
from ssc import SwingPoints2
import kbd1, kebf, kes7, kesb


def signals(ohlc: pd.DataFrame, symbol: str = "", models=["KBD1"]) -> pd.DataFrame:

    df_original = ohlc.copy()
    df = ohlc.copy()

    df = SwingPoints2(df)
    df["ddt2"] = ddt2(df)
    df["mvf"] = (
        (asc(df["close"], lookback=20) - df["low"])
        / asc(df["close"], lookback=20)
        * 100
    )
    df["atr"] = atr(df["high"], df["low"], df["close"], period=20)
    df["ldv"] = lv(df)
    df["weekly_rdata"] = weekly_rdata(df)

    df = df[-200:]  # Limit to last 200 rows for performance

    signals = []
    if df.empty:
        return df_original

    for d in range(1, len(df)):
        if "KBD1" in models:
            df_original = kbd1.signal(df.iloc[:d], symbol)

    return df_original
