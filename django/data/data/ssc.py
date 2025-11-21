import pandas as pd


def classify_bars(df):
    """
    Classify each bar as:
    DB  = Directional Bar
    ISB = Inside Bar
    OSB = Outside Bar
    """
    df["bartype"] = None

    # First bar is always DB
    df.iloc[0, df.columns.get_loc("bartype")] = "DB"

    for i in range(1, len(df)):
        prev_high = df.iloc[i - 1]["high"]
        prev_low = df.iloc[i - 1]["low"]
        high = df.iloc[i]["high"]
        low = df.iloc[i]["low"]

        # ISB: inside previous bar
        if high < prev_high and low > prev_low:
            df.at[df.index[i], "bartype"] = "ISB"

        # OSB: outside previous bar
        elif high > prev_high and low < prev_low:
            df.at[df.index[i], "bartype"] = "OSB"

        # All other cases are DB (normal direction bar)
        else:
            df.at[df.index[i], "bartype"] = "DB"
    return df


def generate_swings(df):
    df["swing"] = None

    for i in range(1, len(df)):
        high = df.iloc[i]["high"]
        low = df.iloc[i]["low"]
        bartype = df.iloc[i]["bartype"]

        prev_high = df.iloc[i - 1]["high"]
        prev_low = df.iloc[i - 1]["low"]
        previous_swing = df.iloc[i - 1]["swing"]
        current_swing = None

        if bartype == "DB":
            if high > prev_high:
                df.at[df.index[i], "swing"] = "high"
                current_swing = "high"

            elif low < prev_low:
                df.at[df.index[i], "swing"] = "low"
                current_swing = "low"

        if bartype == "OSB":
            if high > prev_high and low < prev_low:
                if previous_swing == "high":
                    df.at[df.index[i], "swing"] = "high"
                    current_swing = "high"
                elif previous_swing == "low":
                    df.at[df.index[i], "swing"] = "low"
                    current_swing = "low"

        # if bartype == "ISB":
        #     df.at[df.index[i], "swing"] = previous_swing
        #     current_swing = previous_swing

    return df


df = pd.read_json("nifty-dataset.json")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df[df["datetime"] >= pd.to_datetime("2025-06-25")]

df = classify_bars(df)
df = generate_swings(df)
df.to_clipboard()
print(df[["datetime", "close", "bartype", "swing"]])
