import os
import osmnx as ox 
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


LINES = True

def read_N_and_E(filepath=None):
    gdf_nodes_path = 'nodes.shp'
    gdf_edges_path = 'edges.shp'
    if not filepath is None:
        gdf_nodes_path = os.path.join(filepath, gdf_nodes_path)
        gdf_edges_path = os.path.join(filepath, gdf_edges_path)
    gdf_nodes = gpd.read_file(gdf_nodes_path)
    gdf_edges = gpd.read_file(gdf_edges_path)

    return gdf_nodes, gdf_edges

def plot_GPS_point_from_trajectory(t_number, color, G, savepath=None, lines=False, show=True):
    if not 0 < t_number < 1001:
        raise ValueError('the t_number must in [1, 1000]')
    t_number -= 1

    fig, ax = ox.plot_graph(G, node_size=3, figsize=(40, 40), edge_linewidth=1.5, show=False)

    gps_points = eval(train1000['POLYLINE'][t_number])
    x, y = zip(*gps_points)
    x_max, x_min, x_gap, x_mid = max(x), min(x), max(x) - min(x), (max(x) + min(x))/2
    y_max, y_min, y_gap, y_mid = max(y), min(y), max(y) - min(y), (max(y) + min(y))/2
    gap = max(x_gap, y_gap) * 0.6
    ax.set_xlim(x_mid - gap, x_mid + gap)
    ax.set_ylim(y_mid - gap, y_mid + gap)

    if lines:
        ax.plot(x, y, linewidth = 4, color=color, linestyle='-', marker='x', markersize=20)
    else:
        ax.scatter(x, y, c=color, marker='x',s=20)

    if savepath:
        fig.savefig(savepath, dpi=80)
        print(f'GPS picture {t_number+1} saving finished.')

    if show:
        plt.show()


if __name__ == '__main__':
    train1000 = pd.read_csv('../../data/train-1000.csv')

    gdf_nodes, gdf_edges = read_N_and_E('../../data/porto')
    G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges)
    # map_xlim, map_ylim = ax.get_xlim(), ax.get_ylim()

    for t_number, color in enumerate(('red', 'blue', 'orange', 'yellow', 'green', 'grey', 'pink', 'purple', 'cyan', 'olive')):
        plot_GPS_point_from_trajectory(t_number+1, color=color, G=G, savepath=f'../../results/task2/GPS{t_number+1}.png', lines=LINES)

    fig, ax = ox.plot_graph(G, node_size=1.5, figsize=(40, 40), edge_linewidth=0.5, show=False)
    # plt.xlim(*map_xlim)
    # plt.ylim(*map_ylim)
    for t_number, color in enumerate(('red', 'blue', 'orange', 'yellow', 'green', 'grey', 'pink', 'purple', 'cyan', 'olive')):
        gps_points = eval(train1000['POLYLINE'][t_number])
        x, y = zip(*gps_points)
        if LINES:
            ax.plot(x, y, linewidth = 1, color=color, linestyle='-', marker='x', markersize=3)
        else:
            ax.scatter(x, y, c=color, marker='x',s=3)

    plt.savefig('../../results/task2/GPSall.png', dpi=320)
