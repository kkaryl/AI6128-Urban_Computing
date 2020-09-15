import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import random


def track_print(site, floor, savepath=None):
    random.seed(1)  # this ensure the color printed each time is same
    file_path = os.path.join('../data', site, floor)

    json_path = os.path.join(file_path, 'floor_info.json')
    with open(json_path) as file:
        mapinfo = json.load(file)['map_info']
    mapheight, mapwidth = mapinfo['height'], mapinfo['width']

    total_waypoint = []
    file_list = os.listdir(os.path.join(file_path, "path_data_files"))
    for filename in file_list:
        temp_waypoint = []
        txtname = os.path.join(file_path, "path_data_files", filename)
        with open(txtname, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if not line or line[0] == '#':
                    continue

                line_data = line.split('\t')
                if line_data[1] == 'TYPE_WAYPOINT':
                    temp_waypoint.append((float(line_data[2]), float(line_data[3])))
        total_waypoint.append(temp_waypoint)

    img = mpimg.imread(os.path.join(file_path, 'floor_image.png'))
    plt.clf()
    plt.imshow(img)
    mapscaler = (img.shape[0] / mapheight + img.shape[1] / mapwidth) / 2
    for i, ways in enumerate(total_waypoint):
        color = random.choice(('red', 'blue', 'orange', 'yellow', 'green', 'black', 'pink'))
        x, y = zip(*ways)
        x, y = np.array(x), np.array(y)
        x, y = x * mapscaler, img.shape[0] - y * mapscaler
        plt.plot(x, y, linewidth='1', color=color, linestyle='-', marker='x', markersize=4)

    plt.xticks((np.arange(25, mapwidth, 25) * mapscaler).astype('uint'), np.arange(25, mapwidth, 25).astype('uint'))
    plt.yticks((img.shape[0] - np.arange(25, mapheight, 25) * mapscaler).astype('uint'),
               np.arange(25, mapheight, 25).astype('uint'))
    if savepath:
        plt.savefig(savepath, dpi=160)
    else:
        plt.show()


if __name__ == "__main__":
    save_dir = './savedPicture/waypoints'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for site, floor in [('site1', 'B1'), ('site1', 'F1'), ('site1', 'F2'), ('site1', 'F3'), ('site1', 'F4'),
                        ('site2', 'B1'), \
                        ('site2', 'F1'), ('site2', 'F2'), ('site2', 'F3'), ('site2', 'F4'), ('site2', 'F5'),
                        ('site2', 'F6'), ('site2', 'F7'), ('site2', 'F8')]:
        print(site, '   ---------   ', floor)
        save_path = os.path.join(save_dir, site + '--' + floor)
        track_print(site, floor, save_path)
