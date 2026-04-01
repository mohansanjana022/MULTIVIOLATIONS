
# import streamlit as st
# import streamlit.components.v1 as components
# import folium
# from geopy.geocoders import Nominatim
# import osmnx as ox
# import networkx as nx
# import pandas as pd
# import numpy as np
# from folium.plugins import HeatMap, MarkerCluster, AntPath, Fullscreen, MiniMap
# from modules.blackspot_detector import detect_blackspots

# # ------------------------------------------------
# # SESSION STATE
# # ------------------------------------------------

# keys = [
#     "route_generated","route_map","risk_score","risk_level",
#     "distance","travel_time","high_risk_count",
#     "medium_risk_count","safe_segments","directions"
# ]

# for key in keys:
#     if key not in st.session_state:
#         st.session_state[key] = 0 if "count" in key or key=="risk_score" else None

# geolocator = Nominatim(user_agent="traffic_ai")

# # ------------------------------------------------
# # LOAD DATA
# # ------------------------------------------------

# @st.cache_data
# def load_accident_data():
#     df = pd.read_csv("data/nyc_traffic_preprocessed.csv")
#     return df.dropna(subset=["LATITUDE", "LONGITUDE"])

# @st.cache_data
# def load_blackspots():
#     return detect_blackspots("data/nyc_traffic_preprocessed.csv")

# @st.cache_resource
# def load_graph():
#     return ox.load_graphml("road_network.graphml")

# # ------------------------------------------------
# # FUNCTIONS
# # ------------------------------------------------

# def get_coordinates(place):
#     loc = geolocator.geocode(place)
#     return (loc.latitude, loc.longitude) if loc else None

# def calculate_distance(G, route):
#     return sum(G.get_edge_data(u, v)[0]["length"] for u, v in zip(route[:-1], route[1:])) / 1000

# def estimate_time(distance):
#     return (distance / 40) * 60

# def generate_directions(G, route):
#     steps = []
#     for u, v in zip(route[:-1], route[1:]):
#         edge = G.get_edge_data(u, v)[0]
#         name = edge.get("name", "Unnamed Road")
#         length = edge.get("length", 0) / 1000
#         steps.append(f"Continue on {name} for {length:.2f} km")
#     return steps

# def get_color(risk):
#     return "#FF3B30" if risk=="HIGH RISK" else "#FF9500" if risk=="MEDIUM RISK" else "#34C759"

# # ------------------------------------------------
# # ROUTE GENERATION
# # ------------------------------------------------

# def generate_safe_route(start_coord, end_coord):
#     G = load_graph()
#     blackspots = load_blackspots()

#     for u, v, k, data in G.edges(keys=True, data=True):
#         data["weight"] = data.get("length", 1)

#     for _, row in blackspots.iterrows():
#         node = ox.distance.nearest_nodes(G, row["LONGITUDE"], row["LATITUDE"])
#         for neighbor in G.neighbors(node):
#             for key in G[node][neighbor]:
#                 multiplier = 10 if row["Risk_Level"]=="HIGH RISK" else 6 if row["Risk_Level"]=="MEDIUM RISK" else 3
#                 G[node][neighbor][key]["weight"] *= multiplier

#     orig = ox.distance.nearest_nodes(G, start_coord[1], start_coord[0])
#     dest = ox.distance.nearest_nodes(G, end_coord[1], end_coord[0])

#     route = nx.shortest_path(G, orig, dest, weight="weight")
#     return G, route, blackspots

# # ------------------------------------------------
# # MAP (STATIC HTML FIX)
# # ------------------------------------------------

# def plot_route(G, route, start_coord, end_coord, blackspots, show_heatmap=True):

#     m = folium.Map(location=start_coord, zoom_start=13, tiles="CartoDB positron")

#     Fullscreen().add_to(m)
#     MiniMap().add_to(m)

#     route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

#     folium.PolyLine(route_coords, color="black", weight=8, opacity=0.4).add_to(m)

#     AntPath(
#         locations=route_coords,
#         color="#0066FF",
#         weight=6,
#         delay=800,
#         dash_array=[10, 20],
#         pulse_color="#FFFFFF"
#     ).add_to(m)

#     folium.Marker(start_coord, icon=folium.Icon(color="green")).add_to(m)
#     folium.Marker(end_coord, icon=folium.Icon(color="red")).add_to(m)

