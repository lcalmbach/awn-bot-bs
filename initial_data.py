import pandas as pd
from const import ADR_FILE, APARTMENT_FILE

URL_TEMPLATE = (
    "https://data.bs.ch/api/explore/v2.1/catalog/datasets/{}/exports/csv?"
    "lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%3B&select={}"
)

print("Downloading adresses")
fields = ','.join(['egid', 'strname', 'deinr', 'dplz4', 'dplzname'])
url_entries = URL_TEMPLATE.format(100231, fields)
adr_df = pd.read_csv(url_entries, sep=';')
adr_df.to_parquet(ADR_FILE, engine='pyarrow')

print("Downloading apartments")
fields = ','.join(['egid', 'ewid', 'whgnr', 'weinr', 'wstwk_decoded', 'wbez', 'wbauj', 'warea', 'wazim'])
url_apartments = URL_TEMPLATE.format(100232, fields)
apa_df = pd.read_csv(url_apartments, sep=';')
apa_df.to_parquet(APARTMENT_FILE, )

# print(adr_df.head())
# streets = adr_df['strname'].unique()
# streets.sort()
# print(streets)
