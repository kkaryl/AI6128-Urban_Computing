import argparse
import json
import logging
import os
import random
import sys

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import utils
import config

""" CONFIG """
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('E1')




def main():
    # save_path = Path(config.OUTPUT_DIR).resolve().joinpath(Path(__file__).resolve().stem)
    save_path = os.path.join(config.OUTPUT_DIR, os.path.splitext(os.path.basename(__file__))[0])
    logger.info(f'default output path: {save_path}')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save_dir', help='Save directory for output images', type=str, default=save_path)
    parser.add_argument('--dpi', help='DPI of saved images', type=int, default=config.SAVE_IMG_DPI)
    # parser.add_argument('-p', '--production', dest='production', action='store_true', help='Example of boolean arg')
    # parser.add_argument('-o', '--option', dest='option', type=str, help='Example of str arg')
    # parser.add_argument('file', metavar='file', type=str, help='Example of a positional argument')

    args = vars(parser.parse_args())

    if args['save_dir']:
        logger.info('saving outputs to: %s', str(args['save_dir']))
        utils.create_dir(args['save_dir'])

    for site, floor in utils.get_site_floors(config.DATA_DIR):
        print(site, ' ------------ ', floor)
        visualize_waypoints(site, floor, args['save_dir'], int(args['dpi']))

    logger.info('COMPLETED')
    logger.info('--------------')

def visualize_waypoints(site, floor, save_dir=None, save_dpi=160):
    random.seed(config.RANDOM_SEED)  # this ensure the color printed each time is same
    floor_path = os.path.join(config.DATA_DIR, site, floor)

    floor_waypoints = []
    floor_data_path = os.path.join(floor_path, config.PATH_DATA_DIR)
    txt_filenames = os.listdir(floor_data_path)
    for filename in txt_filenames:
        txt_waypoints = []
        txt_path = os.path.join(floor_data_path, filename)
        with open(txt_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if not line or line[0] == '#':
                    continue

                line_data = line.split('\t')
                if line_data[1] == 'TYPE_WAYPOINT':
                    txt_waypoints.append((float(line_data[2]), float(line_data[3])))
        floor_waypoints.append(txt_waypoints)

    # read floor information to get map height, width
    json_path = os.path.join(floor_path, config.FLOOR_INFO_JSON_FILE)
    with open(json_path) as file:
        map_info = json.load(file)['map_info']
    map_height, map_width = map_info['height'], map_info['width']

    img = mpimg.imread(os.path.join(floor_path, config.FLOOR_IMAGE_FILE))
    plt.clf()
    plt.imshow(img)
    map_scaler = (img.shape[0] / map_height + img.shape[1] / map_width) / 2
    for i, ways in enumerate(floor_waypoints):
        color = random.choice(('red', 'blue', 'orange', 'yellow', 'green', 'black', 'pink'))
        x, y = zip(*ways)
        x, y = np.array(x), np.array(y)
        x, y = x * map_scaler, img.shape[0] - y * map_scaler
        plt.plot(x, y, linewidth='1', color=color, linestyle='-', marker='x', markersize=4)

    plt.xticks((np.arange(25, map_width, 25) * map_scaler).astype('uint'),
               np.arange(25, map_width, 25).astype('uint'))
    plt.yticks((img.shape[0] - np.arange(25, map_height, 25) * map_scaler).astype('uint'),
               np.arange(25, map_height, 25).astype('uint'))
    plt.tight_layout()

    if save_dir:
        save_path = os.path.join(save_dir, site + "--" + floor)
        plt.savefig(save_path, dpi=save_dpi)
    else:
        plt.show()


if __name__ == '__main__':
    main()