#     marker_cluster = MarkerCluster().add_to(m)

#     for _, row in blackspots.iterrows():
#         color = get_color(row["Risk_Level"])

#         folium.CircleMarker(
#             [row["LATITUDE"], row["LONGITUDE"]],
#             radius=4,
#             color=color,
#             fill=True
#         ).add_to(marker_cluster)

#     if show_heatmap:
#         df = load_accident_data()
#         HeatMap(df[["LATITUDE","LONGITUDE"]].values.tolist()).add_to(m)

#     # Risk calculation
#     high = medium = 0
#     for _, row in blackspots.iterrows():
#         for lat, lon in route_coords:
#             if np.sqrt((lat-row["LATITUDE"])**2 + (lon-row["LONGITUDE"])**2) < 0.01:
#                 if row["Risk_Level"]=="HIGH RISK":
#                     high += 1
#                 elif row["Risk_Level"]=="MEDIUM RISK":
#                     medium += 1

#     safe = len(route_coords) - (high + medium)
#     risk_score = min((high*4)+(medium*2), 100)
#     level = "HIGH RISK" if risk_score>70 else "MEDIUM RISK" if risk_score>30 else "LOW RISK"

#     return m._repr_html_(), risk_score, level, high, medium, safe

# # ------------------------------------------------
# # UI FUNCTION
# # ------------------------------------------------

# def show_safe_route():

#     st.markdown("## 🚦 AI Safe Route Recommendation")

#     start = st.text_input("Start Location")
#     dest = st.text_input("Destination")
#     show_heatmap = st.checkbox("Show Heatmap", True)

#     if st.button("Find Safest Route"):

#         sc = get_coordinates(start)
#         dc = get_coordinates(dest)

#         if not sc or not dc:
#             st.error("Invalid location")
#             return

#         with st.spinner("Processing safest route..."):

#             G, route, bs = generate_safe_route(sc, dc)

#             dist = calculate_distance(G, route)
#             time = estimate_time(dist)
#             dirs = generate_directions(G, route)

#             m_html, score, level, high, med, safe = plot_route(G, route, sc, dc, bs, show_heatmap)

#             st.session_state.route_map = m_html
#             st.session_state.risk_score = score
#             st.session_state.distance = dist
#             st.session_state.travel_time = time
#             st.session_state.high_risk_count = high
#             st.session_state.medium_risk_count = med
#             st.session_state.safe_segments = safe
#             st.session_state.directions = dirs
#             st.session_state.route_generated = True

#     # DISPLAY
#     if st.session_state.route_generated:

#         st.markdown("### 🚗 Route Overview")

#         col1, col2, col3 = st.columns(3)
#         col1.metric("📏 Distance", f"{st.session_state.distance:.2f} km")
#         col2.metric("⏱ Travel Time", f"{st.session_state.travel_time:.1f} min")
#         col3.metric("⚠ Risk Score", f"{st.session_state.risk_score}/100")

#         # ✅ STATIC MAP (NO RERENDER)
#         if st.session_state.route_map:
#             components.html(
#                 st.session_state.route_map,
#                 height=750,
#                 scrolling=False
#             )

#         st.markdown("### 🧭 Directions")

#         for i, step in enumerate(st.session_state.directions[:15]):
#             st.write(f"{i+1}. {step}")


import streamlit as st
import streamlit.components.v1 as components
import folium
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from folium.plugins import HeatMap, MarkerCluster, AntPath, Fullscreen, MiniMap
from modules.blackspot_detector import detect_blackspots

from ui_config import apply_global_style

apply_global_style()
# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
keys = [
    "route_generated","route_map","risk_score",
    "distance","travel_time","high_risk_count",
    "medium_risk_count","safe_segments","directions","routes"
]

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = None

geolocator = Nominatim(user_agent="traffic_ai")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
@st.cache_data
def load_accident_data():
    df = pd.read_csv("data/nyc_traffic_preprocessed.csv")
    return df.dropna(subset=["LATITUDE", "LONGITUDE"])

@st.cache_data
def load_blackspots():
    return detect_blackspots("data/nyc_traffic_preprocessed.csv")

@st.cache_resource
def load_graph():
    return ox.load_graphml("road_network.graphml")

