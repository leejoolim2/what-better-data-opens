"""Zonal statistics: WorldPop population and SRTM-derived slope by ADM2.
Chapter 10 uses slope_deg_srtm as the instrument; Chapters 3/5/11/13 use population.
Requires: rasterio, rasterstats, geopandas
Data:  WorldPop  https://hub.worldpop.org  (100 m, UN-adjusted, per country)
       SRTM 30 m https://earthexplorer.usgs.gov  or via Earth Engine 'USGS/SRTMGL1_003'
"""
import geopandas as gpd
from rasterstats import zonal_stats

adm2 = gpd.read_file("data/real/adm2_six_countries.gpkg")

pop = zonal_stats(adm2, "data/real/worldpop_khm_2020.tif", stats=["sum"], nodata=-99999)
adm2["population"] = [p["sum"] for p in pop]

slp = zonal_stats(adm2, "data/real/srtm_slope_khm.tif", stats=["mean"], nodata=-99999)
adm2["slope_deg_srtm"] = [s["mean"] for s in slp]

adm2.drop(columns="geometry").to_csv("data/real/adm2_covariates.csv", index=False)
