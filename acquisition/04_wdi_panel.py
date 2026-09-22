"""World Bank WDI country panel — predictors for the synthetic control chapter.
Indicator codes match the column names in data/ch12_scm_cities.csv."""
import pandas as pd, requests

IND = {"EN_POP_DNST": "EN.POP.DNST",          # population density
       "NY_GDP_PCAP_CD": "NY.GDP.PCAP.CD",    # GDP per capita, current USD
       "SP_URB_TOTL_IN_ZS": "SP.URB.TOTL.IN.ZS"}
ISO = "KHM;VNM;UZB;KEN;USA;GBR"
URL = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?date=2000:2023&format=json&per_page=20000"

out = []
for col, ind in IND.items():
    js = requests.get(URL.format(iso=ISO, ind=ind), timeout=60).json()[1]
    out.append(pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]),
                              col: r["value"]} for r in js]))
df = out[0]
for extra in out[1:]:
    df = df.merge(extra, on=["iso3", "year"], how="outer")
df.sort_values(["iso3", "year"]).to_csv("data/real/wdi_panel.csv", index=False)
print(df.shape)