# ------------------------------------------------
# FUNCTIONS
# ------------------------------------------------
def get_coordinates(place):
    loc = geolocator.geocode(place)
    return (loc.latitude, loc.longitude) if loc else None

def calculate_distance(G, route):
    return sum(G.get_edge_data(u, v)[0]["length"] for u, v in zip(route[:-1], route[1:])) / 1000

def estimate_time(distance):
    return (distance / 40) * 60

def generate_directions(G, route):
    steps = []
    for u, v in zip(route[:-1], route[1:]):
        edge = G.get_edge_data(u, v)[0]
        name = edge.get("name", "Unnamed Road")
        length = edge.get("length", 0) / 1000
        steps.append(f"Continue on {name} for {length:.2f} km")
    return steps

def get_color(risk):
    return "#FF3B30" if risk=="HIGH RISK" else "#FF9500" if risk=="MEDIUM RISK" else "#34C759"

# ------------------------------------------------
# MULTI ROUTE GENERATION
# ------------------------------------------------
def generate_routes(start_coord, end_coord):

    G = load_graph()
    blackspots = load_blackspots()

    G_safe = G.copy()
    G_balanced = G.copy()
    G_fast = G.copy()

    # SAFE
    for u, v, k, data in G_safe.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    for _, row in blackspots.iterrows():
        node = ox.distance.nearest_nodes(G_safe, row["LONGITUDE"], row["LATITUDE"])
        for neighbor in G_safe.neighbors(node):
            for key in G_safe[node][neighbor]:
                multiplier = 12 if row["Risk_Level"]=="HIGH RISK" else 8 if row["Risk_Level"]=="MEDIUM RISK" else 4
                G_safe[node][neighbor][key]["weight"] *= multiplier

    # BALANCED
    for u, v, k, data in G_balanced.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    for _, row in blackspots.iterrows():
        node = ox.distance.nearest_nodes(G_balanced, row["LONGITUDE"], row["LATITUDE"])
        for neighbor in G_balanced.neighbors(node):
            for key in G_balanced[node][neighbor]:
                multiplier = 6 if row["Risk_Level"]=="HIGH RISK" else 3
                G_balanced[node][neighbor][key]["weight"] *= multiplier

    # FAST
    for u, v, k, data in G_fast.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    orig = ox.distance.nearest_nodes(G, start_coord[1], start_coord[0])
    dest = ox.distance.nearest_nodes(G, end_coord[1], end_coord[0])

    route_safe = nx.shortest_path(G_safe, orig, dest, weight="weight")
    route_balanced = nx.shortest_path(G_balanced, orig, dest, weight="weight")
    route_fast = nx.shortest_path(G_fast, orig, dest, weight="weight")

    return G, route_safe, route_balanced, route_fast, blackspots

# ------------------------------------------------
# MAP
# ------------------------------------------------
def plot_route(G, route, start_coord, end_coord, blackspots, show_heatmap=True):

    m = folium.Map(location=start_coord, zoom_start=13, tiles="CartoDB positron")
    Fullscreen().add_to(m)
    MiniMap().add_to(m)

    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

    folium.PolyLine(route_coords, color="black", weight=6, opacity=0.3).add_to(m)

    AntPath(route_coords, color="#0066FF", weight=6).add_to(m)

    folium.Marker(start_coord, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end_coord, icon=folium.Icon(color="red")).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in blackspots.iterrows():
        folium.CircleMarker(
            [row["LATITUDE"], row["LONGITUDE"]],
            radius=4,
            color=get_color(row["Risk_Level"]),
            fill=True
        ).add_to(marker_cluster)

    if show_heatmap:
        df = load_accident_data()
        HeatMap(df[["LATITUDE","LONGITUDE"]].values.tolist()).add_to(m)

    # Risk
    high = medium = 0
    for _, row in blackspots.iterrows():
        for lat, lon in route_coords:
            if np.sqrt((lat-row["LATITUDE"])**2 + (lon-row["LONGITUDE"])**2) < 0.01:
                if row["Risk_Level"]=="HIGH RISK":
                    high += 1
                elif row["Risk_Level"]=="MEDIUM RISK":
                    medium += 1

    safe = len(route_coords) - (high + medium)
    risk_score = min((high*4)+(medium*2), 100)

    return m._repr_html_(), risk_score, high, medium, safe

