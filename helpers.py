import re
from collections import Counter
from textblob import TextBlob
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io


class GraphStyler:
    def __init__(self):
        self.themes = {
                "Dark": {
        "bg": "#121212",
        "text": "#EAEAEA",
        "grid": "#2A2A2A",
        "primary": "#1DB954",

    },
    "Light": {
        "bg": "#F9FAFB",
        "text": "#111827",
        "grid": "#E5E7EB",
        "primary": "#2563EB"
    },
    "Cyberpunk": {
        "bg": "#0A001F",
        "text": "#00FFFF",
        "grid": "#7F00FF",
        "primary": "#FF0080"
    },
    "Pastel": {
        "bg": "#FFF1F1",
        "text": "#4A4A4A",
        "grid": "#F2D7D9",
        "primary": "#A3C4F3"
    },
    "Minimalist": {
        "bg": "#FAFAFA",
        "text": "#2C2C2C",
        "grid": "#E6E6E6",
        "primary": "#5555FF"
    },
    "Jha Look": {
        "bg": "#EEEEEE",
        "text": "black",
        "grid": "#F0E4E0",
        "primary": "#00B4D8"

    }
        }
        self.current_theme = self.themes["Dark"]

    def update_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]

    def get_color_sequence(self, n):
        if self.current_theme == self.themes["Cyberpunk"]:
            return ['#FF33FF', '#00FFFF', '#00FF00', '#FFFF00']
        elif self.current_theme == self.themes["Pastel"]:
            return ['#9D8189', '#F08080', '#F4A261', '#5499C7']
        elif self.current_theme == self.themes["Minimalist"]:
            return ['#606060', '#A0A0A0', '#C0C0C0', '#404040']
        elif self.current_theme == self.themes["Jha Look"]:
            return ['#48BFE3', '#5390D9', '#0077B6', '#003566']
        else:
            return ['#25D366', '#075E54', '#8696A0', '#1F3440']

    def style_graph(self, fig, x_label, y_label):
        fig.update_layout(
            plot_bgcolor=self.current_theme["bg"],
            paper_bgcolor=self.current_theme["bg"],
            font=dict(family="Poppins", size=14, color=self.current_theme["text"]),

            xaxis=dict(
                title=f"{x_label}",
                title_font=dict(size=16, color=self.current_theme["text"]),
                showgrid=True,
                gridcolor=self.current_theme["grid"],
                zerolinecolor=self.current_theme["grid"]
            ),

            yaxis=dict(
                title=f"{y_label}",
                title_font=dict(size=16, color=self.current_theme["text"]),
                showgrid=True,
                gridcolor=self.current_theme["grid"],
                zerolinecolor=self.current_theme["grid"]
            ),
            bargap=0.3,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        return fig


def get_last_message_date(df):
    return df.iloc[-1]['Date-Time'].strftime('%d %b, %Y %I:%M %p') if not df.empty else "N/A"


def get_first_message_date(df):
    return df.iloc[0]['Date-Time'].strftime('%d %b, %Y %I:%M %p') if not df.empty else "N/A"


def count_words(messages):
    return sum(len(str(msg).split()) for msg in messages)


def count_media_messages(messages):
    return sum(1 for msg in messages if "<Media omitted>" in str(msg))


def count_links(messages):
    url_pattern = r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|in|gov|edu|info)\b'
    return sum(1 for msg in messages if re.search(url_pattern, str(msg)))


def get_sentiment(messages):
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for msg in messages:
        if "<Media omitted>" in str(msg):
            continue

        polarity = TextBlob(str(msg)).sentiment.polarity
        if polarity > 0.1:
            sentiments["Positive"] += 1
        elif polarity < -0.1:
            sentiments["Negative"] += 1
        else:
            sentiments["Neutral"] += 1
    return sentiments


