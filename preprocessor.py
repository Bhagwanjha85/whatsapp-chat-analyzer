"""
Data preprocessing module
Converts raw WhatsApp chat text into structured DataFrame
Handles different date formats and extracts temporal features
"""

import pandas as pd
import re
from collections import Counter
import emoji


def preprocess(data):
    """
    Processes raw WhatsApp chat data into structured DataFrame
    Handles both 12-hour and 24-hour time formats
    Returns DataFrame with parsed dates and additional time features
    """
    # Regex patterns for different time formats
    pattern_12hr = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APap][Mm]) - ([^:]+): (.+)"
    pattern_24hr = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{2}:\d{2}) - ([^:]+): (.+)"

    # Try matching different time formats
    matches_12hr = re.findall(pattern_12hr, data)
    matches_24hr = re.findall(pattern_24hr, data)

    # Create DataFrame based on detected format
    if matches_12hr:
        df = pd.DataFrame(matches_12hr, columns=["Date", "Time", "User", "Message"])
        df["Date-Time"] = pd.to_datetime(df["Date"] + " " + df["Time"],
                                         format="%d/%m/%Y %I:%M %p", errors="coerce")
    elif matches_24hr:
        df = pd.DataFrame(matches_24hr, columns=["Date", "Time", "User", "Message"])
        df["Date-Time"] = pd.to_datetime(df["Date"] + " " + df["Time"],
                                         format="%d/%m/%Y %H:%M", errors="coerce")
    else:
        return pd.DataFrame(columns=["Date-Time", "User", "Message"])

    # Clean and enhance data
    df = df[df["User"].str.strip() != ""]  # Remove empty users

    # Extract temporal features
    df["year"] = df["Date-Time"].dt.year
    df["month"] = df["Date-Time"].dt.month_name()
    df["day"] = df["Date-Time"].dt.day_name()
    df["hour"] = df["Date-Time"].dt.hour
    df["minute"] = df["Date-Time"].dt.minute

    if not df.empty:
        df['User'] = df['User'].str.strip().astype(str)
        df = df[df["User"].str.strip() != ""]

        # Extract temporal features
        df["year"] = df["Date-Time"].dt.year
        df["month"] = df["Date-Time"].dt.month_name()
        df["day"] = df["Date-Time"].dt.day_name()

        # Add proper categorical ordering for days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                      'Friday', 'Saturday', 'Sunday']
        df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)

    return df
