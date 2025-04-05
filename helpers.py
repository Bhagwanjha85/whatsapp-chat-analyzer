"""
Helper functions for data processing and visualization
Contains statistical calculations and graph styling logic
"""

import re
from collections import Counter
from textblob import TextBlob
import emoji
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud


# Add Last Message Date to Statistics:
def get_last_message_date(df):
    return df.iloc[-1]['Date'] if not df.empty else "N/A"


class GraphStyler:
    def __init__(self):
        self.themes = {
            "Dark": {"bg": "#0A192F", "text": "#FFFFFF", "grid": "#444444"},
            "Light": {"bg": "#FFFFFF", "text": "#000000", "grid": "#DDDDDD"},
            "Cyberpunk": {"bg": "#000000", "text": "#00FF00", "grid": "#4444FF"},
            "Pastel": {"bg": "#F8EDEB", "text": "#6D6875", "grid": "#B5838D"}
        }
        self.current_theme = self.themes["Dark"]

    def update_theme(self, theme_name, custom_bg=None, custom_text=None, custom_grid=None):
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
        else:
            self.current_theme = {"bg": custom_bg, "text": custom_text, "grid": custom_grid}

    def style_graph(self, fig, x_label, y_label):
        fig.update_layout(
            plot_bgcolor=self.current_theme["bg"],
            paper_bgcolor=self.current_theme["bg"],
            xaxis=dict(title=x_label, title_font=dict(size=18, color=self.current_theme["text"]), showgrid=False),
            yaxis=dict(title=y_label, title_font=dict(size=18, color=self.current_theme["text"]), showgrid=True),
            font=dict(family="Arial", size=20, color=self.current_theme["text"]),
            bargap=0.3,
            margin=dict(l=50, r=50, t=70, b=50),
        )
        return fig

def count_words(messages):
    """Calculates total word count across all messages"""
    return sum(len(msg.split()) for msg in messages)

def detect_offensive_words(messages):
    """
    Detects and counts predefined offensive words
    Returns Counter object with word frequencies
    """
    offensive_words = ["nude", "sex", "fuck", "bitch", "asshole", "porn", "fool", "dick", "boobs", "slut",
                       "madharchod", "nigger", "nigga", "cunt", "pussy", "lund", "lora", "chode", "mc",
                       "ma ka bhosda", "gandmara", "fuckyou", "fuck you", "laude"]
    return Counter(word.lower() for msg in messages for word in msg.split() if word.lower() in offensive_words)

def count_media_messages(messages):
    return sum(1 for msg in messages if "<Media omitted>" in msg)


def count_links(messages):
    url_pattern = r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|in|gov|edu|info)\b'
    return sum(1 for msg in messages if re.search(url_pattern, msg))


def get_first_message_date(df):
    return df.iloc[0]['Date'] if not df.empty else "N/A"


def get_longest_message(messages):
    return max(messages, key=len) if messages.any() else ""


def get_sentiment(messages):
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for msg in messages:
        polarity = TextBlob(msg).sentiment.polarity
        sentiments["Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"] += 1
    return sentiments


def get_top_users(df):
    return df['User'].value_counts().nlargest(5)


def extract_emojis(messages):
    all_emojis = [char for msg in messages for char in msg if emoji.is_emoji(char)]
    return Counter(all_emojis)


def analyze_active_days(df):
    """Ensure complete day coverage with zero-filled missing days"""
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']

    # Count messages per day
    day_counts = df['day'].value_counts()

    # Create complete index with all days
    day_counts = day_counts.reindex(days_order, fill_value=0)

    # Calculate percentages
    total_messages = day_counts.sum()
    day_percentages = (day_counts / total_messages * 100).round(2) if total_messages > 0 \
        else pd.Series([0] * 7, index=days_order)

    return day_counts, day_percentages


def get_conversation_starters(df):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['date_only'] = df['Date'].dt.date
    first_messages = df.groupby('date_only')['User'].first().reset_index()
    starter_counts = first_messages['User'].value_counts().reset_index()
    starter_counts.columns = ['User', 'Count']
    return starter_counts


def get_conversation_starters(df):
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    except Exception as e:
        print(f"Date conversion error: {e}")
        return pd.DataFrame()

    df = df.dropna(subset=['Date'])
    df = df.sort_values('Date')

    df['date_only'] = df['Date'].dt.date
    first_messages = df.groupby('date_only')['User'].first().reset_index()

    starter_counts = first_messages['User'].value_counts().reset_index()
    starter_counts.columns = ['User', 'Count']

    # Extract temporal features
    df["year"] = df["Date-Time"].dt.year
    df["month"] = df["Date-Time"].dt.month_name()
    df["day"] = df["Date-Time"].dt.day_name()

    # Add proper categorical ordering for days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)
    return starter_counts
