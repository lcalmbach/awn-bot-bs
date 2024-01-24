import streamlit as st
import pandas as pd
import time
import json
from texts import texts
from const import (
    ADR_FILE,
    APARTMENT_FILE,
    assistant_responses,
)
from tools import show_table
from enum import Enum
import folium
from streamlit_folium import folium_static


class Mode(Enum):
    SINGLE=0
    MULTIPLE=1

class AwnBot:
    def __init__(self):
        self.mode = Mode.SINGLE.value
        self.addresses = pd.read_parquet(ADR_FILE)
        self.apartments = pd.read_parquet(APARTMENT_FILE)
        self.streets = list(self.addresses["strname"].unique())
        self.locations = list(self.addresses["dplzname"].unique())
        self.streets.sort()
        self.appartments_df = pd.DataFrame()
        self.egid = 0
        

    def show_info(self):
        with st.expander("Informationen zur App"):
            if self.mode == Mode.SINGLE.value:
                st.markdown(f"{texts['info']}")
            else:
                st.markdown(f"{texts['info_multiple']}")
        
    def show_map(self, df):
        """
        Display a map with markers for each location in the given DataFrame.

        Parameters:
        - df (pandas.DataFrame): The DataFrame containing location data with latitude and longitude columns.

        Returns:
        None
        """
        map_center = [df["latitude"].mean(), df["longitude"].mean()]
        map = folium.Map(location=map_center, zoom_start=18)
        tool_tip = f'''{self.street} {self.housenumber}\n
    {self.plz} {self.location}\n\n EGID: {self.egid}'''
        for index, row in df.iterrows():
            folium.Marker(
                [row["latitude"], row["longitude"]],
                popup=tool_tip,
            ).add_to(map)
        folium_static(map)
       
    def show_multiple_mode(self):
        def get_appartments(egid: int):
            df = self.apartments[self.apartments["egid"] == egid]
            df = df[["egid", "whgnr", "wstwk_decoded", "wbez", "warea", "wazim", "ewid"]]
            df.columns = [
                "EGID",
                "AWN",
                "Stockwerk",
                "Info",
                "Fläche",
                "Anz. Zimmer",
                "EWID",
            ]
            df['Adresse'] = self.street + ' ' + self.housenumber + ', ' + self.plz + ' ' + self.location
            cols = df.columns.tolist()
            cols = [cols[-1]] + cols[:-1]
            df = df[cols]
            return df

        st.markdown("Suche Adressen und drücke Schaltfläche `Adresse hinzufügen`")
        self.egid = 0
        cols = st.columns(2)
        with cols[0]:
            options_streets = ["<Wähle eine Strasse>"] + self.streets
            self.street = st.selectbox("Strasse", options=options_streets)
        with cols[1]:
            if options_streets.index(self.street) == 0:
                housenumbers = self.addresses["deinr"].unique()
            else:
                housenumbers = self.addresses[self.addresses["strname"] == self.street][
                    "deinr"
                ].unique()
            housenumbers = [x for x in housenumbers if x is not None]
            housenumbers.sort()

            hrn_options = ["<Wähle eine Hausnummer>"] + housenumbers
            self.housenumber = st.selectbox(
                "Hausnummer",
                options=hrn_options,
                disabled=self.street == "<Wähle eine Strasse>",
            )

        with cols[0]:
            if hrn_options.index(self.housenumber) == 0:
                plz_options = self.addresses["dplz4"].unique().sort()
                plz_options = ["Wähle eine Postleitzahl"] + [plz_options]
            else:
                plz_options = self.addresses[
                    (self.addresses["strname"] == self.street)
                    & (self.addresses["deinr"] == self.housenumber)
                ]["dplz4"].unique()
                plz_options = [str(x) for x in plz_options if x is not None]
            self.plz = st.selectbox("Postleitzahl", options=plz_options)
        record = self.addresses[
            (self.addresses["strname"] == self.street)
            & (self.addresses["deinr"] == self.housenumber)
        ][["dplzname", "egid", "latitude", "longitude"]].drop_duplicates()

        with cols[1]:
            if self.plz == "Wähle eine Postleitzahl":
                ort_options = list(self.addresses["dplzname"])
                ort_options.sort()
            else:
                ort_options = record["dplzname"]
                self.egid = record.iloc[0]["egid"]
            self.location = st.selectbox("Ort:", ort_options, disabled=True)
        if self.egid > 0:
            self.show_map(record)
        cols = st.columns(2)
        if st.button('Adresse hinzufügen', disabled=self.egid == 0):
            self.appartments_df = pd.concat([self.appartments_df, get_appartments(self.egid)])
        if len(self.appartments_df) > 0:
            show_table(self.appartments_df, {})
            st.download_button(
                label="Wohnungen herunterladen",
                data=self.appartments_df.to_csv(sep=';').encode('utf-8'),
                file_name="wohnungen.csv",
                mime="text/csv",
            )
    
    def show_single_mode(self):
        self.show_info()
        st.markdown("**Gib bitte deine Adresse ein:**")
        self.egid = 0
        cols = st.columns(2)
        with cols[0]:
            options_streets = ["<Wähle eine Strasse>"] + self.streets
            self.street = st.selectbox("Strasse", options=options_streets)
        with cols[1]:
            if options_streets.index(self.street) == 0:
                housenumbers = self.addresses["deinr"].unique()
            else:
                housenumbers = self.addresses[self.addresses["strname"] == self.street][
                    "deinr"
                ].unique()
            housenumbers = [x for x in housenumbers if x is not None]
            housenumbers.sort()

            hrn_options = ["<Wähle eine Hausnummer>"] + housenumbers
            self.housenumber = st.selectbox(
                "Hausnummer",
                options=hrn_options,
                disabled=self.street == "<Wähle eine Strasse>",
            )

        with cols[0]:
            if hrn_options.index(self.housenumber) == 0:
                plz_options = self.addresses["dplz4"].unique().sort()
                plz_options = ["Wähle eine Postleitzahl"] + [plz_options]
            else:
                plz_options = self.addresses[
                    (self.addresses["strname"] == self.street)
                    & (self.addresses["deinr"] == self.housenumber)
                ]["dplz4"].unique()
                plz_options = [str(x) for x in plz_options if x is not None]
            self.plz = st.selectbox("Postleitzahl", options=plz_options)
        record = self.addresses[
            (self.addresses["strname"] == self.street)
            & (self.addresses["deinr"] == self.housenumber)
        ][["dplzname", "egid", "latitude", "longitude"]].drop_duplicates()

        with cols[1]:
            if self.plz == "Wähle eine Postleitzahl":
                ort_options = list(self.addresses["dplzname"])
                ort_options.sort()
            else:
                ort_options = record["dplzname"]
                self.egid = record.iloc[0]["egid"]
            self.location = st.selectbox("Ort:", ort_options, disabled=True)
        if self.egid > 0:
            self.show_map(record)
        # st.markdown('**Gebäude**')
        # st.markdown(f'Egid: {self.egid}')
        cols = st.columns(2)
        options_floors = self.apartments[self.apartments["egid"] == self.egid][
            "wstwk_decoded"
        ].unique()
        options_floors.sort()
        with cols[0]:
            self.floor = st.selectbox("Stockwerk", options=options_floors)
        contact_email = "vitus.thali@bs.ch"
        contact = "Vitus Thali"
        st.markdown(    
            f'Wähle deine Wohnung aus. Bei mehreren Wohnungen auf dem gleichen Stockwerk kannst kannst die Zimmerzahl oder Grösse der Wohnung verwenden, um deine Wohnng zu erkennen. Bist du unsicher, dann wende dich bitte an <a href="mailto:{contact_email}">{contact}</a> (Statistisches Amt Basel Stadt).',
            unsafe_allow_html=True,
        )
        df = self.apartments[
            (self.apartments["egid"] == self.egid)
            & (self.apartments["wstwk_decoded"] == self.floor)
        ]
        fields = ["egid", "whgnr", "wstwk_decoded", "wbez", "warea", "wazim", "ewid"]
        df = df[fields]
        df = df.sort_values("wstwk_decoded")
        df.columns = [
            "EGID",
            "AWN",
            "Stockwerk",
            "Info",
            "Fläche",
            "Anz. Zimmer",
            "EWID",
        ]
        settings = {"height": 200}
        response = show_table(df, [], settings)
        if response:
            st.subheader(f"Deine Wohnungsnummer: {response['AWN']}")

    def address_text(self):
        return f'{self.args["street"]} {self.args["housenumber"]}, {self.args["plz"]} {self.args["location"]} (EGID Gebäude: {self.args["egid"]})'

    
    def get_floors(self):
        return self.apartments[self.apartments["egid"] == self.args["egid"]][
            "wstwk_decoded"
        ].unique()
    
    def get_apartments_on_floor(self):
        apartments_on_floor = self.apartments[
            (self.apartments["egid"] == self.args["egid"]) &
            (self.apartments["wstwk_decoded"] == self.args["floor"])
        ]
        return apartments_on_floor

    def get_records(self):
        addresses = self.addresses
        apartments = self.apartments
        # st.write(self.args)
        if self.args["street"] > "":
            addresses = addresses[
                (addresses["strname"] == self.args['street'])
            ]
        if self.args["housenumber"] > "":
            addresses = addresses[
                (addresses["deinr"] == self.args['housenumber'])
            ]
        if self.args["plz"] != "":
            addresses = addresses[
                (addresses["dplz4"] == self.args['plz'])
            ]
        if (len(addresses) > 0) & (self.args["location"] > ""):
            addresses = addresses[
                (addresses["dplzname"] == self.args['plz'])
            ]
        if len(addresses) == 1:
            self.args['egid'] = addresses.iloc[0]['egid']

        if self.args["egid"] != "":
            apartments = apartments[apartments["egid"] == self.args["egid"]]
            if self.args["floor"] > "":
                addresses = addresses[
                    (addresses["egid"] == self.egid)
                ]
        return addresses, apartments

    def get_address(self):
        return f'{self.args["street"]} {self.args["housenumber"]}, {self.args["plz"]} {self.args["location"]} (EGID Gebäude: {self.args["egid"]})'
    
    def format_response(self, response):
        includes = []
        for include in assistant_responses[self.status.name]['includes']:
            if include == 'adrs':
                includes.append(self.get_address())
            if include == 'floors':
                includes.append(self.get_floors())
        if includes:
            response = response.format(*includes)
        return response
                
    
    def show_ui(self):
        st.subheader("🔎AWN-Finder")
        self.mode=st.radio("Modus", ["Einzelne Wohnung", "Mehrere Gebäude"])
        if self.mode == "Einzelne Wohnung":
            self.show_single_mode()
        else:
            self.show_multiple_mode()
        
