import pandas as pd
import re
from collections import Counter

def preprocess(data):
    pattern_12hr = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APap][Mm]) - ([^:]+): (.+)"
    pattern_24hr = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{2}:\d{2}) - ([^:]+): (.+)"

    matches_12hr = re.findall(pattern_12hr, data)
    matches_24hr = re.findall(pattern_24hr, data)

    df = pd.DataFrame()

    if matches_12hr:
        df = pd.DataFrame(matches_12hr, columns=["Date", "Time", "User", "Message"])
        try:
            df["Date-Time"] = pd.to_datetime(df["Date"] + " " + df["Time"],
                                             format="%d/%m/%Y %I:%M %p", errors="coerce")
        except:
             df["Date-Time"] = pd.to_datetime(df["Date"] + " " + df["Time"],
                                             format="%m/%d/%y %I:%M %p", errors="coerce")

    elif matches_24hr:
        df = pd.DataFrame(matches_24hr, columns=["Date", "Time", "User", "Message"])
        df["Date-Time"] = pd.to_datetime(df["Date"] + " " + df["Time"],
                                         format="%d/%m/%Y %H:%M", errors="coerce")

    else:
        return pd.DataFrame(columns=["Date-Time", "User", "Message"])

    df = df.dropna(subset=['Date-Time'])
    df = df[df["User"].str.strip() != ""]

    if df.empty:
        return df

    df['User'] = df['User'].str.strip().astype(str)

    df["year"] = df["Date-Time"].dt.year
    df["month"] = df["Date-Time"].dt.month_name()
    df["day"] = df["Date-Time"].dt.day_name()
    df["hour"] = df["Date-Time"].dt.hour
    df["minute"] = df["Date-Time"].dt.minute
    df['date_only'] = df['Date-Time'].dt.date

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)

    return df