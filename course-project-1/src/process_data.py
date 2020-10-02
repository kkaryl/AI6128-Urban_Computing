from dataclasses import dataclass
import os
import numpy as np
from sample_codes.compute_f import compute_step_positions

@dataclass
class MagneticData():
    unix_time: int
    x_pos: float
    y_pos: float
    m_strength: float

    def __post_init__(self):
        self.unix_time = int(self.unix_time)
        self.x_pos = float(self.x_pos)
        self.y_pos = float(self.y_pos)
        self.m_strength = float(self.m_strength)

def get_waypoints(txt_path: str, xy_only = True, augment_wp=False):
    wp = []

    # for waypoint augmentation using accelerometer and rotation vector
    accel = []
    rotate = []

    # parse text file
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue

            line_data = line.split('\t')
            if line_data[1] == 'TYPE_WAYPOINT':
                # Unix Time, X Pos, Y Pos
                wp.append([int(line_data[0]), float(line_data[2]), float(line_data[3])])
            elif augment_wp and line_data[1] == 'TYPE_ACCELEROMETER':
                # Unix Time, X axis, Y axis, Z axis
                accel.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif augment_wp and line_data[1] == 'TYPE_ROTATION_VECTOR':
                # Unix Time, X axis, Y axis, Z axis
                rotate.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])

    wp = np.array(wp)

    if augment_wp:
        # get more waypoints using accelerator and rotation position data
        accel, rotate = np.array(accel), np.array(rotate)
        wp = compute_step_positions(accel, rotate, wp)  # compute_f function

    return wp[:,1:] if xy_only else wp

def get_magnetic_positions(txt_path: str, augment_wp=False):
    mg, wp = [], []

    # for waypoint augmentation using accelerometer and rotation vector
    accel = []
    rotate = []

    # parse text file
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue

            line_data = line.split('\t')
            if line_data[1] == 'TYPE_MAGNETIC_FIELD':
                # Unix Time, X axis, Y axis, Z axis
                mg.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif line_data[1] == 'TYPE_WAYPOINT':
                # Unix Time, X Pos, Y Pos
                wp.append([int(line_data[0]), float(line_data[2]), float(line_data[3])])
            elif augment_wp and line_data[1] == 'TYPE_ACCELEROMETER':
                # Unix Time, X axis, Y axis, Z axis
                accel.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif augment_wp and line_data[1] == 'TYPE_ROTATION_VECTOR':
                # Unix Time, X axis, Y axis, Z axis
                rotate.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])

    mg, wp = np.array(mg), np.array(wp)
    ori_mg_count = len(mg)
    if augment_wp:
        # get more waypoints using accelerator and rotation position data
        accel, rotate = np.array(accel), np.array(rotate)
        wp = compute_step_positions(accel, rotate, wp) # compute_f function

    wp_time = wp[:, 0]  # extract time
    # convert magnetic time position to closest waypoint's time
    for m_row in mg:
        closest_time_idx = np.argmin(abs(wp_time - m_row[0]))
        m_row[0] = wp_time[closest_time_idx]

    # aggregate magnetic values of the same waypoint's time
    wp_magnetic = []
    for time, x_pos, y_pos in wp:
        m_time_data = np.array([[m[1], m[2], m[3]] for m in mg if m[0] == time])
        m_agg_data = [time, x_pos, y_pos, 0.]
        x = m_time_data[0][1]
        if len(m_time_data) > 0:
            m_str = np.mean(np.sqrt(np.sum(m_time_data ** 2, axis=1)))
            m_agg_data[3] = m_str
        wp_magnetic.append(m_agg_data)
    wp_count = len(wp_magnetic)
    return wp_magnetic, ori_mg_count, wp_count


# if __name__ == '__main__':
#     folder = '../data/site1/B1/path_data_files'
#     filename = '5dda14a2c5b77e0006b17533.txt'
#     file_path = os.path.join(folder, filename)
#     file_path2 = '../data\\site1\\B1\\path_data_files\\5dda14979191710006b5720e.txt'
#     wp_m = get_magnetic_positions(file_path2,augment_wp=False)
#     print(wp_m[0])
