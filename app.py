"""
Main Streamlit application for WhatsApp Chat Analysis
Handles UI, file upload, and analysis orchestration
"""

import streamlit as st
from matplotlib import pyplot as plt
import preprocessor
from helpers import *
import helpers as helper
import seaborn as sns
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud

# 🎨 Custom CSS styles for the application
st.markdown("""
    <style>
        /* Main app background gradient */
        .stApp { 
            background-image: url('https://xmple.com/wallpaper/highlight-black-red-gradient-linear-3840x2160-c2-000000-8b0000-l-67-a-345-f-21.svg'); 
            color:#ffffff;
            background-repeat: no-repeat, repeat;
             background-size: cover;
             background-position: center;
        }
        /* Sidebar styling with gradient */
        .stSidebar { 
            background: linear-gradient(155deg, #00C9B1, #2A3F5F);
            color:white;
            
        }
        /* Custom info box styling */
        .info-box {
            background-color: #ffffff; 
            color:black;
            padding: 15px;
            border-radius: 10px; 
            border: 2px solid #654ea3;
            margin-bottom: 10px;
        }
        /* Footer positioning in sidebar */
        .sidebar-footer {
            position:absolute;
            top:40px;
            width: 100%;
            margin-top:54%;
            text-align:center;
            padding: 1rem;
            background-image: url('https://www.kythelmet.com/bg-world.svg'); 
            color:#ffffff;
            background-repeat: no-repeat, repeat;
            background-size: cover;
            background-position: center;
            border-radius:10px;
            color:gold;
        }
        .sidebar-footer a{
         # text-decoration:none;
         color:white;
         }
         
         
    </style>""", unsafe_allow_html=True)

# Initialize custom graph styler
styler = GraphStyler()


def show_detailed_instructions():
    """Displays comprehensive instructions that auto-hide when file is uploaded"""
    st.markdown("""
    
    """, unsafe_allow_html=True)



