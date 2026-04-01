import osmnx as ox

place = "New York, USA"

G = ox.graph_from_place(place, network_type="drive")

ox.save_graphml(G, "road_network.graphml")

print("Road network saved successfully")