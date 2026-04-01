import pandas as pd
import folium
import numpy as np

def generate_map(csv_path, extra_location=None):

    df_map = pd.read_csv(csv_path)

    violation_explanations = {
        'speeding': 'Speeding',
        'signal_violation': 'Signal Violation',
        'careless_driving': 'Careless Driving',
        'distracted': 'Driver Distraction',
        'wrong_lane': 'Wrong Lane Usage',
        'drink_drive': 'Drunk Driving'
    }

    def get_top_causes(row):
        causes = []
        for col, name in violation_explanations.items():
            if row[col] == 1:
                causes.append(name)
        return causes if causes else ['No Strong Violation Detected']

    df_map['top_causes'] = df_map.apply(get_top_causes, axis=1)

    def get_severity(row):
        count = sum(row[list(violation_explanations.keys())])
        if count >= 2:
            return "Severe"
        elif count == 1:
            return "Moderate"
        else:
            return "Minor"

    df_map['severity'] = df_map.apply(get_severity, axis=1)

    severity_colors = {
        "Severe": "red",
        "Moderate": "orange",
        "Minor": "green"
    }

    nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

    for _, row in df_map.iterrows():
        if not np.isnan(row['LATITUDE']) and not np.isnan(row['LONGITUDE']):

            popup_text = f"""
            <b>Severity:</b> {row['severity']}<br>
            <b>Causes:</b><br>
            {'<br>'.join(row['top_causes'])}
            """

            folium.CircleMarker(
                location=[row['LATITUDE'], row['LONGITUDE']],
                radius=6,
                color=severity_colors[row['severity']],
                fill=True,
                fill_color=severity_colors[row['severity']],
                fill_opacity=0.75,
                popup=popup_text
            ).add_to(nyc_map)

    
    if extra_location:
        lat, lon = extra_location

        folium.Marker(
            location=[lat, lon],
            popup="🚨 New Predicted Accident",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(nyc_map)

    return nyc_map

# import pandas as pd
# import folium
# import numpy as np
# from modules.blackspot_detector import detect_blackspots


# def generate_map(csv_path, extra_location=None):

#     df_map = pd.read_csv(csv_path)

#     violation_explanations = {
#         'speeding': 'Speeding',
#         'signal_violation': 'Signal Violation',
#         'careless_driving': 'Careless Driving',
#         'distracted': 'Driver Distraction',
#         'wrong_lane': 'Wrong Lane Usage',
#         'drink_drive': 'Drunk Driving'
#     }

#     # -----------------------------------
#     # Identify violation causes
#     # -----------------------------------
#     def get_top_causes(row):
#         causes = []
#         for col, name in violation_explanations.items():
#             if row[col] == 1:
#                 causes.append(name)
#         return causes if causes else ['No Strong Violation Detected']

#     df_map['top_causes'] = df_map.apply(get_top_causes, axis=1)

#     # -----------------------------------
#     # Determine severity level
#     # -----------------------------------
#     def get_severity(row):
#         count = sum(row[list(violation_explanations.keys())])
#         if count >= 2:
#             return "Severe"
#         elif count == 1:
#             return "Moderate"
#         else:
#             return "Minor"

#     df_map['severity'] = df_map.apply(get_severity, axis=1)

#     severity_colors = {
#         "Severe": "red",
#         "Moderate": "orange",
#         "Minor": "green"
#     }

#     # -----------------------------------
#     # Create base map
#     # -----------------------------------
#     nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

#     # -----------------------------------
#     # Plot accident points
#     # -----------------------------------
#     for _, row in df_map.iterrows():

#         if not np.isnan(row['LATITUDE']) and not np.isnan(row['LONGITUDE']):

#             popup_text = f"""
#             <b>Severity:</b> {row['severity']}<br>
#             <b>Causes:</b><br>
#             {'<br>'.join(row['top_causes'])}
#             """

#             folium.CircleMarker(
#                 location=[row['LATITUDE'], row['LONGITUDE']],
#                 radius=6,
#                 color=severity_colors[row['severity']],
#                 fill=True,
#                 fill_color=severity_colors[row['severity']],
#                 fill_opacity=0.75,
#                 popup=popup_text
#             ).add_to(nyc_map)

#     # -----------------------------------
#     # Detect DBSCAN blackspots
#     # -----------------------------------
#     blackspots = detect_blackspots(csv_path)

#     # -----------------------------------
#     # Plot blackspots
#     # -----------------------------------
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
#             popup=f"<b>Blackspot:</b> {row['Location_Name']}<br><b>Risk:</b> {row['Risk_Level']}"
#         ).add_to(nyc_map)

#     # -----------------------------------
#     # Show predicted accident location
#     # -----------------------------------
#     if extra_location:

#         lat, lon = extra_location

#         folium.Marker(
#             location=[lat, lon],
#             popup="🚨 New Predicted Accident",
#             icon=folium.Icon(color="blue", icon="info-sign")
#         ).add_to(nyc_map)

#     return nyc_map
