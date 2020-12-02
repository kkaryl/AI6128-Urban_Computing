import os
import osmnx as ox 
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from task2 import read_N_and_E


def plot_matched_routes(GPS, mgeom, color, G, ax, fig):
    ax.plot([i[0] for i in mgeom], [i[1] for i in mgeom], c=color, linewidth=1.25)
    if GPS:
        x, y = zip(*GPS)
        ax.scatter(x, y, c=color, marker='x',s=15)


if __name__ == '__main__':
    match_results = pd.read_csv('../../data/match_result.csv')
    train1000 = pd.read_csv('../../data/train-1000.csv')
    gdf_nodes, gdf_edges = read_N_and_E('../../data/Porto')
    G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges)
    fig, ax = ox.plot_graph(G, node_size=3, figsize=(40, 40), edge_linewidth=1, show=False)

    x_min, x_max = 9999, -9999
    y_min, y_max = 9999, -9999 
    for t_number, color in enumerate(('red', 'blue', 'orange', 'yellow', 'green', 'grey', 'pink', 'purple', 'cyan', 'olive')):
        gps_points = eval(train1000['POLYLINE'][t_number])
        mgeom = [[float(j) for j in i.split(' ')] for i in match_results['mgeom'][t_number][11:-1].split(',')]
        x_min = min(x_min, min([i[0] for i in mgeom]))
        x_max = max(x_max, max([i[0] for i in mgeom]))
        y_min = min(y_min, min([i[1] for i in mgeom]))
        y_max = max(y_max, max([i[1] for i in mgeom]))
        plot_matched_routes(gps_points, mgeom, color, G, ax, fig)

    x_mid, y_mid = (x_max+x_min)/2, (y_max+y_min)/2
    x_gap = (x_max - x_min) * 0.6
    y_gap = (y_max - y_min) * 0.6
    if x_gap > y_gap:
        y_gap = max(y_gap, x_gap * 0.6)
    else:
        x_gap = max(x_gap, y_gap)

    ax.set_xlim(x_mid - x_gap, x_mid + x_gap)
    ax.set_ylim(y_mid - y_gap, y_mid + y_gap)

    fig.savefig('../../results/task4/matched_routes.png', dpi=320)

    plt.show()
