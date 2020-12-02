import os
# import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import math


def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
train1000 = pd.read_csv('../../data/train-1000.csv')
consecutive_dis = []

def list2string(L):
    string = str(L)
    return string.replace(' ', '')

# counting...
for t_number in range(1000):
    gps_points = eval(train1000['POLYLINE'][t_number])
    for i in range(len(gps_points)-1):
        pre = gps_points[i]
        post = gps_points[i+1]
        cur_dis = distance(pre, post)
        consecutive_dis.append(cur_dis)
#%%

plt.hist(x = consecutive_dis, 
    bins = 20,
    color = 'steelblue',
    edgecolor = 'black',
    range=(0,0.02)
    )

plt.savefig('../../results/task6/distribution', dpi=240)


# outliar modifying
threshold_min = 0.01
threshold_max = 0.02
threshold_step = 0.002

for t_number in range(1000):
    gps_points = eval(train1000['POLYLINE'][t_number])
    assert isinstance(train1000['POLYLINE'][t_number], str)

    if len(gps_points) < 2: # if there are less than GPS points in this trajectory
        modified_points = gps_points
    else:
        modified_points = gps_points[:1]
        last_point = gps_points[0]
        threshold = threshold_min
        for i in range(1, len(gps_points)):
            next_point = gps_points[i]
            if distance(last_point, next_point) < threshold: # a valid point
                modified_points.append(next_point)
                last_point = next_point
                threshold = threshold_min
            else:
                threshold += threshold_step
                threshold = min(threshold, threshold_max)
        train1000['POLYLINE'][t_number] = list2string(modified_points)

train1000.to_csv('../../data/modified_train-1000.csv',index=0)
    