# Toxicity & Spam Detection Logic
def get_toxicity_spam_report(messages):
    spam_keywords = [
        "free offer", "click here", "subscribe now", "win cash", "greatest deal", "promo code", "limited time",
        "guaranteed money", "call now", "urgent news", "buy now", "order today", "exclusive deal", "act fast",
        "special promotion", "hot offer", "don’t miss out", "best price", "lowest cost", "instant savings", "act now",
        "today only", "shop now", "get yours now", "clearance sale", "earn money", "make cash fast",
        "double your income", "easy money", "no investment required", "financial freedom", "get rich quick",
        "work from home", "save big", "massive discount", "big savings", "lowest rates", "extra income", "free gift",
        "bonus offer", "cash bonus", "claim your reward", "free trial", "complimentary access", "instant access",
        "join free", "claim now", "gift inside", "act immediately", "hurry up", "limited stock", "expires soon",
        "final notice", "last chance", "time running out", "immediate action required", "don’t delay",
        "offer ends tonight", "only a few left", "click below", "click this link", "check this out",
        "visit our website", "learn more now", "go here", "see for yourself", "get started now", "tap to claim",
        "download instantly", "miracle solution", "secret revealed", "100% success", "risk-free", "no strings attached",
        "unbelievable results", "guaranteed win", "once-in-a-lifetime offer", "proven system", "win big today",
        "online biz opportunity", "be your own boss", "start earning today", "no experience required", "signup bonus",
        "instant approval", "one-click access", "unlimited bandwidth", "easy registration", "Limited time offer",
        "offer deal", "diwali offer", "Great deal", "Deal offer", "Money back"
    ]
    toxic_keywords = [
        "idiot", "stupid", "dumb", "hate you", "shame", "worst", "loser", "ugly", "nonsense", "fool", "disgusting",
        "worthless", "trash", "pathetic", "moron", "annoying", "useless", "arrogant", "horrible", "crazy", "lazy",
        "jerk", "selfish", "nasty", "embarrassing", "terrible", "ridiculous", "toxic", "liar", "coward", "creep",
        "disgrace", "failure", "awful", "stupidhead", "dumbass", "fake", "cringe", "hopeless", "unwanted",
        "ignorant", "boring", "gross", "mean", "bad", "brainless", "nobody", "weak", "evil", "backstabber",
        "two-faced", "jealous", "crybaby", "clown", "drama queen", "lunatic", "cheap", "disrespectful",
        "crazy person", "bad attitude", "narrow-minded", "heartless", "cold", "bitter", "immature", "greedy",
        "rude", "dumb move", "stupid act", "worthless person", "horrid", "dirty", "ungrateful", "negative",
        "fake friend", "toxic person", "psycho", "sick mind", "trash talker", "backstabber", "unpleasant",
        "attention seeker", "overacting", "manipulative", "idiotic", "moronic", "shameless", "noob",
        "slow", "silly", "lame", "twisted", "hateful", "disgusted", "horrendous", "filthy",
        "nasty mind", "trash human", "bully", "obnoxious", "narcissist", "vile", "mean-spirited", "backstabber",
        "snake", "devil", "cowardly", "sarcastic", "hypocrite", "two-timer", "disloyal", "ignoramus",
        "lowlife", "dirtbag", "blockhead", "nitwit", "airhead", "chatterbox", "untrustworthy", "idiocracy",
        "dimwit", "pessimist", "hater", "blameworthy", "spoiled", "cold-hearted", "stone-hearted", "miserable",
        "maniac", "temperamental", "attention seeker", "crybaby", "complainer", "argumentative",
        "toxic soul", "broke-minded", "lousy", "problematic", "narrow-souled", "fake heart",
        "manipulator", "gaslighter", "schemer", "overdramatic", "immoral", "insensitive",
        "backstabber", "disloyal person", "unethical", "insolent", "ruthless", "domineering", "vindictive",
        "mean-minded", "obnoxious brat", "low mentality", "negative thinker", "unfriendly", "hostile", "spiteful",
        "troublemaker", "unfair", "unreliable", "irrational", "argument maker", "egoistic", "show-off",
        "attention hungry", "fake smile", "self-centered", "boastful", "judgmental", "irritating", "narrow-hearted",
        "uncivilized", "reckless", "harsh", "bullying", "complaint box", "twisted soul", "arrogant fool",
        "immoral person", "unpleasant mind", "venomous", "offensive", "dumb-minded", "rude soul", "negative vibe",
        "non-sense maker", "villain", "maniac thinker", "rotten", "filthy mind", "dark-hearted", "draining person",
        "malicious", "insulting", "rough-tongued", "argument lover", "toxic thinker", "bad-mouthed"
    ]

    report = {"Spam/Promo": 0, "Toxic/Rude": 0, "Clean": 0}

    for msg in messages:
        message = str(msg).lower()
        if "<media omitted>" in message:
            continue

        is_spam = any(k in message for k in spam_keywords)
        is_toxic = any(k in message for k in toxic_keywords)

        if is_spam and is_toxic:
            report["Toxic/Rude"] += 1
        elif is_toxic:
            report["Toxic/Rude"] += 1
        elif is_spam:
            report["Spam/Promo"] += 1
        else:
            report["Clean"] += 1

    return report


