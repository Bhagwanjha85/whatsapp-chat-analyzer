import streamlit as st
import pandas as pd
import plotly.express as px
from preprocessor import preprocess
from helpers import (
    GraphStyler,
    get_top_users,
    get_sentiment,
    count_words,
    count_media_messages,
    count_links,
    get_first_message_date,
    get_last_message_date,
    create_top_users_bar_chart,
    create_wordcloud,
    create_monthly_timeline,
    create_daily_activity_map,
    create_daily_messages_bar_chart,
    create_monthly_day_count_chart,
    create_monthly_message_count_chart,
    create_monthly_area_timeline,
    create_reply_time_analysis,
    get_toxicity_spam_report,  # NEW IMPORT
    create_toxicity_spam_chart  # NEW IMPORT
)
import zipfile
import io

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
*{
color:#DCDCDC;
margin:0px;
padding:0px;
}

body {
    font-family: 'Poppins', sans-serif;
    color: #E9EDEF;
}

.stApp {
    background-color:#0F1C2E;
}

.st-emotion-cache-1c7yb1t {
    margin-bottom: 50px;
}

.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #075E54;
    color: #E9EDEF;
    text-align: center;
    padding: 10px 0;
    z-index: 1000;
    box-shadow: 0 -3px 15px rgba(0, 0, 0, 0.4);
    font-size: 0.9em;
    transition: all 0.3s ease;
}

.fixed-footer a {
    color: #25D366;
    text-decoration: none;
    font-weight: 600;
}

.dashboard-card {
    background-color: #202C33;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(37, 211, 102, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: default;
    height: 100%;
}

.dashboard-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 35px rgba(37, 211, 102, 0.3);
}

.card-title {
    font-size: 1.1em;
    font-weight: 600;
    color: #8696A0;
    margin-bottom: 5px;
    text-transform: uppercase;
}

.card-value {
    font-size: 2.8em;
    font-weight: 700;
    color: #25D366;
    line-height: 1.2;
}

.css-1d391kg, .css-1dp549z {
    background-color: #0A192F !important;
}

.st-emotion-cache-1ft9j1m h2 {
    color: #25D366;
}

.stButton>button {
    background-color: #075E54;
    color: white;
    border-radius: 8px;
    border: 1px solid #25D366;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.stButton>button:hover {
    background-color: #008069;
    transform: scale(1.03);
}

.stPlotlyChart {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    margin-top: 20px;
}

.emoji-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    padding: 10px 0;
}

.emoji-item {
    font-size: 1.5em;
    text-align: center;
    background-color: #1F2C33;
    padding: 5px;
    border-radius: 8px;
    transition: background-color 0.2s;
}

.emoji-item:hover {
    background-color: #304047;
}

