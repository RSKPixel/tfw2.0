import pandas as pd
from . import tools, ssc
from . import kbd1


def signals(ohlc: pd.DataFrame, models=["KBD1"]) -> pd.DataFrame:

    df = ohlc.copy()

    df = ssc.SwingPoints2(df)
    df = tools.ddt2(df)
    df = tools.weekly_rdata(df)

    df["mvf"] = (
        (tools.asc(df["close"], lookback=20) - df["low"])
        / tools.asc(df["close"], lookback=20)
        * 100
    )
    df["atr"] = tools.atr(df["high"], df["low"], df["close"], lookback=20)
    df["ldv"] = tools.lv(df["high"], df["low"], df["close"], lookback=4)
    df["signal"] = False

    df = df[-200:]  # Limit to last 200 rows for performance

    if df.empty:
        return df

    symbol = df.iloc[0].get("symbol", "")
    signals = pd.DataFrame()
    for d in range(1, len(df)):

        if "KBD1" in models:
            result = kbd1.signal(df.iloc[:d], symbol)
            signals = pd.concat(
                [signals, result[result["kbd1"].notna()]], ignore_index=True
            )

    print(f"Signals found for {symbol} : ", len(signals))
    return signals
