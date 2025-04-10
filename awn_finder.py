import streamlit as st
import pandas as pd
from tools import show_table
from enum import Enum
import folium
import re
from streamlit_folium import folium_static

from lang import get_lang


contact = "AWN Team"
contact_email = "awn@bs.ch"
ADR_FILE = "data/entries.parquet"
APARTMENT_FILE = "data/apartments.parquet"
STREETS_FILE = "data/streets.parquet"

def lang(text):
    """
    Returns the translated text of the given text.
    It passes the PAGE variable holding the key to the current module

    Args:
        text (str): The text to determine the language of.

    Returns:
        str: translated text.
    """
    return get_lang(__name__)[text]


mode_options = []


class Mode(Enum):
    SINGLE = 0
    MULTIPLE = 1


class AwnFinder:
    def __init__(self):
        self.mode = Mode.SINGLE.value
        self.housenumber = None
        self.args = {}
        self.addresses = pd.read_parquet(ADR_FILE)
        self.apartments = pd.read_parquet(APARTMENT_FILE)
        self.streets = list(self.addresses["strname"].unique())
        self.apartments = self.add_address_to_apartment()
        self.eingaenge = []
        self.locations = list(self.addresses["dplzname"].unique())
        self.streets.sort()
        self.apartment_df = pd.DataFrame()
        self.egid = 0 # GWR Gebäudecode
        self.edid = 0 # Eingangsnummer
        self.buildings_df = pd.DataFrame()
        
    def add_address_to_apartment(self):
        # links then self.apartments and self.addresses dataframes using the egid and edid columns and adds the columns housenumber, plzname, location to the self.apartments dataframe
        merged_apartments = merged_apartments = pd.merge(
            self.apartments,
            self.addresses[['egid', 'edid', 'deinr', 'strname', 'dplz4', 'dplzname']],
            on=['egid', 'edid'],
            how='left'
        )
        merged_apartments = merged_apartments.rename(columns={'deinr': 'housenumber', 'dplz4': 'plz', 'dplzname': 'location'})
        return merged_apartments
    
    def sort_house_numbers(self, housenumbers: list) -> list:
        def extract_parts(s):
            parts = re.split("([0-9]+)", s)
            return (
                int(parts[1]) if parts[1].isdigit() else parts[1],
                int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else parts[2],
            )

        [x for x in housenumbers if x is not None]
        sorted_numbers = sorted(housenumbers, key=extract_parts)
        return sorted_numbers

    def show_info(self):
        """
        Displays information about the app based on the selected mode.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """
        with st.expander(lang("app_information")):
            if mode_options.index(self.mode) == Mode.SINGLE.value:
                st.markdown(lang("info_single"))
            else:
                st.markdown(lang("info_multiple"))

    def show_map(self, df):
        """
        Displays a map with markers for each location in the given DataFrame.

        Parameters:
        - df (pandas.DataFrame): The DataFrame containing location data with latitude and longitude columns.

        Returns:
        None
        """
        map_center = [df["latitude"].mean(), df["longitude"].mean()]
        map = folium.Map(location=map_center, zoom_start=18)
        tool_tip = f"""{self.street} {self.housenumber}\n
    {self.plz} {self.location}\n\n EGID: {self.egid}"""
        for _, row in df.iterrows():
            folium.Marker(
                [row["latitude"], row["longitude"]],
                popup=tool_tip,
            ).add_to(map)
        folium_static(map)

    def show_multiple_mode(self):
        def get_apartment(egid: int, eingaenge: list):
            mask = self.apartments["egid"] == egid
            if len(eingaenge) > 0:
                mask &= self.apartments["edid"].isin(eingaenge)
            column_mapping = {
                "egid": "EGID",
                "whgnr": "AWN",
                "wstwk_decoded": "Stockwerk",
                "wbez": "Info",
                "warea": "Fläche",
                "wazim": "Anz. Zimmer",
                "ewid": "EWID",
                "strname": "Strasse",
                "housenumber": "Nr"
            }

            # Ziel-Spaltenreihenfolge inkl. Adresse
            final_columns = [
                "Adresse",
                "EGID",
                "AWN",
                "Stockwerk",
                "Info",
                "Fläche",
                "Anz. Zimmer",
                "EWID"
            ]
            df = (
                self.apartments
                .loc[mask, column_mapping.keys()]
                .drop_duplicates()
                .rename(columns=column_mapping)
                .assign(
                    Adresse=lambda d: d["Strasse"].fillna("").astype(str) + " " + d["Nr"].fillna("").astype(str)
                )[final_columns]
            )
            return df
    

        self.show_info()
        st.markdown(f'**{lang("add_address_button_label")}:**')
        self.egid = 0
        cols = st.columns(2)
        with cols[0]:
            street_placeholder = st.empty()
            options_streets = [f'<{lang("select_street")}>'] + self.streets
            self.street = street_placeholder.selectbox(
                lang("street"),
                options=options_streets
            )
        with cols[1]:
            hnr_placeholder = st.empty()
            if options_streets.index(self.street) == 0:
                housenumbers = self.addresses["deinr"].unique()
            else:
                housenumbers = self.addresses[self.addresses["strname"] == self.street][
                    "deinr"
                ].unique()
            housenumbers = self.sort_house_numbers(housenumbers)

            hrn_options = [f'<{lang("select_house_number")}>'] + housenumbers
            self.housenumber = hnr_placeholder.selectbox(
                lang("house_number"),
                options=hrn_options,
                disabled=self.street == f'<{lang("select_street")}>',
            )
            if self.housenumber != f'<{lang("select_house_number")}>':
                matching_rows = self.addresses[
                    (self.addresses["strname"] == self.street) &
                    (self.addresses["deinr"] == self.housenumber)
                ]

                if not matching_rows.empty:
                    self.egid = matching_rows.iloc[0]['egid']
                else:
                    self.egid = None  # oder raise ValueError("No matching address found.")
                eingaenge = self.addresses[self.addresses['egid']==self.egid]
                if len(eingaenge) > 1:
                    eingange_options = dict(zip(eingaenge['edid'], eingaenge['strname'] + ' ' + eingaenge['deinr']))
                    self.eingaenge = st.multiselect(
                        lang("entrances"),
                        options=list(eingange_options.keys()),
                        format_func=lambda x: eingange_options[x],
                        help=lang("help_entrances")
                    )
                else:
                    self.eingaenge = []
                    
        # if self.housenumber != f'<{lang("select_house_number")}>':
        with cols[0]:
            po_placeholder = st.empty()
            if hrn_options.index(self.housenumber) == 0:
                plz_options = self.addresses["dplz4"].unique().sort()
                plz_options = [f'<{lang("select_postal_code")}>'] + [plz_options]
            else:
                plz_options = self.addresses[
                    (self.addresses["strname"] == self.street)
                    & (self.addresses["deinr"] == self.housenumber)
                ]["dplz4"].unique()
                plz_options = [str(x) for x in plz_options if x is not None]
            
            
            self.plz = po_placeholder.selectbox(
                lang("postal_code"),
                options=plz_options,
                disabled=self.housenumber == f'<{lang("select_house_number")}>'
            )
        mask = self.addresses["egid"] == self.egid
        if len(self.eingaenge) > 0:
            mask &= self.addresses["edid"].isin(self.eingaenge)
        record = (
            self.addresses.loc[mask, ["dplzname", "egid", "edid", "latitude", "longitude"]]
            .drop_duplicates()
        )

        with cols[1]:
            location_placeholder = st.empty()
            if self.plz == f'<{lang("select_postal_code")}>':
                ort_options = list(self.addresses["dplzname"])
                ort_options.sort()
            else:
                ort_options = record["dplzname"]
                self.egid = record.iloc[0]["egid"]
                self.edid = record.iloc[0]["edid"]
            self.location = location_placeholder.selectbox(
                label=f'{lang("location")}:',
                options = ort_options,
                disabled=len(ort_options) > 1
            )

        if st.button(lang("add_address"), disabled=self.egid == 0):
            self.apartment_df = pd.concat([self.apartment_df, get_apartment(self.egid, self.eingaenge)])
        cols = st.columns(2)
        with cols[0]:
            if len(self.apartment_df) > 0:
                st.download_button(
                    label=lang("download_appartments"),
                    data=self.apartment_df.to_csv(sep=";").encode("utf-8"),
                    file_name="wohnungen.csv",
                    mime="text/csv",
                )
                self.buildings_df = pd.concat([self.buildings_df, record])

        if len(self.apartment_df) > 0:
            with cols[1]:
                if st.button(lang("reset_input")):
                    self.buildings_df = pd.DataFrame()
                    self.apartment_df = pd.DataFrame()
                    self.street = street_placeholder.selectbox(
                        lang("street"),
                        options=options_streets,
                        index=0,
                        key='xxx'
                    )
                    self.housenumber = hnr_placeholder.selectbox(
                        lang("house_number"),
                        options=hrn_options,
                        index = 0,
                        disabled=True,
                        key='xx1'
                    )
                    self.plz = po_placeholder.selectbox(
                        lang("postal_code"),
                        options=[f'<{lang("select_postal_code")}>'],
                        index=0,
                        disabled=True,
                        key='xx2'
                    )
                    self.location = location_placeholder.selectbox(
                        f'{lang("location")}:',
                        options=['Basel'],
                        index=0,
                        disabled=True,
                        key='xx3'
                    )

        if len(self.apartment_df) > 0:
            show_table(self.apartment_df, {})
            self.show_map(self.buildings_df)

    def show_single_mode(self):
        self.show_info()
        st.markdown(f'**{lang("enter_address")}:**')
        self.egid = 0
        cols = st.columns(2)
        with cols[0]:
            options_streets = [f'<{lang("select_street")}>'] + self.streets
            self.street = st.selectbox(lang("street"), options=options_streets)
        with cols[1]:
            if options_streets.index(self.street) == 0:
                housenumbers = self.addresses["deinr"].unique()
            else:
                housenumbers = self.addresses[self.addresses["strname"] == self.street][
                    "deinr"
                ].unique()
            housenumbers = [x for x in housenumbers if x is not None]
            housenumbers = self.sort_house_numbers(housenumbers)

            hrn_options = [f'<{lang("select_house_number")}>'] + housenumbers
            self.housenumber = st.selectbox(
                lang("house_number"),
                options=hrn_options,
                disabled=self.street == f'<{lang("select_street")}>',
            )

        with cols[0]:
            if hrn_options.index(self.housenumber) == 0:
                plz_options = self.addresses["dplz4"].unique().sort()
                plz_options = [lang("select_postal_code")] + [plz_options]
            else:
                plz_options = self.addresses[
                    (self.addresses["strname"] == self.street)
                    & (self.addresses["deinr"] == self.housenumber)
                ]["dplz4"].unique()
                plz_options = [str(x) for x in plz_options if x is not None]
            self.plz = st.selectbox(lang("postal_code"), options=plz_options)
        record = self.addresses[
            (self.addresses["strname"] == self.street)
            & (self.addresses["deinr"] == self.housenumber)
        ][["dplzname", "egid", "latitude", "longitude"]].drop_duplicates()

        with cols[1]:
            if self.plz == lang("select_postal_code"):
                ort_options = list(self.addresses["dplzname"])
                ort_options.sort()
            else:
                ort_options = record["dplzname"]
                self.egid = record.iloc[0]["egid"]
            self.location = st.selectbox(
                f'{lang("location")}', ort_options, disabled=True
            )

        cols = st.columns(2)
        options_floors = self.apartments[self.apartments["egid"] == self.egid][
            "wstwk_decoded"
        ].unique()
        if len(options_floors) > 0:
            options_floors.sort()
            with cols[0]:
                self.floor = st.selectbox(lang("floor"), options=options_floors)
        else:
            self.floor = False
        if self.floor:
            st.markdown(
                lang("select_apartment_with_explenation").format(
                    contact_email
                ),
                unsafe_allow_html=True,
            )
            df = self.apartments[
                (self.apartments["egid"] == self.egid)
                & (self.apartments["housenumber"] == self.housenumber)
                & (self.apartments["wstwk_decoded"] == self.floor)
            ]
            fields = [
                "egid",
                "whgnr",
                "strname",
                "housenumber",
                "location",
                "wstwk_decoded",
                "wbez",
                "warea",
                "wazim",
                "ewid",
            ]
            df = df[fields]
            df = df.sort_values("wstwk_decoded")
            df.columns = [
                "EGID",
                "AWN",
                "Strasse",
                "Hausnummer",
                "Ort",
                "Stockwerk",
                "Info",
                "Fläche",
                "Anz. Zimmer",
                "EWID",
            ]
            settings = {"height": 200}
            response = show_table(df, [], settings)
            if response:
                st.subheader(f"{lang('your_awn')}: {response['AWN']}")
            self.show_map(record)

    def address_text(self):
        return f"{self.args['street']} {self.args['housenumber']}, {self.args['plz']} {self.args['location']} ({lang['egid_building']}: {self.args['egid']})"

    def get_floors(self):
        return self.apartments[self.apartments["egid"] == self.args["egid"]][
            "wstwk_decoded"
        ].unique()

    def get_apartments_on_floor(self):
        apartments_on_floor = self.apartments[
            (self.apartments["egid"] == self.args["egid"])
            & (self.apartments["wstwk_decoded"] == self.args["floor"])
        ]
        return apartments_on_floor

    def get_records(self):
        addresses = self.addresses
        apartments = self.apartments
        if self.args["street"] > "":
            addresses = addresses[(addresses["strname"] == self.args["street"])]
        if self.args["housenumber"] > "":
            addresses = addresses[(addresses["deinr"] == self.args["housenumber"])]
        if self.args["plz"] != "":
            addresses = addresses[(addresses["dplz4"] == self.args["plz"])]
        if (len(addresses) > 0) & (self.args["location"] > ""):
            addresses = addresses[(addresses["dplzname"] == self.args["plz"])]
        if len(addresses) == 1:
            self.args["egid"] = addresses.iloc[0]["egid"]

        if self.args["egid"] != "":
            apartments = apartments[apartments["egid"] == self.args["egid"]]
            if self.args["floor"] > "":
                addresses = addresses[(addresses["egid"] == self.egid)]
        return addresses, apartments

    def get_address(self):
        return f"{self.args['street']} {self.args['housenumber']}, {self.args['plz']} {self.args['location']} (EGID Gebäude: {self.args['egid']})"

    def format_response(self, response):
        includes = []
        for include in [self.status.name]["includes"]:
            if include == "adrs":
                includes.append(self.get_address())
            if include == "floors":
                includes.append(self.get_floors())
        if includes:
            response = response.format(*includes)
        return response

    def show_ui(self):
        global mode_options

        mode_options = lang("mode_options")
        st.subheader("🔎AWN-Finder")

        self.mode = st.radio(lang("mode"), mode_options)
        if mode_options.index(self.mode) == 0:
            self.show_single_mode()
        else:
            self.housenumber = None
            self.show_multiple_mode()
