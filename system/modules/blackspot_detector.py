# from geopy.geocoders import Nominatim
# import pandas as pd

# geolocator = Nominatim(user_agent="traffic_ai")

# def get_location(lat, lon):
#     try:
#         location = geolocator.reverse((lat, lon), timeout=10)
#         return location.address
#     except:
#         return "Unknown"

# def detect_blackspots(file):

#     df = pd.read_csv(file)
#     df = df[(df["LATITUDE"] != 0) & (df["LONGITUDE"] != 0)]

#     grouped = (
#         df.groupby(["LATITUDE","LONGITUDE"])
#         .size()
#         .reset_index(name="Accident_Count")
#         .sort_values("Accident_Count", ascending=False)
#         .head(10)
#     )

#     # convert coordinates → place name
#     grouped["Location_Name"] = grouped.apply(
#         lambda x: get_location(x["LATITUDE"], x["LONGITUDE"]), axis=1
#     )

#     return grouped

from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import folium

import os
import pandas as pd
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="traffic_ai")

CACHE_FILE = "data/location_cache.csv"

# load cache if exists
if os.path.exists(CACHE_FILE):
    location_cache = pd.read_csv(CACHE_FILE)
else:
    location_cache = pd.DataFrame(columns=["lat","lon","location"])


def get_location(lat, lon):

    global location_cache

    # check cache first
    cached = location_cache[
        (location_cache["lat"] == lat) &
        (location_cache["lon"] == lon)
    ]

    if not cached.empty:
        return cached.iloc[0]["location"]

    # if not cached → call API
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        address = location.address
    except:
        address = "Unknown"

    # save to cache
    new_row = pd.DataFrame([[lat, lon, address]],
                           columns=["lat","lon","location"])

    location_cache = pd.concat([location_cache, new_row], ignore_index=True)

    location_cache.to_csv(CACHE_FILE, index=False)

    return address
# ------------------------------------------------
# BLACKSPOT DETECTION USING DBSCAN
# ------------------------------------------------
def detect_blackspots(file):

    df = pd.read_csv(file)

    df = df[(df["LATITUDE"] != 0) & (df["LONGITUDE"] != 0)]
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

    coords = df[["LATITUDE", "LONGITUDE"]].values

    db = DBSCAN(eps=0.003, min_samples=5)
    clusters = db.fit_predict(coords)

    df["cluster"] = clusters

    df = df[df["cluster"] != -1]

    grouped = (
        df.groupby("cluster")
        .agg({
            "LATITUDE": "mean",
            "LONGITUDE": "mean",
            "cluster": "size"
        })
        .rename(columns={"cluster": "Accident_Count"})
        .reset_index(drop=True)
    )

    # -----------------------------
    # RISK LEVEL CLASSIFICATION
    # -----------------------------
    def risk_level(count):

        if count >= 30:
            return "HIGH RISK"
        elif count >= 15:
            return "MEDIUM RISK"
        else:
            return "LOW RISK"

    grouped["Risk_Level"] = grouped["Accident_Count"].apply(risk_level)

    return grouped


# ------------------------------------------------
# BLACKSPOT MAP
# ------------------------------------------------
def generate_blackspot_map(file):

    blackspots = detect_blackspots(file)

    blackspot_map = folium.Map(
        location=[40.7128, -74.0060],
        zoom_start=11
    )

    for _, row in blackspots.iterrows():

        if row["Risk_Level"] == "HIGH RISK":
            color = "red"
        elif row["Risk_Level"] == "MEDIUM RISK":
            color = "orange"
        else:
            color = "green"

        folium.CircleMarker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=f"""
            <b>Blackspot Cluster</b><br>
            Accidents: {row['Accident_Count']}<br>
            Risk Level: {row['Risk_Level']}<br>
            Lat: {row['LATITUDE']}<br>
            Lon: {row['LONGITUDE']}
            """
        ).add_to(blackspot_map)

    return blackspot_map


# from geopy.geocoders import Nominatim
# import pandas as pd
# import numpy as np
# from sklearn.cluster import DBSCAN
# import folium

# geolocator = Nominatim(user_agent="traffic_ai")


# # ------------------------------------------------
# # GET LOCATION NAME FROM COORDINATES
# # ------------------------------------------------
# def get_location(lat, lon):
#     try:
#         location = geolocator.reverse((lat, lon), timeout=10)
#         return location.address
#     except:
#         return "Unknown"


# # ------------------------------------------------
# # BLACKSPOT DETECTION USING DBSCAN
# # ------------------------------------------------
# def detect_blackspots(file):

#     df = pd.read_csv(file)

#     # Remove invalid coordinates
#     df = df[(df["LATITUDE"] != 0) & (df["LONGITUDE"] != 0)]
#     df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

#     coords = df[["LATITUDE", "LONGITUDE"]].values

#     # Apply DBSCAN clustering
#     db = DBSCAN(eps=0.003, min_samples=5)
#     clusters = db.fit_predict(coords)

#     df["cluster"] = clusters

#     # Remove noise points (-1)
#     df = df[df["cluster"] != -1]

#     grouped = (
#         df.groupby("cluster")
#         .agg({
#             "LATITUDE": "mean",
#             "LONGITUDE": "mean",
#             "cluster": "size"
#         })
#         .rename(columns={"cluster": "Accident_Count"})
#         .reset_index(drop=True)
#     )

#     # ------------------------------------------------
#     # RISK LEVEL CLASSIFICATION
#     # ------------------------------------------------
#     def risk_level(count):

#         if count >= 30:
#             return "HIGH RISK"
#         elif count >= 15:
#             return "MEDIUM RISK"
#         else:
#             return "LOW RISK"

#     grouped["Risk_Level"] = grouped["Accident_Count"].apply(risk_level)

#     # Convert coordinates → location name
#     grouped["Location_Name"] = grouped.apply(
#         lambda x: get_location(x["LATITUDE"], x["LONGITUDE"]), axis=1
#     )

#     return grouped


# # ------------------------------------------------
# # GENERATE BLACKSPOT MAP (SEPARATE PAGE)
# # ------------------------------------------------
# def generate_blackspot_map(file):

#     blackspots = detect_blackspots(file)

#     blackspot_map = folium.Map(
#         location=[40.7128, -74.0060],
#         zoom_start=11
#     )

#     for _, row in blackspots.iterrows():

#         if row["Risk_Level"] == "HIGH RISK":
#             color = "red"
#         elif row["Risk_Level"] == "MEDIUM RISK":
#             color = "orange"
#         else:
#             color = "green"

#         folium.CircleMarker(
#             location=[row["LATITUDE"], row["LONGITUDE"]],
#             radius=10,
#             color=color,
#             fill=True,
#             fill_color=color,
#             fill_opacity=0.9,
#             popup=f"""
#             <b>Blackspot Location:</b> {row['Location_Name']}<br>
#             <b>Accident Count:</b> {row['Accident_Count']}<br>
#             <b>Risk Level:</b> {row['Risk_Level']}
#             """
#         ).add_to(blackspot_map)

#     return blackspot_map