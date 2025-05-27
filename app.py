import streamlit as st
import json
from awn_finder import AwnFinder
from lang import get_used_languages, init_lang_dict_complete, get_lang

__version__ = "0.0.21"
__author__ = "Lukas Calmbach"
__author_email__ = "lukas.calmbach@bs.ch"
VERSION_DATE = "2025-05-27"
my_name = "awn-finder-bs"
my_emoji = "🏠"
GIT_REPO = "https://github.com/lcalmbach/awn-bot-bs"
PAGE = "app"
SETTINGS_FILE = "settings.json"


def display_language_selection():
    """
    The display_info function displays information about the application. It
    uses the st.expander container to create an expandable section for the
    information. Inside the expander, displays the input and output format.
    """
    index = list(st.session_state["used_languages_dict"].keys()).index(
        st.session_state["lang"]
    )
    sel_lang = st.selectbox(
        label=f'🌐{lang["language"]}',
        options=st.session_state["used_languages_dict"].keys(),
        format_func=lambda x: st.session_state["used_languages_dict"][x],
        index=index,
    )

    if sel_lang != st.session_state["lang"]:
        st.session_state["lang"] = sel_lang
        st.rerun()


def get_impressum():
    created_by = lang["created_by"]
    version = lang["version"]
    translation = lang["translation"]
    data_source = lang["data_source"]
    last_data_sync = lang["last_data_sync"]
    text = f"""<div style='background-color:powderblue; padding: 10px;border-radius: 15px;'>
        <small>{created_by}: <a href='mailto:informatik.stata@bs.ch'>Statistisches Amt Basel-Stadt</a><br>
        {version}: {__version__} ({VERSION_DATE})<br>
        {data_source}: <a href='https://data.bs.ch/'>Datenportal Basel-Stadt</a><br>
        {last_data_sync}: {st.session_state['last_update']}<br>
        {translation}: <a href='https://data-alchemy-toolbox.streamlit.app/'>DataAlchemy Toolbox</a><br>
        <a href='{GIT_REPO}'>git-repo</a>
        """
    return text

    
def init():
    global lang

    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title=my_name,
        page_icon=my_emoji,
    )

    if not ("lang" in st.session_state):
        init_lang_dict_complete("./lang/")
        # first item is default language
        st.session_state["used_languages_dict"] = get_used_languages(
            st.session_state["lang_dict"][PAGE]
        )
        st.session_state["lang"] = next(
            iter(st.session_state["used_languages_dict"].items())
        )[0]
        st.session_state.app = AwnFinder()

        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            st.session_state['last_update'] = settings['last_update']
    

def show_footer():
    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(get_impressum(), unsafe_allow_html=True)
    with cols[1]:
        display_language_selection()


def main():
    global lang
    init()
    lang = get_lang(PAGE)
    st.session_state.app.show_ui()
    show_footer()


if __name__ == "__main__":
    main()
