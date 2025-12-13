import pandas as pd


def signal(df: pd.DataFrame, symbol: str = ""):

    df_original = df.copy()
    df_original["kesb"] = None
    df = df.copy()
    if df.iloc[-1]["swing"] not in ["high", "low"]:
        return df_original

    swing_data = df[df["swing_point"].notna()].tail(3)

    if len(df) < 3:
        return df_original

    # Reverse so index 0 = MOST RECENT swing
    swing_points = swing_data["swing_point"][::-1].to_list()
    swings = swing_data["swing"][::-1].to_list()
    swing_dates = swing_data.index[::-1].to_list()
    mvf = swing_data["mvf"][::-1].to_list()

    buy_p = swings == ["low", "high", "low"]
    sell_p = swings == ["high", "low", "high"]

    buy = buy_p and swing_points[0] < swing_points[2] and mvf[0] < mvf[2]
    sell = sell_p and swing_points[0] > swing_points[2] and mvf[0] > mvf[2]

    if buy or sell:
        df_original.at[df_original.index[-1], "kesb"] = "buy" if buy else "sell"
        df_original.at[df_original.index[-1], "signal"] = True

    return df_original
