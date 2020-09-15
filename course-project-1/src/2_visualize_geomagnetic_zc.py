import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import random
from data import get_data_from_one_txt


def magnetic_print(site, floor, savepath=None, cbarange=None):
    random.seed(1)  # this ensure the color printed each time is same
    file_path = os.path.join('../data', site, floor)

    json_path = os.path.join(file_path, 'floor_info.json')
    with open(json_path) as file:
        mapinfo = json.load(file)['map_info']
    mapheight, mapwidth = mapinfo['height'], mapinfo['width']

    file_list = os.listdir(os.path.join(file_path, "path_data_files"))
    magnetic_data = np.zeros((0, 3))
    for filename in file_list:
        txtname = os.path.join(file_path, "path_data_files", filename)
        trajectory_data = get_data_from_one_txt(txtname)
        posMagn = np.array(trajectory_data)[:, (1, 2, 6)].astype(float)
        magnetic_data = np.append(magnetic_data, posMagn, axis=0)

    img = mpimg.imread(os.path.join(file_path, 'floor_image.png'))
    plt.clf()
    plt.imshow(img)
    mapscaler = (img.shape[0] / mapheight + img.shape[1] / mapwidth) / 2
    x = magnetic_data[:, 0] * mapscaler
    y = img.shape[0] - magnetic_data[:, 1] * mapscaler
    intensity = magnetic_data[:, 2]
    if cbarange:
        plt.scatter(x, y, c=intensity, s=10, vmin=cbarange[0], vmax=cbarange[1])
    else:
        plt.scatter(x, y, c=intensity, s=10)
    plt.colorbar()
    plt.xticks((np.arange(25, mapwidth, 25) * mapscaler).astype('uint'), np.arange(25, mapwidth, 25).astype('uint'))
    plt.yticks((img.shape[0] - np.arange(25, mapheight, 25) * mapscaler).astype('uint'),
               np.arange(25, mapheight, 25).astype('uint'))
    if savepath:
        plt.savefig(savepath, dpi=160)
    else:
        plt.show()


if __name__ == "__main__":
    save_dir = './savedPicture/magnetic'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for site, floor in [('site1', 'B1'), ('site1', 'F1'), ('site1', 'F2'), ('site1', 'F3'), ('site1', 'F4'),
                        ('site2', 'B1'), \
                        ('site2', 'F1'), ('site2', 'F2'), ('site2', 'F3'), ('site2', 'F4'), ('site2', 'F5'),
                        ('site2', 'F6'), ('site2', 'F7'), ('site2', 'F8')]:
        print(site, '   ---------   ', floor)
        save_path = os.path.join(save_dir, site + '--' + floor)
        magnetic_print(site, floor, save_path, cbarange=(20, 80))

