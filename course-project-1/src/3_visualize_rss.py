import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import random
from collections import defaultdict
from data import get_data_from_one_txt
import config


def wifi_print(site, floor, savepath=None, cbarange=None, selectmethod='random 3'):
    random.seed(1)  # this ensure the color printed each time is same
    file_path = os.path.join('../data', site, floor)

    json_path = os.path.join(file_path, 'floor_info.json')
    with open(json_path) as file:
        mapinfo = json.load(file)['map_info']
    mapheight, mapwidth = mapinfo['height'], mapinfo['width']

    file_list = os.listdir(os.path.join(file_path, "path_data_files"))

    wifi_data = defaultdict(list)
    for filename in file_list:
        txtname = os.path.join(file_path, "path_data_files", filename)
        trajectory_data = get_data_from_one_txt(txtname)
        for tdata in trajectory_data:
            px, py = tdata[1], tdata[2]
            timestamp_wifis = tdata[7]
            for bssid, rssi in timestamp_wifis.items():
                wifi_data[bssid].append((px, py, rssi))

    if selectmethod == 'input':
        print(f'This floor has {len(wifi_data)} wifi aps')
        print('Example 10 wifi ap bssids:\n')
        ten_wifi_sample = random.sample(wifi_data.keys(), 10)
        for bssid in ten_wifi_sample:
            print(bssid)
        target_wifi = input(f"Please input target wifi ap bssid:\n")
        target_wifi_data = np.array(wifi_data[target_wifi])

        img = mpimg.imread(os.path.join(file_path, 'floor_image.png'))
        plt.clf()
        plt.imshow(img)
        plt.title('Wifi: ' + bssid)
        mapscaler = (img.shape[0] / mapheight + img.shape[1] / mapwidth) / 2
        x = target_wifi_data[:, 0] * mapscaler
        y = img.shape[0] - target_wifi_data[:, 1] * mapscaler
        rssi_intensity = target_wifi_data[:, 2]
        if cbarange:
            plt.scatter(x, y, c=rssi_intensity, s=10, vmin=cbarange[0], vmax=cbarange[1])
        else:
            plt.scatter(x, y, c=rssi_intensity, s=10)
        plt.colorbar()
        plt.xticks((np.arange(25, mapwidth, 25) * mapscaler).astype('uint'), np.arange(25, mapwidth, 25).astype('uint'))
        plt.yticks((img.shape[0] - np.arange(25, mapheight, 25) * mapscaler).astype('uint'),
                   np.arange(25, mapheight, 25).astype('uint'))
        if savepath:
            plt.savefig(savepath, dpi=160)
        else:
            plt.show()
    else:
        selectmethod = selectmethod.split()
        if len(selectmethod) == 2 and selectmethod[0] == 'random':
            sample_number = int(selectmethod[1])
            bssids = random.sample(wifi_data.keys(), sample_number)

            if not savepath:
                savedir = './WifiHeatMap'
            else:
                savedir = savepath
            if not os.path.exists(savedir):
                os.makedirs(savedir)

            for bssid in bssids:
                target_wifi_data = np.array(wifi_data[bssid])
                savepath = os.path.join(savedir, bssid.replace(':', '-'))

                img = mpimg.imread(os.path.join(file_path, 'floor_image.png'))
                plt.clf()
                plt.imshow(img)
                plt.title('Wifi: ' + bssid)
                mapscaler = (img.shape[0] / mapheight + img.shape[1] / mapwidth) / 2
                x = target_wifi_data[:, 0] * mapscaler
                y = img.shape[0] - target_wifi_data[:, 1] * mapscaler
                rssi_intensity = target_wifi_data[:, 2]
                if cbarange:
                    plt.scatter(x, y, c=rssi_intensity, s=10, vmin=cbarange[0], vmax=cbarange[1])
                else:
                    plt.scatter(x, y, c=rssi_intensity, s=10)
                plt.colorbar()
                plt.xticks((np.arange(25, mapwidth, 25) * mapscaler).astype('uint'),
                           np.arange(25, mapwidth, 25).astype('uint'))
                plt.yticks((img.shape[0] - np.arange(25, mapheight, 25) * mapscaler).astype('uint'),
                           np.arange(25, mapheight, 25).astype('uint'))
                plt.savefig(savepath, dpi=160)
        else:
            raise ValueError('Parameter selectmethod is not in a right form.')


if __name__ == "__main__":
    # wifi_print('site1', 'F1', savepath='./wifipictest', cbarange=(-90, -45), selectmethod='input')
    save_dir = os.path.join(config.OUTPUT_DIR, os.path.splitext(os.path.basename(__file__))[0])
    #save_dir = './savedPicture/wifi'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for site, floor in [('site1', 'B1'), ('site1', 'F1'), ('site1', 'F2'), ('site1', 'F3'), ('site1', 'F4'),
                        ('site2', 'B1'), \
                        ('site2', 'F1'), ('site2', 'F2'), ('site2', 'F3'), ('site2', 'F4'), ('site2', 'F5'),
                        ('site2', 'F6'), ('site2', 'F7'), ('site2', 'F8')]:
        print(site, '   ---------   ', floor)
        save_path = os.path.join(save_dir, site + '--' + floor)
        wifi_print(site, floor, save_path)
    print("Done")