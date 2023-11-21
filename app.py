import streamlit as st
from awn_bot import AwnBot

__version__ = "0.0.4"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2023-11-21"
my_name = "awn-finder-bs"
my_emoji = "🏠"
GIT_REPO = "https://github.com/lcalmbach/awn-bot-bs"


APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    Datasource: <a href="https://data.bs.ch/">Open Data Basel-Stadt</a><br>
    <a href="{GIT_REPO}">git-repo</a>
    """


def init():
    st.set_page_config(
        layout="centered",
        initial_sidebar_state="auto",
        page_title=my_name,
        page_icon=my_emoji,
    )


def main():
    mode = "interactive"
    init()
    if "app" not in st.session_state:
        st.session_state.app = AwnBot(mode)

    st.session_state.app.show_ui()

    if mode != "bot":
        st.markdown("---")
        st.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