# ------------------------------------------------
# UI
# ------------------------------------------------
import streamlit as st
import streamlit.components.v1 as components
import folium
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from folium.plugins import HeatMap, MarkerCluster, AntPath, Fullscreen, MiniMap
from modules.blackspot_detector import detect_blackspots

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
keys = [
    "route_generated","route_map","risk_score",
    "distance","travel_time","high_risk_count",
    "medium_risk_count","safe_segments","directions","routes"
]

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = None

geolocator = Nominatim(user_agent="traffic_ai")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
@st.cache_data
def load_accident_data():
    df = pd.read_csv("data/nyc_traffic_preprocessed.csv")
    return df.dropna(subset=["LATITUDE", "LONGITUDE"])

@st.cache_data
def load_blackspots():
    return detect_blackspots("data/nyc_traffic_preprocessed.csv")

@st.cache_resource
def load_graph():
    return ox.load_graphml("road_network.graphml")

# ------------------------------------------------
# FUNCTIONS
# ------------------------------------------------
def get_coordinates(place):
    loc = geolocator.geocode(place)
    return (loc.latitude, loc.longitude) if loc else None

def calculate_distance(G, route):
    return sum(G.get_edge_data(u, v)[0]["length"] for u, v in zip(route[:-1], route[1:])) / 1000

def estimate_time(distance):
    return (distance / 40) * 60

def generate_directions(G, route):
    steps = []
    for u, v in zip(route[:-1], route[1:]):
        edge = G.get_edge_data(u, v)[0]
        name = edge.get("name", "Unnamed Road")
        length = edge.get("length", 0) / 1000
        steps.append(f"Continue on {name} for {length:.2f} km")
    return steps

def get_color(risk):
    return "#FF3B30" if risk=="HIGH RISK" else "#FF9500" if risk=="MEDIUM RISK" else "#34C759"

# ------------------------------------------------
# MULTI ROUTE GENERATION
# ------------------------------------------------
def generate_routes(start_coord, end_coord):

    G = load_graph()
    blackspots = load_blackspots()

    G_safe = G.copy()
    G_balanced = G.copy()
    G_fast = G.copy()

    # SAFE
    for u, v, k, data in G_safe.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    for _, row in blackspots.iterrows():
        node = ox.distance.nearest_nodes(G_safe, row["LONGITUDE"], row["LATITUDE"])
        for neighbor in G_safe.neighbors(node):
            for key in G_safe[node][neighbor]:
                multiplier = 12 if row["Risk_Level"]=="HIGH RISK" else 8 if row["Risk_Level"]=="MEDIUM RISK" else 4
                G_safe[node][neighbor][key]["weight"] *= multiplier

    # BALANCED
    for u, v, k, data in G_balanced.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    for _, row in blackspots.iterrows():
        node = ox.distance.nearest_nodes(G_balanced, row["LONGITUDE"], row["LATITUDE"])
        for neighbor in G_balanced.neighbors(node):
            for key in G_balanced[node][neighbor]:
                multiplier = 6 if row["Risk_Level"]=="HIGH RISK" else 3
                G_balanced[node][neighbor][key]["weight"] *= multiplier

    # FAST
    for u, v, k, data in G_fast.edges(keys=True, data=True):
        data["weight"] = data.get("length", 1)

    orig = ox.distance.nearest_nodes(G, start_coord[1], start_coord[0])
    dest = ox.distance.nearest_nodes(G, end_coord[1], end_coord[0])

    route_safe = nx.shortest_path(G_safe, orig, dest, weight="weight")
    route_balanced = nx.shortest_path(G_balanced, orig, dest, weight="weight")
    route_fast = nx.shortest_path(G_fast, orig, dest, weight="weight")

    return G, route_safe, route_balanced, route_fast, blackspots

