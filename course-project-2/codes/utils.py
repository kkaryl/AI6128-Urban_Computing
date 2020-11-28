import os
import osmnx as ox 
import geopandas as gpd

def read_N_and_E(filepath=None):
    gdf_nodes_path = 'nodes.shp'
    gdf_edges_path = 'edges.shp'
    if not filepath is None:
        gdf_nodes_path = os.path.join(filepath, gdf_nodes_path)
        gdf_edges_path = os.path.join(filepath, gdf_edges_path)
    gdf_nodes = gpd.read_file(gdf_nodes_path)
    gdf_edges = gpd.read_file(gdf_edges_path)

    return gdf_nodes, gdf_edges

def load_G_from_N_and_E(filepath=None):
    gdf_nodes, gdf_edges = read_N_and_E(filepath)
    return ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges)