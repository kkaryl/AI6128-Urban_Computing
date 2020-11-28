import os
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt
import osmnx as ox 

from task2 import read_N_and_E
from task4 import plot_matched_routes


def linestring2list(string):
    if not isinstance(string, str):
        string = string.wkt

    assert string[:10] == 'LINESTRING'
    string = string.replace(', ', ',')
    string = string[string.find('(')+1:-1]

    return [[float(j) for j in i.split(' ')] for i in string.split(',')]

# givn the roat fid, return the information of roads: (osmid, u, v, length)
def route_info(fid): 

    point_list = gdf_edges.loc[fid, 'geometry']
    point_list = linestring2list(point_list)

    length = 0
    if len(point_list) > 1:
        for i in range(len(point_list)-1):
            length += ((point_list[i+1][0]-point_list[i][0]) ** 2 + (point_list[i+1][1] - point_list[i][1]) ** 2) ** 0.5
    length = round(length, 7)

    return (gdf_edges.loc[fid, 'osmid'], int(gdf_edges.loc[fid, 'u']), int(gdf_edges.loc[fid, 'v']), length)

# two roads with different FID might be the same road(e.g. fid=1100, fid=4231)
# while two roads with the same OSMID might be different(e.g. osmid=868082261), and one road might have multiple OSMID (e.g. fid=4)
def construct_road_fid2id(results): 

    road_fid2id_info = dict()
    road_uvd2id = dict()
    road_id2fids = dict()

    for result in results:
        cpath = result['cpath']
        opath = result['opath']
        for fid in cpath+opath:
            if not fid in road_fid2id_info:
                osmid, u, v, d = route_info(fid)
                uvd = (min(u,v), max(u,v), d)
                if uvd not in road_uvd2id:
                    road_id2fids[len(road_uvd2id)] = []
                    road_uvd2id[uvd] = len(road_uvd2id)
                ID = road_uvd2id[uvd]
                road_id2fids[ID].append(fid)
                road_fid2id_info[fid] = (ID, osmid, u, v, d)

    return road_fid2id_info, road_id2fids

# return the 5 most roads' fids and their name. ([((fid1,fid2), name1, freq), ((fid3,), name2, freq), ..., ((fid4,fid5), name5, freq)])
def five_most_often(results):

    road_id2frequency = defaultdict(int)
    for route in results:
        repeat_c_ids = [road_fid2id_info[c][0] for c in route['cpath']]
        c_ids = []
        for r in repeat_c_ids:
            if len(c_ids) == 0 or r != c_ids[-1]:
                c_ids.append(r)

        for ID in c_ids:
            road_id2frequency[ID] += 1
    sorted_id = sorted(road_id2frequency.keys(), key=lambda x: road_id2frequency[x], reverse=True)

    result = []
    for i in range(5):
        ID = sorted_id[i]
        fids = tuple(road_id2fids[ID])
        road_name = gdf_edges.loc[fids[0], "name"]
        result.append((fids, road_name, road_id2frequency[ID]))

    return result

