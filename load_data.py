import pandas as pd
import requests
import io

PROXY_DICT = {"https": "http://dpdstatasvsql05:dpdstatasvsql05_@proxy1.bs.ch:3128"}
ADR_FILE = "data/entries.parquet"
APARTMENT_FILE = "data/apartments.parquet"
URL_TEMPLATE = (
    "https://data.bs.ch/api/explore/v2.1/catalog/datasets/{}/exports/csv?"
    "lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%3B&select={}"
)

print("Downloading apartments")
fields = ",".join(
    [
        "egid",
        "edid",
        "ewid",
        "whgnr",
        "weinr",
        "wstwk_decoded",
        "wbez",
        "wbauj",
        "warea",
        "wazim",
    ]
)
url_apartments = URL_TEMPLATE.format(100232, fields)

r = requests.get(url_apartments, proxies=PROXY_DICT).text

# apa_df = pd.read_csv(io.StringIO(r), sep=";")
apa_df = pd.read_csv(url_apartments, sep=";")
apa_df.to_parquet(
    APARTMENT_FILE,
)
egid_wohnungen = apa_df["egid"].unique()

print("Downloading adresses")
fields = ",".join(
    ["egid", "edid", "strname", "deinr", "dplz4", "dplzname", "eingang_koordinaten", "doffadr"]
)
url_entries = URL_TEMPLATE.format(100231, fields)
adr_df = pd.read_csv(url_entries, sep=";")
adr_df = adr_df[adr_df["egid"].isin(egid_wohnungen)]
# Nur offizielle Adressen
adr_df[["latitude", "longitude"]] = adr_df["eingang_koordinaten"].str.split(
    ",", expand=True
)
adr_df["latitude"] = adr_df["latitude"].astype(float)
adr_df["longitude"] = adr_df["longitude"].astype(float)
adr_df.to_parquet(ADR_FILE, engine="pyarrow")

print("Download completed")

# print(adr_df.head())
# streets = adr_df['strname'].unique()
# streets.sort()
# print(streets)