def get_top_users(df):
    return df['User'].value_counts().nlargest(10)


def analyze_active_days(df):
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    day_counts = df['day'].value_counts().reindex(days_order, fill_value=0)
    return day_counts


def create_daily_messages_bar_chart(df, styler):
    daily_counts = analyze_active_days(df).reset_index()
    daily_counts.columns = ['Day', 'Messages']

    fig = px.bar(daily_counts, x='Day', y='Messages',
                 color='Messages',
                 color_continuous_scale=[styler.current_theme["grid"], styler.current_theme["primary"]],
                 title='Total Messages by Day of the Week')

    fig = styler.style_graph(fig, 'Day of Week', 'Total Messages')
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return fig


def create_monthly_day_count_chart(df, styler):
    df['day_of_month'] = df['Date-Time'].dt.day

    day_counts = df['day_of_month'].value_counts().sort_index().reset_index()
    day_counts.columns = ['Day', 'Messages']

    fig = px.bar(day_counts, x='Day', y='Messages',
                 color='Messages',
                 color_continuous_scale=[styler.current_theme["grid"], styler.current_theme["primary"]],
                 title='Total Messages by Day of Month (1-31)')

    fig = styler.style_graph(fig, 'Day of Month', 'Total Messages')
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_xaxes(dtick=1)
    return fig


def create_monthly_message_count_chart(df, styler):
    df['month_num'] = df['Date-Time'].dt.month

    month_counts = df.groupby('month_num').size().reset_index(name='Messages')
    month_counts.columns = ['Month', 'Messages']

    fig = px.bar(month_counts, x='Month', y='Messages',
                 color='Messages',
                 color_continuous_scale=[styler.current_theme["grid"], styler.current_theme["primary"]],
                 title='Total Messages by Month Number (1-12)')

    fig = styler.style_graph(fig, 'Month Number', 'Total Messages')
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_xaxes(dtick=1)
    return fig


def create_top_users_bar_chart(df, styler):
    top_users_data = get_top_users(df).reset_index()
    top_users_data.columns = ['User', 'Messages']

    fig = px.bar(top_users_data, x='User', y='Messages',
                 color='Messages',
                 color_continuous_scale=[styler.current_theme["primary"], styler.current_theme["text"]],
                 title='Top 10 Most Active Users')

    fig = styler.style_graph(fig, 'User', 'Messages Sent')
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return fig


def create_wordcloud(messages):
    text = " ".join([str(msg) for msg in messages])
    stop_words = set(STOPWORDS)
    stop_words.update(
        ["media", "omitted", "Media", "omit", "message", "de", "to", "la", "you", "is", "a", "an", "the", "in", "it"])

    wc = WordCloud(width=800, height=400,
                   background_color='white',
                   stopwords=stop_words,
                   min_font_size=10)

    wc.generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0)
    img_buf.seek(0)
    plt.close()
    return img_buf


def create_monthly_timeline(df, styler):
    timeline = df.groupby(['year', 'month']).size().reset_index(name='Count')

    timeline['Date'] = pd.to_datetime(timeline['month'] + ' ' + timeline['year'].astype(str), format='%B %Y')
    timeline = timeline.sort_values('Date')
    timeline['Label'] = timeline['month'] + ' ' + timeline['year'].astype(str)

    fig = px.line(timeline, x='Label', y='Count', text='Count',
                  title='Monthly Message Activity (Line Plot)',
                  line_shape='spline')

    fig.update_traces(line_color=styler.current_theme["primary"], line_width=4, mode='lines+markers',
                      marker=dict(size=8, color=styler.current_theme["text"]))

    fig = styler.style_graph(fig, 'Month and Year', 'Message Count')

    fig.update_xaxes(tickangle=45, nticks=10)
    return fig


