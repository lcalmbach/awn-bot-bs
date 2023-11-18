import streamlit as st
import pandas as pd
from texts import texts
from const import ADR_FILE, APARTMENT_FILE
from tools import show_table


class AwnBot:
    def __init__(self):
        self.addresses = pd.read_parquet(ADR_FILE)
        self.apartments = pd.read_parquet(APARTMENT_FILE)
        self.streets = list(self.addresses['strname'].unique())
        self.streets.sort()

    def show_info(self):
        st.subheader("🔎AWN-Finder")
        with st.expander("Informationen zur App"):
            st.markdown(f"{texts['info']}")

    def show_ui(self):
        self.show_info()

        st.markdown('**Gib deine Adresse ein:**')
        cols = st.columns(2)
        with cols[0]:
            self.street = st.selectbox("Strasse", options=self.streets)
        housenumbers = self.addresses[self.addresses['strname'] == self.street]['deinr'].unique()
        housenumbers.sort()
        with cols[1]:
            self.housenumber = st.selectbox("Hausnummer", options=housenumbers)
        plz_options = self.addresses[(self.addresses['strname'] == self.street) & (self.addresses['deinr'] == self.housenumber) ]['dplz4'].unique()
        with cols[0]:
            self.plz = st.selectbox("Postleitzahl", options=plz_options)
        record = self.addresses[(self.addresses['strname'] == self.street) & (self.addresses['deinr'] == self.housenumber) ][['dplzname', 'egid']].drop_duplicates()
        self.ort = record.iloc[0]['dplzname']
        self.egid = record.iloc[0]['egid']
        with cols[1]:
            st.text_input("Ort:", value=self.ort, disabled=True)
        
        # st.markdown('**Gebäude**')
        # st.markdown(f'Egid: {self.egid}') 
        cols = st.columns(2)
        options_floors = self.apartments[self.apartments['egid'] == self.egid]['wstwk_decoded'].unique()
        options_floors.sort()
        with cols[0]:
            self.floor = st.selectbox("Stockwerk", options=options_floors)
        st.markdown('Wähle deine Wohnung aus, bei mehreren Wohnungen achte auf die Zimmerzahl oder Grösse):')
        df = self.apartments[(self.apartments['egid'] == self.egid) & (self.apartments['wstwk_decoded'] == self.floor)]
        
        fields = ['egid', 'whgnr', 'wstwk_decoded', 'wbez', 'warea', 'wazim']
        df = df[fields]
        df = df.sort_values('wstwk_decoded')
        df.columns = ['EGID', 'AWN', 'Stockwerk', 'Info', 'Fläche', 'Anz. Zimmer']
        settings = {"height": 200}
        response = show_table(df, [], settings)
        if response:
            st.subheader(f"Deine Wohnungsnummer: {response['AWN']}")


            

