import streamlit as st
import preprocessor
from helpers import *
import plotly.express as px


# 🎨 Custom Styles
st.markdown("""
    <style>
        .stApp { 
            background: linear-gradient(135deg, #654ea3, #eaafc8); 
            color:#ffffff;
        }
        .stSidebar { 
            background: linear-gradient(155deg, #00C9B1, #2A3F5F);
            color:#9BFF2E;
        }
        .info-box {
            background-color: #ffffff; 
            color:#11998e;
            padding: 15px;
            border-radius: 10px; 
            border: 2px solid #654ea3;
            margin-bottom: 10px;
        }
        
        div[data-testid="stSidebarNav"] + div {
            position: relative;
            min-height: 90vh;
        }
        .sidebar-footer {
            position: absolute;
            color:orange;
            top:0;
            width: 100%;
            margin-top:54%;
            padding: 1rem;
            background: inherit;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
    </style>""", unsafe_allow_html=True)

# Initialize styler
styler = GraphStyler()

# Streamlit App UI
def main():
    st.sidebar.title("📊 WhatsApp Chat Analyzer")
    uploaded_file = st.sidebar.file_uploader("📂 Upload your WhatsApp Chat (.txt)", type=["txt"])

    with st.sidebar:
        # ... existing sidebar elements ...

        # Add after all other sidebar elements but before main content
        st.markdown("---")
        st.markdown('<div class="sidebar-footer">'
                    '🙏 App created by Bhagwan Jha\n\n'
                    '📧 Contact: bk.jha.3297@gmail.com\n'
                    '🌐 [GitHub](https://github.com/Bhagwanjha85)'
                    
                    '</div>',
                    unsafe_allow_html=True)

    if uploaded_file:
        data = uploaded_file.getvalue().decode("utf-8")
        df = preprocessor.preprocess(data)

        if not df.empty:
            display_analysis(df)
        else:
            st.warning("⚠️ No messages found in the uploaded file.")

def display_analysis(df):
    st.write("### 🔍 Processed Chat Data:")
    st.dataframe(df)

    user_list = ["Overall"] + sorted(df["User"].unique().tolist())
    selected_user = st.sidebar.selectbox("👥 Select a User", user_list)

    if st.sidebar.button("🔎 Analyze Chat"):
        user_df = df if selected_user == "Overall" else df[df["User"] == selected_user]
        stats = calculate_statistics(user_df, df)
        display_basic_insights(stats)
        visualize_data(stats, user_df)
        display_advanced_analysis(user_df)
        st.success("✅ Analysis Complete!")



def calculate_statistics(user_df, df):
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
        "Conversation Starters": get_conversation_starters(df)
    }


def display_basic_insights(stats):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="info-box">📨 <b>Total Messages:</b> {stats["Total Messages"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">✍️ <b>Total Words:</b> {stats["Total Words"]}</div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="info-box">📸 <b>Media Messages:</b> {stats["Media Messages"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🔗 <b>Links Shared:</b> {stats["Links Shared"]}</div>',
                    unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">📅 <b>First Message Date:</b> {stats["First Message Date"]}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">💬 <b>Longest Message:</b> {stats["Longest Message"]}</div>',
                unsafe_allow_html=True)

def visualize_data(stats, user_df):
    visualize_top_users(stats)
    visualize_sentiment(stats)
    visualize_offensive_words(stats)
    visualize_emojis(user_df)
    visualize_conversation_starters(stats)

def visualize_top_users(stats):
    st.write("### 🏆 Top 5 Active Users")
    fig_users = px.bar(stats["Top Users"], x=stats["Top Users"].index, y=stats["Top Users"].values,
                       labels={'x': 'User', 'y': 'Messages Sent'})
    st.plotly_chart(styler.style_graph(fig_users, "User", "Messages Sent"))

def visualize_sentiment(stats):
    st.write("### 📊 Sentiment Analysis")
    fig_sentiment = px.bar(x=list(stats["Sentiment"].keys()), y=list(stats["Sentiment"].values()),
                           labels={'x': 'Sentiment', 'y': 'Count'})
    st.plotly_chart(styler.style_graph(fig_sentiment, "Sentiment", "Count"))

def visualize_offensive_words(stats):
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