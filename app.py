import streamlit as st
from awn_bot import AwnBot

__version__ = "0.0.2"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2023-11-18"
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
    st.set_page_config(  # Alternate names: setup_page, page, layout
        layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
        initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
        page_title=my_name,  # String or None. Strings get appended with "• Streamlit".
        page_icon=my_emoji,  # String, anything supported by st.image, or None.
    )


def main():
    init()
    if "app" not in st.session_state:
        st.session_state.app = AwnBot()

    st.session_state.app.show_ui()
    st.markdown("---")
    st.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()