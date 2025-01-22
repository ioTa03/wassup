import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns

# Set up page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="WhatsApp Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for background blur, spinner styling, and loading text
st.markdown(
    """
    <style>
        .loader-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
            z-index: 9999;
            flex-direction: column;
            color: white;
        }
        .loader {
            border: 16px solid #f3f3f3;
            border-top: 16px solid #3498db;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
        }
        .loader-text {
            margin-top: 20px;
            font-size: 20px;
            font-weight: bold;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Setup
st.sidebar.title("That's up on your WhatsApp")
st.sidebar.write("Analyze your WhatsApp chat data easily and beautifully!")

# File Upload and Chat Preview Section
st.title("💬 WhatsApp Chat Analyzer")
st.markdown("""
    Welcome to the **WhatsApp Chat Analyzer**!  
    Upload your WhatsApp chat export file, and we'll help you analyze patterns, frequencies, and more.
""")

uploaded_file = st.file_uploader("📂 Upload your chat file", type=["txt"])

if uploaded_file:
    try:
        st.success(f"File uploaded: {uploaded_file.name}")
        chat_data = uploaded_file.read().decode("utf-8")

        # Chat Preview
        with st.expander("📜 Chat Preview"):
            st.text_area("Chat Content", chat_data[:1000], height=300)

        st.info("Further analysis tools will appear here!")

        # Preprocessing the uploaded file
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        # User Selection
        selected_user = st.sidebar.selectbox("Delve deeper into: ", user_list)

        if st.sidebar.button("Let's Go"):
            # Show the loader on top of the page with blur and loading text
            st.markdown('<div class="loader-container"><div class="loader"></div><div class="loader-text">One moment, please wait...</div></div>', unsafe_allow_html=True)

            # Show a spinner while data is being fetched
            with st.spinner("Fetching data... Please wait!"):
                # Fetching Stats
                number_messages, words, num_media_messages, links = helper.fetch_stats(selected_user, df)
                c1, c2, c3, c4 = st.columns(4)

                # Displaying Stats
                with c1:
                    st.header("Total Messages")
                    st.title(number_messages)
                with c2:
                    st.header("Total Words")
                    st.title(words)
                with c3:
                    st.header("Total Media Shared")
                    st.title(num_media_messages)
                with c4:
                    st.header("Links Shared")
                    st.title(links)

                # Monthly Timeline
                st.title("Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                sns.lineplot(data=timeline, x='time', y='message', ax=ax, color='black')
                ax.set_xticklabels(ax.get_xticks(), rotation=90)
                st.pyplot(fig)

                # Daily Timeline
                st.title("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                sns.lineplot(data=daily_timeline, x='only_date', y='message', ax=ax, color='black')
                ax.set_xticklabels(ax.get_xticks(), rotation=90)
                st.pyplot(fig)

                # Activity Map
                st.title('Activity Map')
                col1, col2 = st.columns(2)

                with col1:
                    st.header("Most busy day")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    sns.barplot(x=busy_day.index, y=busy_day.values, ax=ax, color='purple')
                    ax.set_xticklabels(ax.get_xticks(), rotation=90)
                    st.pyplot(fig)

                with col2:
                    st.header("Most busy month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    sns.barplot(x=busy_month.index, y=busy_month.values, ax=ax, color='orange')
                    ax.set_xticklabels(ax.get_xticks(), rotation=90)
                    st.pyplot(fig)

                st.title("Weekly Activity Map")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, cmap="coolwarm", ax=ax)
                st.pyplot(fig)

                # Busiest Users
                if selected_user == 'Overall':
                    st.title('Busiest People in the Group')
                    x, new_df = helper.most_busy_users(df)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig, ax = plt.subplots(figsize=(8, 4))
                        sns.barplot(x=x.index, y=x.values, ax=ax, color='black')
                        ax.set_xticklabels(ax.get_xticks(), rotation=90)
                        st.pyplot(fig)

                    with col2:
                        st.dataframe(new_df)

                # Word Cloud
                st.title("Word Cloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots(figsize=(6, 6))
                ax.imshow(df_wc)
                ax.axis("off")
                st.pyplot(fig)

                # Most Common Words
                most_common_df = helper.most_common_words(selected_user, df)
                st.title('Most Common Words')
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.barplot(data=most_common_df, y=0, x=1, ax=ax, palette="viridis", orient="h")
                ax.set_yticklabels(most_common_df[0])
                st.pyplot(fig)

                # Emojis Used
                emoji_df = helper.emojis_helper(selected_user, df)
                st.title("Emojis Used in the Chat")
                top_10_emoji_df = emoji_df.head(10)

                font_path = "NotoColorEmoji-Regular.ttf"
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()

                fig, ax = plt.subplots(figsize=(6, 6))
                ax.pie(top_10_emoji_df[1], labels=top_10_emoji_df[0], autopct="%0.2f", colors=sns.color_palette("pastel"))
                st.pyplot(fig)

            st.markdown('<style>.loader-container { display: none; }</style>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
else:
    st.warning("No file uploaded yet. Please upload a WhatsApp chat file.")

# Footer
st.markdown("""
    ---
    Made with [❤️](https://github.com/iota03)
""")