def main():
    """
    Main function that runs the Streamlit app
    Handles file upload and initializes analysis
    """

    # Initialize instructions placeholder
    instructions_placeholder = st.empty()

    # Show instructions only if no file uploaded
    if 'uploaded' not in st.session_state:
        instructions_placeholder.markdown("""
           <div style='margin-left: 15px;'>
            <div style='margin: 15px 0;'>
                <h3 style='color: #00FFFF'>Step 1: Export WhatsApp Chat</h3>
                <div style='margin-left: 20px;'>
                    <p><strong>Android/iOS:</strong></p>
                    <ul>
                        <li>Open target chat in WhatsApp</li>
                        <li>Tap ⋮ Menu → More → Export chat</li>
                        <li>Select <span style='color:orange'>"Without Media"</span> option</li>
                        <li>Click Ok and <span style='color:#9BFF2E'>"Download the file in your own system"</span> option</li>
                    </ul>
                    
                    
            </div>

            <div style='margin: 15px 0;'>
                <h3 style='color: #00FFFF'>Step 2: Upload File</h3>
                <div style='margin-left: 20px;'>
                    <ul>
                        <li>Look for uploader in left sidebar (<span style='color:#eaafc8'>📂 icon</span>)</li>
                        <li>Select exported .txt file</li>
                        <li>Wait for file processing (2-10 seconds)</li>
                    </ul>
                </div>
            </div>

            <div style='margin: 15px 0;'>
                <h3 style='color: #00FFFF'>Step 3: Analyze Chat</h3>
                <div style='margin-left: 20px;'>
                    <ul>
                        <li>Select user from dropdown (or "Overall")</li>
                        <li>Click <span style='color:#38ef7d'>"🔎 Analyze Chat"</span> button</li>
                        <li>Scroll to explore visualizations:
                            <ul>
                                <li>📈 Message statistics</li>
                                <li>😀 Emoji usage</li>
                                <li>📅 Activity patterns</li>
                                <li>📊 Sentiment analysis</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.sidebar.title("WHATSAPP CHAT ANALYZER")
    # File processing and analysis trigger
    uploaded_file = st.sidebar.file_uploader("📂 Upload your WhatsApp Chat (.txt)", type=["txt"])

    # Sidebar footer with creator information
    with st.sidebar:
        st.markdown("---")
        st.markdown('<div class="sidebar-footer">'
                    '© Bhagwan Jha @ 2025-26 \n\n'
                    '(https://github.com/Bhagwanjha85)</div>',
                    unsafe_allow_html=True)
    if uploaded_file:
        # Clear instructions when file is uploaded
        instructions_placeholder.empty()
        st.session_state.uploaded = True

        # Rest of your processing code
        data = uploaded_file.getvalue().decode("utf-8")
        df = preprocessor.preprocess(data)

        if not df.empty:
            display_analysis(df)
        else:
            st.warning("⚠️ No messages found in the uploaded file.")


def display_analysis(df):
    """
    Controls the main analysis workflow
    Handles user selection and analysis triggering
    """
    st.write("### 🔍 Processed Chat Data:")

    # User selection dropdown
    user_list = ["Overall"] + sorted(df["User"].unique().tolist())
    selected_user = st.sidebar.selectbox("👥 Select a User", user_list)

    if st.sidebar.button("🔎 Analyze Chat"):
        user_df = df if selected_user == "Overall" else df[df["User"] == selected_user]
        stats = calculate_statistics(user_df, df)  # Calculate key metrics

        # Display results
        display_basic_insights(stats)
        visualize_data(stats, user_df)
        display_advanced_analysis(user_df)
        st.success("✅ Analysis Complete!")


def calculate_statistics(user_df, df):
    """
    Computes various chat statistics
    Returns dictionary of calculated metrics
    """
    return {
        "Total Messages": user_df.shape[0],
        "Total Words": count_words(user_df["Message"]),
        "Media Messages": count_media_messages(user_df["Message"]),
        "Links Shared": count_links(user_df["Message"]),
        "First Message Date": get_first_message_date(df),
        "Longest Message": get_longest_message(user_df["Message"]),
        "Sentiment": get_sentiment(user_df["Message"]),
        "Offensive Words": detect_offensive_words(user_df["Message"]),
        "Top Users": get_top_users(df),
        "Conversation Starters": get_conversation_starters(df),
        "Last Message Date": get_last_message_date(df),
    }


def display_basic_insights(stats):
    """
    Displays key statistics in styled info boxes
    Uses two-column layout for better organization
    """
    col1, col2 = st.columns(2)

    # for Display total msg. :
    with col1:
        st.markdown(f'<div class="info-box">📨 <b>Total Messages:</b> {stats["Total Messages"]}</div>',
                    unsafe_allow_html=True)

        # for Display total words:
        st.markdown(f'<div class="info-box">✍️ <b>Total Words:</b> {stats["Total Words"]}</div>',
                    unsafe_allow_html=True)

    # for Display how much media msg. shared:
    with col2:
        st.markdown(f'<div class="info-box">📸 <b>Media Messages:</b> {stats["Media Messages"]}</div>',
                    unsafe_allow_html=True)

        # for Display total link share in a group/individually:
        st.markdown(f'<div class="info-box">🔗 <b>Links Shared:</b> {stats["Links Shared"]}</div>',
                    unsafe_allow_html=True)

    # for Display first Message Date:
    st.markdown(f'<div class="info-box">📅 <b>First Message Date:</b> {stats["First Message Date"]}</div>',
                unsafe_allow_html=True)

    # for Display Last Message Date:
    st.markdown(f'<div class="info-box">📅 <b>Last Message Date:</b> {stats["Last Message Date"]}</div>',
                unsafe_allow_html=True)

    # for Display Longest Message :
    st.markdown(f'<div class="info-box">💬 <b>Longest Message:</b> {stats["Longest Message"]}</div>',
                unsafe_allow_html=True)


def visualize_data(stats, user_df):
    visualize_top_users(stats)
    visualize_sentiment(stats)
    visualize_offensive_words(stats)
    visualize_emojis(user_df)
    visualize_conversation_starters(stats)


# Top 5 active Users Visualization:
def visualize_top_users(stats):
    st.write("### 🏆 Top 5 Active Users")
    top_users = stats["Top Users"].reset_index()
    top_users.columns = ['User', 'Messages']

    top_users['User'] = top_users['User'].apply(lambda x: str(x).split('\n')[0])

    fig_users = px.bar(top_users, x='User', y='Messages',
                       labels={'User': 'User', 'Messages': 'Messages Sent'})
    fig_users.update_xaxes(type='category', tickangle=45)
    st.plotly_chart(styler.style_graph(fig_users, "User", "Messages Sent"))


# to display the sentiment analysis of the users
def visualize_sentiment(stats):
    st.write("### 📊 Sentiment Analysis")
    fig_sentiment = px.bar(x=list(stats["Sentiment"].keys()), y=list(stats["Sentiment"].values()),
                           labels={'x': 'Sentiment', 'y': 'Count'})
    st.plotly_chart(styler.style_graph(fig_sentiment, "Sentiment", "Count"))


# to display the most offensive used users
def visualize_offensive_words(stats, selected_user=None, df=None):
    if stats["Offensive Words"]:
        st.write("### 🚨 Most Used Offensive Words:")
        fig_offensive = px.bar(x=list(stats["Offensive Words"].keys()),
                               y=list(stats["Offensive Words"].values()),
                               labels={'x': 'Words', 'y': 'Count'})
        st.plotly_chart(styler.style_graph(fig_offensive, "Words", "Count"))
    else:
        st.write("✅ No offensive words detected!")


def visualize_emojis(user_df):
    st.write("### 😀 Most Used Emoji(s)")
    emoji_counts = extract_emojis(user_df["Message"])
    if emoji_counts:
        df_emoji = pd.DataFrame(emoji_counts.items(), columns=["Emoji", "Count"]).nlargest(5, "Count")
        fig_emoji = px.pie(df_emoji, names="Emoji", values="Count",
                           color_discrete_sequence=px.colors.sequential.Viridis_r)
        fig_emoji.update_layout(plot_bgcolor='#0A192F', paper_bgcolor='#1a2f4b', font=dict(color='yellow'))
        st.plotly_chart(fig_emoji)
    else:
        st.write("❌ No emojis found in messages!")


# to display Who Starts Most Conversations ?
def visualize_conversation_starters(stats):
    starters = stats["Conversation Starters"]
    if not starters.empty:
        st.write("### 🚀 Who Starts Most Conversations")
        fig = px.treemap(starters, path=['User'], values='Count',
                         color='Count', color_continuous_scale='Teal')
        fig.update_layout(
            plot_bgcolor=styler.current_theme["bg"],
            paper_bgcolor=styler.current_theme["bg"],
            font=dict(color=styler.current_theme["text"]),
            margin=dict(t=50, l=25, r=25, b=25)
        )
        st.plotly_chart(fig)
    else:
        st.write("No conversation starters data available.")

# to display the Most Active Days Per Week according to hrs. and days .
def display_advanced_analysis(user_df):
    st.write("### 📅 Most Active Days Per Week")
    day_counts, day_percentages = analyze_active_days(user_df)

    tab1, tab2 = st.tabs(["Annotated Heatmap", "Radial Distribution"])
    with tab1:
        display_heatmap(user_df)
    with tab2:
        display_radial_chart(day_counts)

    display_daily_distribution(day_counts, day_percentages)


def display_heatmap(user_df):
    st.write("#### 🔥 Hourly-Daily Activity Heatmap")
    heatmap_data = user_df.groupby(['day', 'hour']).size().unstack().fillna(0)
    fig_heat = px.imshow(heatmap_data, labels=dict(x="Hour", y="Day", color="Messages"),
                         x=heatmap_data.columns, y=heatmap_data.index, color_continuous_scale='RdBu_r', aspect="auto")
    fig_heat.update_xaxes(side="top")
    st.plotly_chart(fig_heat)


def display_radial_chart(day_counts):
    st.write("#### 🎯 Activity Radial Distribution")
    fig_radial = px.line_polar(day_counts.reset_index(), r=day_counts.values, theta='day',
                               line_close=True, color_discrete_sequence=['#ff6b6b'], template='plotly_dark')
    fig_radial.update_traces(fill='toself')
    st.plotly_chart(fig_radial)


def display_daily_distribution(day_counts, day_percentages):
    st.write("#### 📊 Daily Message Distribution")
    fig_days = px.bar(day_counts, x=day_counts.index, y=day_counts.values,
                      color=day_percentages.values, color_continuous_scale='Magma',
                      labels={'x': 'Day', 'y': 'Messages'}, text=day_percentages.apply(lambda x: f'{x}%'))
    fig_days.add_scatter(x=day_counts.index, y=day_counts.values, mode='lines+markers',
                         name='Trend', line=dict(color='#38ef7d', width=4))
    st.plotly_chart(styler.style_graph(fig_days, "Day", "Messages"))


if __name__ == "__main__":
    main()
