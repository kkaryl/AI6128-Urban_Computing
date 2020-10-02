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
import seaborn as sns
from cycler import cycler
from process_data import get_waypoints

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
    parser.add_argument('-a', '--augment', dest='augment', action='store_true',
                        help='Toggle to augment waypoints.', default=True)
    # parser.add_argument('-p', '--production', dest='production', action='store_true', help='Example of boolean arg')
    # parser.add_argument('-o', '--option', dest='option', type=str, help='Example of str arg')
    # parser.add_argument('file', metavar='file', type=str, help='Example of a positional argument')

    args = vars(parser.parse_args())
    wp_augment = bool(args['augment'])
    if args['save_dir']:
        logger.info('saving outputs to: %s', str(args['save_dir']))
        utils.create_dir(args['save_dir'])

    all_waypoints = {}
    for site, floor in utils.get_site_floors(config.DATA_DIR):
        print(site, ' ------------ ', floor)
        wp_count = visualize_waypoints(site, floor, args['save_dir'], int(args['dpi']), wp_augment)
        all_waypoints[(site, floor)] = wp_count

    logger.info(all_waypoints)
    logger.info('COMPLETED')
    logger.info('--------------')

def visualize_waypoints(site, floor, save_dir=None, save_dpi=160, wp_augment=False):
    random.seed(config.RANDOM_SEED)  # this ensure the color printed each time is same
    floor_path = os.path.join(config.DATA_DIR, site, floor)

    floor_waypoints = []
    floor_data_path = os.path.join(floor_path, config.PATH_DATA_DIR)
    txt_filenames = os.listdir(floor_data_path)
    for filename in txt_filenames:
        txt_path = os.path.join(floor_data_path, filename)
        txt_waypoints = get_waypoints(txt_path, xy_only=True, augment_wp=wp_augment)
        floor_waypoints.append(txt_waypoints)

    # read floor information to get map height, width
    json_path = os.path.join(floor_path, config.FLOOR_INFO_JSON_FILE)
    with open(json_path) as file:
        map_info = json.load(file)['map_info']
    map_height, map_width = map_info['height'], map_info['width']

    total_waypoints = 0
    img = mpimg.imread(os.path.join(floor_path, config.FLOOR_IMAGE_FILE))
    sns.reset_orig()
    colors = sns.color_palette('dark', n_colors=10)
    plt.rc('axes', prop_cycle=(cycler('color', colors))) # set colors
    plt.clf()
    plt.imshow(img)
    map_scaler = (img.shape[0] / map_height + img.shape[1] / map_width) / 2
    for i, ways in enumerate(floor_waypoints):
        x, y = zip(*ways)
        total_waypoints += len(x)
        x, y = np.array(x), np.array(y)
        x, y = x * map_scaler, img.shape[0] - y * map_scaler
        plt.plot(x, y, linewidth='0.5', linestyle='-', marker='x', markersize=3)

    if not wp_augment:
        plt.title(f"{site} - {floor} - {total_waypoints} Waypoints".title())
    else:
        plt.title(f"{site} - {floor} - {total_waypoints} Augmented Waypoints".title())

    plt.xticks((np.arange(25, map_width, 25) * map_scaler).astype('uint'),
               np.arange(25, map_width, 25).astype('uint'))
    plt.yticks((img.shape[0] - np.arange(25, map_height, 25) * map_scaler).astype('uint'),
               np.arange(25, map_height, 25).astype('uint'))
    plt.tight_layout()

    if save_dir:
        if not wp_augment:
            save_path = os.path.join(save_dir, site + "--" + floor)
        else:
            save_path = os.path.join(save_dir, site + "--" + floor + "--" + "A")
        plt.savefig(save_path, dpi=save_dpi)
    else:
        plt.show()

    return total_waypoints


if __name__ == '__main__':
    main()
