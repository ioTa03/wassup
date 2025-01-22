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
        /* Full-page spinner background blur */
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
            backdrop-filter: blur(5px); /* Blur the background */
            z-index: 9999; /* Keep the loader on top */
            flex-direction: column; /* Stack the spinner and text vertically */
            color: white;
        }
        /* Spinner styling */
        .loader {
            border: 16px solid #f3f3f3;
            border-top: 16px solid #3498db;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
        }
        /* Text Styling */
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
                    # monthly timeline
                st.title("Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # daily timeline
                st.title("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # activity map
                st.title('Activity Map')
                col1, col2 = st.columns(2)

                with col1:
                    st.header("Most busy day")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.header("Most busy month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                st.title("Weekly Activity Map")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots()
                ax = sns.heatmap(user_heatmap)
                st.pyplot(fig)
                # Finding the Busiest Users (Overall view)


                if selected_user == 'Overall':
                    st.title('Busiest People in the Group')
                    x, new_df = helper.most_busy_users(df)
                    fig, ax = plt.subplots(figsize=(8, 4))

                    col1, col2 = st.columns(2)

                    with col1:
                        ax.bar(x.index, x.values, color='black')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)

                # Word Cloud
                st.title("Word Cloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots(figsize=(6, 6))
                plt.imshow(df_wc)
                st.pyplot(fig)

                # Most Common Words
                most_common_df = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots(figsize=(8, 4))

                ax.barh(most_common_df[0], most_common_df[1],color='black')
                plt.xticks(rotation='vertical')

                st.title('Most Common Words')
                st.pyplot(fig)

                # Emojis Used in the Chat
                emoji_df = helper.emojis_helper(selected_user, df)
                st.title("Emojis Used in the Chat")

                # Only top 10 emojis
                top_10_emoji_df = emoji_df.head(10)

                # Specify the path to your font file
                font_path = "NotoColorEmoji-Regular.ttf"

                # Register the font with Matplotlib
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()


                fig, ax = plt.subplots(figsize=(6, 6))  # Adjust the size as needed
                ax.pie(top_10_emoji_df[1], labels=top_10_emoji_df[0], autopct="%0.2f")
                st.pyplot(fig)

            # Removing the loader after the spinner disappears
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
