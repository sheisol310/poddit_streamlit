import openai
import praw
import streamlit as st
import os

# Set up the app layout
st.set_page_config(page_title="Poddit", page_icon=":microphone:", layout="wide")

# Set GPT-3 API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]


# Define functions
def generate_script(content):
    """Generate a podcast script using OpenAI's GPT-3."""
    
    st.session_state.script = ''
    st.session_state.text_error = ""
    
    if not content:
        st.session_state.text_error = "Please copy and paste a post content."
        return
    
    with text_spinner_placeholder:
        with st.spinner("Please wait while your podcast script is being generated..."):
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Please write a podcast script based on the title and content: {content}. Remember to write "
                       f"it like dialogue. The script should read like a conversation between the characters. The "
                       f"response first mentions the title and then the podcast script.",
                temperature=0.9,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=["{}"],
            )
            
            st.session_state.text_error = ""
            res = response["choices"][0]["text"].strip().replace('"', "")
            st.session_state.script = res


def get_subreddit_content(category):
    """Get subreddit content using Praw."""
    
    reddit = praw.Reddit(
        client_id=st.secrets["REDDIT_CLIENT_ID"],
        client_secret=st.secrets["REDDIT_CLIENT_SECRET"],
        user_agent=st.secrets["REDDIT_USER_AGENT"]
    )
    
    subreddit = 'tifu'
    if category == 'Hot':
        return reddit.subreddit(subreddit).hot(limit=3)
    elif category == 'New':
        return reddit.subreddit(subreddit).new(limit=3)
    elif category == 'Rising':
        return reddit.subreddit(subreddit).rising(limit=3)
    elif category == 'Top':
        return reddit.subreddit(subreddit).top(limit=3)


# Sidebar
st.sidebar.title("Poddit - Generate Podcast Scripts from Reddit Posts")
st.sidebar.write(
    "Use Praw to get posts from subreddit 'Today I Fucked Up' and use OpenAI to generate a podcast script based on "
    "the post content.")

# Step 1
st.sidebar.write('---')
st.sidebar.header("Step 1: Select a category of TIFU subreddit")
category_options = ["Hot", "New", "Rising", "Top"]
category = st.sidebar.selectbox("Category", category_options)
get_posts_button = st.sidebar.button("Get Posts")

# Step 2
if get_posts_button:
    parse_articles = get_subreddit_content(category)
    st.sidebar.write('---')
    st.sidebar.header("Step 2: Pick a post and copy the content. (ctrl+a, ctrl+c) ")
    for index, submission in enumerate(parse_articles):
        if submission.selftext != '':
            text_value = f"Title: \n {submission.title} \n\n Content: \n {submission.selftext}"
            label_text = f"Post No.{index + 1}:"
            st.sidebar.text_area(label=f"**{label_text}**", value=text_value, height=200)
            st.sidebar.write('---')

# Main layout
if "script" not in st.session_state:
    st.session_state.script = ""
if "text_error" not in st.session_state:
    st.session_state.text_error = ""

# Force responsive layout for columns also on mobile
st.write(
    """<style>
    [data-testid="stHorizontalBlock"] {
        max-width: 100% !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    </style>""",
    unsafe_allow_html=True,
)

# Step 3
st.header("Step 3: Generate a podcast script")
st.write("Paste the copied content in the text area below and click 'Generate Script' to create a podcast script "
         "based on the post.")
post_content = st.text_area(label="Post Content", placeholder="Paste the copied content here", height=250)

col1, col2 = st.columns(2)
with col1:
    st.button(
        label="Generate Script",
        type="primary",
        on_click=generate_script,
        args=(post_content,),
    )

text_spinner_placeholder = st.empty()

if st.session_state.text_error:
    st.error(st.session_state.text_error)

if st.session_state.script:
    st.write('---')
    st.header("Step 4: Check and download the podcast script")
    st.write("If you are satisfied with the generated podcast script, you can clikc 'Download Script' it in the text "
             "area below. If not, you can click 'Regenerate Script' to try again with a different post.")
    podcast_script = st.text_area(label="Podcast Script", value=st.session_state.script, height=300)
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            label="Regenerate Script",
            type="primary",
            on_click=generate_script,
            args=(post_content,),
        )
    with col2:
        st.download_button(
            label="Download Script",
            data=podcast_script,
            file_name="podcast_script.txt",
            mime="text/plain",
        )