def create_monthly_area_timeline(df, styler):
    timeline = df.groupby(['year', 'month']).size().reset_index(name='Count')

    timeline['Date'] = pd.to_datetime(timeline['month'] + ' ' + timeline['year'].astype(str), format='%B %Y')
    timeline = timeline.sort_values('Date')
    timeline['Label'] = timeline['month'] + ' ' + timeline['year'].astype(str)

    fig = px.area(timeline, x='Label', y='Count',
                  title='Monthly Message Activity (Area Plot)',
                  line_shape='spline')

    fig.update_traces(fillcolor=styler.current_theme["primary"],
                      line=dict(color=styler.current_theme["primary"], width=2), opacity=0.7)

    fig = styler.style_graph(fig, 'Month and Year', 'Message Count')

    fig.update_xaxes(tickangle=45, nticks=10)
    return fig


def create_daily_activity_map(df, styler):
    activity = df.groupby(['day', 'hour']).size().reset_index(name='Count')

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    hours_order = list(range(24))

    full_index = pd.MultiIndex.from_product([days_order, hours_order], names=['day', 'hour'])
    activity = activity.set_index(['day', 'hour']).reindex(full_index, fill_value=0).reset_index()

    fig = px.density_heatmap(activity,
                             x='hour',
                             y='day',
                             z='Count',
                             histfunc='sum',
                             title='Activity Heatmap (Day vs. Hour)',
                             color_continuous_scale=["#111B21", styler.current_theme["primary"]])

    fig.update_layout(
        plot_bgcolor=styler.current_theme["bg"],
        paper_bgcolor=styler.current_theme["bg"],
        font=dict(family="Poppins", size=14, color=styler.current_theme["text"]),
        xaxis=dict(
            title='Hour of Day (0-23)',
            tickmode='array',
            tickvals=list(range(0, 24, 2)),
            showgrid=False
        ),
        yaxis=dict(title='Day of Week', autorange="reversed", showgrid=False)
    )

    return fig


# Toxicity & Spam Chart
def create_toxicity_spam_chart(report_data, styler):
    report_df = pd.DataFrame(report_data.items(), columns=['Category', 'Count'])

    color_map = {
        'Toxic/Rude': '#FF6347',
        'Spam/Promo': '#FFA500',
        'Clean': '#25D366'
    }

    fig = px.bar(report_df, x='Category', y='Count',
                 color='Category',
                 color_discrete_map=color_map,
                 title='Toxicity and Spam Report')

    fig = styler.style_graph(fig, 'Message Category', 'Total Count')
    fig.update_traces(marker_line_width=0, opacity=0.9, texttemplate='%{y}', textposition='outside')

    return fig


def create_reply_time_analysis(df, styler):
    top_10_users = get_top_users(df).index.tolist()
    filtered_df = df[df['User'].isin(top_10_users)].copy()

    if filtered_df['User'].nunique() < 2:
        return None

    filtered_df['Time_Diff'] = filtered_df['Date-Time'].diff()
    filtered_df['Prev_User'] = filtered_df['User'].shift(1)

    reply_df = filtered_df[
        (filtered_df['User'] != filtered_df['Prev_User']) & (filtered_df['Prev_User'].notna())].copy()

    reply_time_minutes = reply_df.groupby('User')['Time_Diff'].mean().dt.total_seconds() / 60

    reply_data = reply_time_minutes.reset_index(name='Avg_Reply_Time_Minutes')
    reply_data['Avg_Reply_Time'] = reply_data['Avg_Reply_Time_Minutes'].apply(
        lambda x: f"{int(x // 60)}h {int(x % 60)}m")

    reply_data['User'] = reply_data['User'].astype(str)

    fig = px.bar(reply_data, x='User', y='Avg_Reply_Time_Minutes',
                 text='Avg_Reply_Time',
                 color='Avg_Reply_Time_Minutes',
                 color_continuous_scale=[styler.current_theme["grid"], styler.current_theme["primary"]],
                 title='Average Reply Time (Lower is Faster) for Top 10 Active Users')

    fig = styler.style_graph(fig, 'User', 'Average Reply Time (Minutes)')
    fig.update_traces(marker_line_width=0, opacity=0.9, textposition='outside')

    fig.update_xaxes(
        type='category',
        tickangle=45,
        tickformat='d',
        categoryorder='total descending'
    )

    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', yaxis_tickformat=".0f")

    return fig