def five_most_time(results, ignore_log_number=10, ignore_log_rate=1.5):

    road_id2travel_patch = defaultdict(list) # id: [(time1, dis1),(time2, dis2)]

    error = 0
    for route in results:
        c_index = 0
        repeat_c_ids = [road_fid2id_info[c][0] for c in route['cpath']]
        c_ids = []
        for r in repeat_c_ids:
            if len(c_ids) == 0 or r != c_ids[-1]:
                c_ids.append(r)

        last_o_id = road_fid2id_info[route['opath'][0]][0]
        for o_index in range(1, len(route['opath'])):
            cur_o_id = road_fid2id_info[route['opath'][o_index]][0]

            if last_o_id == cur_o_id: # if two consecutive GPS points are in the same road
                if route['spdist'][o_index] > 1e-7:
                    road_id2travel_patch[cur_o_id].append((15, route['spdist'][o_index]))
            else: # if two consecutive GPS passed many different roads
                temp_id_list = []
                temp_dis_list = []

                c_id = c_ids[c_index]    
                # for the current road, the car pass the distance of (road_dis - offset).
                cur_dis = road_fid2id_info[route['opath'][o_index-1]][4] - route['offset'][o_index-1]
                if cur_dis > 1e-7:
                    temp_id_list.append(c_id)
                    temp_dis_list.append(cur_dis) 
                
                c_index += 1
                c_id = c_ids[c_index]

                while c_id != cur_o_id:
                    temp_id_list.append(c_id)
                    temp_dis_list.append(road_fid2id_info[route['cpath'][c_index]][4])
                    c_index += 1
                    c_id = c_ids[c_index]

                if route['offset'][o_index] > 1e-7:
                    temp_id_list.append(c_id)
                    temp_dis_list.append(route['offset'][o_index]) 

                total_dis = sum(temp_dis_list)
                temp_time_list = [15/total_dis * i for i in temp_dis_list]
                for i, t, d in zip(*(temp_id_list, temp_time_list, temp_dis_list)):
                    road_id2travel_patch[i].append((t,d))
                last_o_id = cur_o_id

    mean_pass_times = dict() # (log_number, mean_pass_time)
    for ID, logs in road_id2travel_patch.items():
        log_number = len(logs)
        if log_number < ignore_log_number: # if the number of logs smaller than ignore_log_number, just ignore this road ID
            continue
        road_length = road_fid2id_info[road_id2fids[ID][0]][4]
        total_pass_distance = sum([log[1] for log in logs])
        log_rate = total_pass_distance / road_length
        if log_rate < ignore_log_rate: # if the total distance throughed in this road by cars is smaller than 1.5 length of road, ignore this road ID.
            continue
        total_pass_time = sum([log[0] for log in logs])
        mean_pass_time = total_pass_time / total_pass_distance * road_length
        mean_pass_times[ID] = (log_number, mean_pass_time, log_rate)

    sorted_pass_time = sorted(mean_pass_times.items(), key=lambda x:x[1][1], reverse=True)[:5]
    fid_time_lognumber = [(tuple(road_id2fids[s[0]]), s[1][1], s[1][0], s[1][2]) for s in sorted_pass_time]

    return fid_time_lognumber


gdf_nodes, gdf_edges = read_N_and_E('data/Porto')
G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges)
match_results = pd.read_csv('./data/match_result.csv')

all_results = []
ignore_number = 0
for n in range(1000):
    if len(eval(match_results['opath'][n])) < 2 or len(eval(match_results['cpath'][n])) < 2:
        ignore_number += 1
        continue
    all_results.append(dict(
        t_number=n+1, cpath=eval(match_results['cpath'][n]), opath=eval(match_results['opath'][n]), 
        offset=eval(match_results['offset'][n]), length=eval(match_results['length'][n]),
        spdist=eval(match_results['spdist'][n]), mgeom=linestring2list(match_results['mgeom'][n])
        ))
print(f'There are {ignore_number} routes are ignored due to lack of data.')
road_fid2id_info, road_id2fids = construct_road_fid2id(all_results)

often5 = five_most_often(all_results)
time5 = five_most_time(all_results, ignore_log_number=10, ignore_log_rate=1.5)

fig, ax = ox.plot_graph(G, node_size=3, figsize=(40, 40), edge_linewidth=1, show=False)
x_min, x_max = 9999, -9999
y_min, y_max = 9999, -9999 

for i, color in enumerate(('red', 'red', 'red', 'red', 'red')): # frequency
    road_fid = often5[i][0][0]
    road_wkt = linestring2list(gdf_edges.loc[road_fid,'geometry'])
    x_min = min(x_min, min([i[0] for i in road_wkt]))
    x_max = max(x_max, max([i[0] for i in road_wkt]))
    y_min = min(y_min, min([i[1] for i in road_wkt]))
    y_max = max(y_max, max([i[1] for i in road_wkt]))
    plot_matched_routes(None, road_wkt, color, G, ax, fig)

for i, color in enumerate(('blue', 'blue', 'blue', 'blue', 'blue')): # time
    road_fid = time5[i][0][0]
    road_wkt = linestring2list(gdf_edges.loc[road_fid,'geometry'])
    x_min = min(x_min, min([i[0] for i in road_wkt]))
    x_max = max(x_max, max([i[0] for i in road_wkt]))
    y_min = min(y_min, min([i[1] for i in road_wkt]))
    y_max = max(y_max, max([i[1] for i in road_wkt]))
    plot_matched_routes(None, road_wkt, color, G, ax, fig)

x_mid, y_mid = (x_max+x_min)/2, (y_max+y_min)/2
x_gap = (x_max - x_min) * 0.6
y_gap = (y_max - y_min) * 0.6
if x_gap > y_gap:
    y_gap = max(y_gap, x_gap * 0.6)
else:
    x_gap = max(x_gap, y_gap)

ax.set_xlim(x_mid - x_gap, x_mid + x_gap)
ax.set_ylim(y_mid - y_gap, y_mid + y_gap)

fig.savefig('./savedpictures/task5/most5_freq&time.png', dpi=320)

plt.show()
