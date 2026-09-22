"""Download ADM2 boundaries for the six study countries (geoBoundaries API).
Produces the frame that every other file joins to via shapeID."""
import requests, geopandas as gpd, pandas as pd

ISO3 = ["KHM", "VNM", "UZB", "KEN", "USA", "GBR"]
API = "https://www.geoboundaries.org/api/current/gbOpen/{iso}/ADM2/"

frames = []
for iso in ISO3:
    meta = requests.get(API.format(iso=iso), timeout=60).json()
    gdf = gpd.read_file(meta["gjDownloadURL"])
    gdf["shapeGroup"] = iso
    frames.append(gdf[["shapeID", "shapeName", "shapeGroup", "geometry"]])
    print(f"{iso}: {len(gdf)} ADM2 units")

out = pd.concat(frames, ignore_index=True)
gpd.GeoDataFrame(out, crs="EPSG:4326").to_file("data/real/adm2_six_countries.gpkg", driver="GPKG")