"""


def load_css(css_text):
    st.markdown(f'<style>{css_text}</style>', unsafe_allow_html=True)


def get_chat_data_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'zip':
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:

                txt_files = [f for f in z.namelist() if f.endswith('.txt')]
                if not txt_files:
                    st.error("No WhatsApp chat (.txt) file found inside the ZIP archive.")
                    return None

                with z.open(txt_files[0]) as f:
                    return f.read().decode("utf-8")
        except zipfile.BadZipFile:
            st.error("The uploaded file is a corrupted or invalid ZIP archive.")
            return None
        except UnicodeDecodeError:
            st.error("Could not decode file inside ZIP. Ensure it is a UTF-8 encoded text file.")
            return None

    elif file_type == 'txt':
        try:
            return uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("Could not decode file. Ensure it is a UTF-8 encoded text file.")
            return None

    else:
        st.error("Unsupported file type. Please upload a .txt or .zip file.")
        return None


def main_app():
    load_css(CUSTOM_CSS)

    st.set_page_config(
        layout="wide",
        page_title="WhatsApp Chat Analyzer",
        initial_sidebar_state="expanded"
    )

    st.sidebar.title("Configuration and Filters")

    uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt or .zip)", type=["txt", "zip"])

    selected_theme = st.sidebar.selectbox("Select Theme", [
        "Dark", "Light", "Cyberpunk", "Pastel",
        "Minimalist", "Jha Look"
    ])

    styler = GraphStyler()
    styler.update_theme(selected_theme)

    st.sidebar.markdown("---")

    st.title("WhatsApp Chat Analyzer Dashboard")
    st.markdown("Upload a file to start the analysis.")

    if uploaded_file is not None:

        raw_data = get_chat_data_from_file(uploaded_file)

        if raw_data is None:
            return

        df = preprocess(raw_data)

        if df.empty:
            st.error("No valid WhatsApp chat data found in the uploaded file. Please check the format.")
            return

        user_list = df['User'].unique().tolist()
        user_list.sort()
        user_list.insert(0, "Overall Chat")

        selected_user = st.sidebar.selectbox("Analyze data for:", user_list)

        if selected_user != "Overall Chat":
            filtered_df = df[df['User'] == selected_user]
            st.header(f"Analysis for {selected_user}")
        else:
            filtered_df = df
            st.header("Overall Chat Summary")

        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        total_messages = len(filtered_df)
        total_words = count_words(filtered_df['Message'])
        media_count = count_media_messages(filtered_df['Message'])
        link_count = count_links(filtered_df['Message'])
        first_date = get_first_message_date(df)
        last_date = get_last_message_date(df)

        with col1:
            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="card-title">Total Messages</div>
                    <div class="card-value">{total_messages}</div>
                    <p style="font-size:0.9em; color:#8696A0;">Last Message: {last_date.split(',')[0]}</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            avg_words_per_msg = round(total_words / total_messages, 1) if total_messages else 0
            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="card-title">Total Words</div>
                    <div class="card-value">{total_words}</div>
                    <p style="font-size:0.9em; color:#8696A0;">Avg. {avg_words_per_msg} words/msg</p>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            media_percentage = round(media_count / total_messages * 100, 1) if total_messages else 0
            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="card-title">Media Messages</div>
                    <div class="card-value">{media_count}</div>
                    <p style="font-size:0.9em; color:#8696A0;">{media_percentage}% of total</p>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="card-title">Links Shared</div>
                    <div class="card-value">{link_count}</div>
                    <p style="font-size:0.9em; color:#8696A0;">Started: {first_date.split(',')[0]}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<h2 style='color:#25D366; margin-top: 30px;'>Graphs and Patterns</h2>", unsafe_allow_html=True)

        st.markdown("---")
        if selected_user == "Overall Chat":
            st.subheader("Top Active Users")
            fig_top_users = create_top_users_bar_chart(filtered_df, styler)
            st.plotly_chart(fig_top_users, use_container_width=True)

            st.markdown("---")
            st.subheader("Average Reply Time Analysis")
            fig_reply_time = create_reply_time_analysis(df, styler)
            if fig_reply_time:
                st.plotly_chart(fig_reply_time, use_container_width=True)
            else:
                st.info("Reply time analysis requires a chat with at least two active users.")

        else:
            st.subheader(f"{selected_user}'s Activity Timeline (Line Plot)")
            fig_timeline = create_monthly_timeline(filtered_df, styler)
            st.plotly_chart(fig_timeline, use_container_width=True)

            st.markdown("---")
            st.subheader(f"{selected_user}'s Activity Timeline (Area Plot)")
            fig_area_timeline = create_monthly_area_timeline(filtered_df, styler)
            st.plotly_chart(fig_area_timeline, use_container_width=True)

        st.markdown("---")
        st.subheader("Daily Message Activity (Day of Week)")
        fig_daily_bar = create_daily_messages_bar_chart(filtered_df, styler)
        st.plotly_chart(fig_daily_bar, use_container_width=True)

        st.markdown("---")
        st.subheader("Message Activity by Month Number (1-12)")
        fig_monthly_num = create_monthly_message_count_chart(filtered_df, styler)
        st.plotly_chart(fig_monthly_num, use_container_width=True)

        st.markdown("---")
        st.subheader("Message Activity by Day of Month")
        fig_monthly_day = create_monthly_day_count_chart(filtered_df, styler)
        st.plotly_chart(fig_monthly_day, use_container_width=True)

        st.markdown("---")
        st.subheader("Sentiment Summary")
        sentiment_counts = get_sentiment(filtered_df['Message'])
        sentiment_df = pd.DataFrame(sentiment_counts.items(), columns=['Sentiment', 'Count'])

        fig_sentiment = px.pie(sentiment_df, values='Count', names='Sentiment',
                               color_discrete_sequence=['#25D366', '#075E54', '#8696A0'])
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
        fig_sentiment = styler.style_graph(fig_sentiment, '', '')
        fig_sentiment.update_layout(title_text='Sentiment Breakdown')
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # NEW FEATURE: Toxicity and Spam Report
        st.markdown("---")
        st.subheader("Toxicity and Spam Detection Report")
        toxicity_report = get_toxicity_spam_report(filtered_df['Message'])
        fig_toxicity = create_toxicity_spam_chart(toxicity_report, styler)
        st.plotly_chart(fig_toxicity, use_container_width=True)
        # End of New Feature

        st.markdown("---")
        st.subheader("Chat Activity Heatmap (Day vs. Hour)")
        fig_heatmap = create_daily_activity_map(filtered_df, styler)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("---")
        st.subheader("Word Frequency Analysis")

        st.markdown("##### Most Used Words")
        wordcloud_img = create_wordcloud(filtered_df['Message'])
        st.image(wordcloud_img, use_container_width=True, caption="Visual representation of frequent words")


    else:
        st.info("Upload your WhatsApp chat (.txt or .zip) file to begin. Use the 'Export Chat' option on WhatsApp.")

    st.markdown("""
        <div class="fixed-footer">
            WhatsApp Chat Analyzer | Developed by: Bhagwan Ji Jha
        </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    try:
        main_app()
    except Exception as e:
        st.error(f"An error occurred during application execution: {e}")