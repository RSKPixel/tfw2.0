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

    swing_data = df[df["swing_point"].notna()].tail(3)

    if len(df) < 3:
        return

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
        signal = {
            "model": "KBS7",
            "symbol": symbol,
            "signal": "buy" if buy else "sell",
            "setup_candle": swing_dates[0],
            "entry_date": swing_dates[0],
            "entry_price": swing_points[0],
            "entry_day_sl": None,
        }
        if buy:
            signal["entry_day_sl"] = swing_data.iloc[-1]["low"]
        else:
            signal["entry_day_sl"] = swing_data.iloc[-1]["high"]

        return signal
    return None
