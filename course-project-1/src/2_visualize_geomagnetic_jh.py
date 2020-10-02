import argparse
import json
import logging
import os
import random
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

import utils
from process_data import get_magnetic_positions
import config

""" CONFIG """
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('E2')


def main():
    save_dir = os.path.join(config.OUTPUT_DIR, os.path.splitext(os.path.basename(__file__))[0])
    logger.info(f'default output path: {save_dir}')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save_dir', help='Save directory for output images', type=str, default=save_dir)
    parser.add_argument('--dpi', help='DPI of saved images', type=int, default=config.SAVE_IMG_DPI)
    parser.add_argument('-a', '--augment', dest='augment', action='store_true',
                        help='Toggle to augment waypoints.', default=True)

    args = vars(parser.parse_args())
    save_dir = str(args['save_dir'])
    dpi = int(args['dpi'])
    wp_augment = bool(args['augment'])
    logger.info(f'CONFIGURATION')
    logger.info(f'save directory: {save_dir}')
    logger.info(f'dpi: {dpi}')
    logger.info(f'augment waypoints: {wp_augment}')

    if save_dir:
        logger.info('saving outputs to: %s', save_dir)
        utils.create_dir(save_dir)

    for site, floor in utils.get_site_floors(config.DATA_DIR):
        print(site, ' ------------ ', floor)
        visualize_geomagnetic(site, floor, save_dir, save_dpi=dpi, augment_wp=wp_augment, m_range=config.MAGNETIC_RANGE)

    logger.info('COMPLETED')
    logger.info('--------------')


def visualize_geomagnetic(site, floor, save_dir=None, save_dpi=160, augment_wp=False, m_range=None):
    random.seed(config.RANDOM_SEED)
    floor_path = os.path.join(config.DATA_DIR, site, floor)

    # Parse magnetic data
    floor_data_path = os.path.join(floor_path, config.PATH_DATA_DIR)
    file_list = os.listdir(floor_data_path)
    floor_magnetic_data = np.zeros((0, 3))
    total_waypoints = 0
    total_mg = 0
    for filename in file_list:
        txt_path = os.path.join(floor_data_path, filename)
        magnetic_data, ori_mg_count, wp_count = get_magnetic_positions(txt_path, augment_wp)
        total_mg += ori_mg_count
        total_waypoints += wp_count
        magnetic_wp_str = np.array(magnetic_data)[:, 1:4].astype(float)
        floor_magnetic_data = np.append(floor_magnetic_data, magnetic_wp_str, axis=0)

    # read floor information to get map height, width
    json_path = os.path.join(floor_path, config.FLOOR_INFO_JSON_FILE)
    with open(json_path) as file:
        map_info = json.load(file)['map_info']
    map_height, map_width = map_info['height'], map_info['width']

    img = mpimg.imread(os.path.join(floor_path, config.FLOOR_IMAGE_FILE))
    reversed_color_map = plt.cm.get_cmap('inferno').reversed()

    plt.clf()
    plt.imshow(img)
    map_scaler = (img.shape[0] / map_height + img.shape[1] / map_width) / 2
    x = floor_magnetic_data[:, 0] * map_scaler
    y = img.shape[0] - floor_magnetic_data[:, 1] * map_scaler
    m_strength = floor_magnetic_data[:, 2]

    if m_range:
        plt.scatter(x, y, c=m_strength, s=10, vmin=m_range[0], vmax=m_range[1], cmap=reversed_color_map)
    else:
        plt.scatter(x, y, c=m_strength, s=10, cmap=reversed_color_map)
    plt.colorbar(cmap=reversed_color_map)
    plt.xticks((np.arange(25, map_width, 25) * map_scaler).astype('uint'),
               np.arange(25, map_width, 25).astype('uint'))
    plt.yticks((img.shape[0] - np.arange(25, map_height, 25) * map_scaler).astype('uint'),
               np.arange(25, map_height, 25).astype('uint'))
    # plt.tight_layout()

    if not augment_wp:
        plt.title(f"{site} - {floor} -- {total_mg} Mag: Ori {total_waypoints} Waypoints".title())
    else:
        plt.title(f"{site} - {floor} -- {total_mg} Mag: Aug {total_waypoints} Waypoints".title())

    if save_dir:
        if augment_wp:
            save_path = os.path.join(save_dir, site + "--" + floor)
        else:
            save_path = os.path.join(save_dir, site + "--" + floor + "--" + "O")
        plt.savefig(save_path, dpi=save_dpi)
    else:
        plt.show()


if __name__ == '__main__':
    main()