# ------------------------------------------------
# MAP
# ------------------------------------------------
def plot_route(G, route, start_coord, end_coord, blackspots, show_heatmap=True):

    m = folium.Map(location=start_coord, zoom_start=13, tiles="CartoDB positron")
    Fullscreen().add_to(m)
    MiniMap().add_to(m)

    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

    folium.PolyLine(route_coords, color="black", weight=6, opacity=0.3).add_to(m)

    AntPath(route_coords, color="#0066FF", weight=6).add_to(m)

    folium.Marker(start_coord, icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end_coord, icon=folium.Icon(color="red")).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in blackspots.iterrows():
        folium.CircleMarker(
            [row["LATITUDE"], row["LONGITUDE"]],
            radius=4,
            color=get_color(row["Risk_Level"]),
            fill=True
        ).add_to(marker_cluster)

    if show_heatmap:
        df = load_accident_data()
        HeatMap(df[["LATITUDE","LONGITUDE"]].values.tolist()).add_to(m)

    # Risk
    high = medium = 0
    for _, row in blackspots.iterrows():
        for lat, lon in route_coords:
            if np.sqrt((lat-row["LATITUDE"])**2 + (lon-row["LONGITUDE"])**2) < 0.01:
                if row["Risk_Level"]=="HIGH RISK":
                    high += 1
                elif row["Risk_Level"]=="MEDIUM RISK":
                    medium += 1

    safe = len(route_coords) - (high + medium)
    risk_score = min((high*4)+(medium*2), 100)

    return m._repr_html_(), risk_score, high, medium, safe

# ------------------------------------------------
# UI
# ------------------------------------------------
def show_safe_route():
    
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("## 🚦 AI Safe Route Recommendation")

    start = st.text_input("Start Location")
    dest = st.text_input("Destination")
    show_heatmap = st.checkbox("Show Heatmap", True)

    if st.button("Find Routes"):

        sc = get_coordinates(start)
        dc = get_coordinates(dest)

        if not sc or not dc:
            st.error("Invalid location")
            return

        with st.spinner("Generating routes..."):

            G, route_safe, route_balanced, route_fast, bs = generate_routes(sc, dc)

            st.session_state.routes = {
                "Safe": route_safe,
                "Balanced": route_balanced,
                "Fast": route_fast
            }

            st.session_state.G = G
            st.session_state.bs = bs
            st.session_state.sc = sc
            st.session_state.dc = dc

            st.session_state.route_generated = True

    # ------------------------------------------------
    # DISPLAY
    # ------------------------------------------------
    if st.session_state.route_generated:

        G = st.session_state.G
        bs = st.session_state.bs
        sc = st.session_state.sc
        dc = st.session_state.dc

        # SELECT ROUTE
        selected = st.radio(
            "Choose Route",
            ["Safe", "Balanced", "Fast"],
            horizontal=True
        )

        route = st.session_state.routes[selected]

        m_html, score, high, med, safe = plot_route(G, route, sc, dc, bs)

        dist = calculate_distance(G, route)
        time = estimate_time(dist)
        dirs = generate_directions(G, route)

        # METRICS
        st.markdown("### 🚗 Route Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Distance", f"{dist:.2f} km")
        col2.metric("⏱ Time", f"{time:.1f} min")
        col3.metric("⚠ Risk", f"{score}/100")

        # EXPLAIN
        st.markdown("### 🟢 Why This Route?")
        st.success(f"""
✔ Avoids {high} high-risk zones  
✔ {safe} safe segments  
✔ Safety improvement: {100-score}%
""")

        # COMPARISON
        def get_metrics(r):
            d = calculate_distance(G, r)
            t = estimate_time(d)
            return round(d,2), round(t,1)

        safe_d, safe_t = get_metrics(st.session_state.routes["Safe"])
        bal_d, bal_t = get_metrics(st.session_state.routes["Balanced"])
        fast_d, fast_t = get_metrics(st.session_state.routes["Fast"])

        df = pd.DataFrame({
            "Route":["🟢 Safe","🟡 Balanced","🔴 Fast"],
            "Distance":[safe_d, bal_d, fast_d],
            "Time":[safe_t, bal_t, fast_t]
        })

        st.dataframe(df, use_container_width=True)

        # ALERTS
        st.markdown("### 🚨 Alerts")
        if high > 0:
            st.error(f"{high} high-risk zones ahead!")
        elif med > 0:
            st.warning(f"{med} medium-risk zones nearby")
        else:
            st.success("Safe route")

        # MAP
        components.html(m_html, height=750, scrolling=False)

        # DIRECTIONS
        st.markdown("### 🧭 Directions")
        for i, step in enumerate(dirs[:15]):
            st.write(f"{i+1}. {step}")

    st.markdown('</div>',unsafe_allow_html=True)