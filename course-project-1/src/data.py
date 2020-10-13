import os
import numpy as np
from collections import defaultdict
import random
from samplecode.compute_f import compute_step_positions


inf = float('inf')
def get_data_from_one_txt(txtpath, augmentation=True):
    acce = []
    magn = []
    ahrs = []
    wifi = []
    ibeacon = []
    waypoint = []

    with open(txtpath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue

            line_data = line.split('\t')

            if line_data[1] == 'TYPE_ACCELEROMETER':
                acce.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif line_data[1] == 'TYPE_MAGNETIC_FIELD':
                magn.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif line_data[1] == 'TYPE_ROTATION_VECTOR':
                ahrs.append([int(line_data[0]), float(line_data[2]), float(line_data[3]), float(line_data[4])])
            elif line_data[1] == 'TYPE_WIFI':
                sys_ts = line_data[0]
                bssid = line_data[3]
                rssi = line_data[4]
                wifi_data = [sys_ts, bssid, rssi]
                wifi.append(wifi_data)
            elif line_data[1] == 'TYPE_BEACON':
                ts = line_data[0]
                uuid = line_data[2]
                major = line_data[3]
                minor = line_data[4]
                rssi = line_data[6]
                ibeacon_data = [ts, '_'.join([uuid, major, minor]), rssi]
                ibeacon.append(ibeacon_data)
            elif line_data[1] == 'TYPE_WAYPOINT':
                waypoint.append([int(line_data[0]), float(line_data[2]), float(line_data[3])])

    acce, magn, ahrs, wifi, ibeacon, waypoint = np.array(acce), np.array(magn), np.array(ahrs), np.array(wifi), np.array(ibeacon), np.array(waypoint)

    if augmentation:
        augmented_data = compute_step_positions(acce, ahrs, waypoint) # use position estimation funciton in sample code compute_f.py
    else:
        augmented_data = waypoint

    index2data = [{'magn':[], 'wifi':defaultdict(list), 'ibeacon':defaultdict(list)} for _ in range(len(augmented_data))]
    index2time = augmented_data[:,0]
    for magn_data in magn: 
        tdiff = abs(index2time - magn_data[0])
        i = np.argmin(tdiff)
        index2data[i]['magn'].append((magn_data[1], magn_data[2], magn_data[3])) # 'magn': [(x1,y1,z1), (x2,y2,z2),...]
    for wifi_data in wifi:
        tdiff = abs(index2time - int(wifi_data[0]))
        i = np.argmin(tdiff)
        index2data[i]['wifi'][wifi_data[1]].append(int(wifi_data[2])) # 'wifi': {'id1':[-50, -20], 'id7':[-10]}
    for ibeacon_data in ibeacon:
        tdiff = abs(index2time - int(ibeacon_data[0]))
        i = np.argmin(tdiff)
        index2data[i]['ibeacon'][ibeacon_data[1]].append(int(ibeacon_data[2])) # 'wifi': {'id2':[-50, -24], 'id5':[-12,-30,-49]}

    txt_data = [None] * len(augmented_data)
    for index in range(len(index2time)):
        t, Px, Py = augmented_data[index]
        txt_data[index] = [t,Px,Py]
        magns, wifis, ibeacons = np.array(index2data[index]['magn']), index2data[index]['wifi'], index2data[index]['ibeacon'] 
        if len(magns) > 0:
            magn_mean = magns.mean(axis=0)
            magn_mean_intense = np.mean(np.sqrt(np.sum(magns**2, axis=1)))
            txt_data[index].extend(list(magn_mean) + [float(magn_mean_intense)])
        else:
            txt_data[index].extend([0,0,0,0])

        txt_data[index].append(defaultdict(lambda: -100))
        for bssid, rssis in wifis.items():
            txt_data[index][-1][bssid] = sum(rssis)/len(rssis)

        txt_data[index].append(defaultdict(lambda: -100))
        for uuid, rssis in ibeacons.items():
            txt_data[index][-1][uuid] = sum(rssis)/len(rssis)

    # returned format [(time, POSx, POSy, magnX, magnY, magnZ, magnIntense, {'BSSID4':rssi, 'BSSID7':rssi,..}, {'UUID2':rssi, 'UUID7':rssi,..}),...]
    return txt_data 


def split_floor_data(site, floor, testratio=0.1, augmentation=True): # (100 + rssi) / 100  ->  (0,1)
    file_path = os.path.join('../data', site, floor)
    file_list = os.listdir(os.path.join(file_path, "path_data_files"))

    total_posMagn_data = np.zeros((0, 6)).astype('float') # (Posx, Posy, MagnX, MagnY, MagnZ, MagnI)
    total_wifi_data = np.zeros((0,0)).astype('float') 
    total_ibeacon_data = np.zeros((0,0)).astype('float') 
    wifi_ibeacon_detected = np.zeros((0,2)).astype('float') # 记录这个时间点是否有对wifi和ibeacon有检测，没有记为0
    index2bssid = []
    bssid2index = dict()
    index2uuid = []
    uuid2index = dict()
    no_wifi_ibeacon = [0,0]
    not_in_train_wifi_ibeacon = [0,0]

    trajectory_data = np.zeros((0,9))
    curfilenum = 0 # Del
    for filename in file_list:
        curfilenum += 1 # Del
        if curfilenum % 10 == 0: # Del
            print(f'already read {curfilenum} txts') # Del
        txtname = os.path.join(file_path, "path_data_files", filename)
        trajectory_data = np.append(trajectory_data, np.array(get_data_from_one_txt(txtname, augmentation=augmentation)), axis=0)
    
    total_posMagn_data = trajectory_data[:, 1:7].astype('float')
    data_number = total_posMagn_data.shape[0]
    test_number = int(testratio * data_number)
    train_number = data_number - test_number
    test_indices = random.sample(range(data_number), test_number)
    train_indices = list(set(range(data_number)).difference(test_indices))
    finish_number = 0

    # add train data the total data
    for index in train_indices:
        # add one instance to total_data
        finish_number += 1 
        if finish_number % 500 == 0:
            print(f'data processing ... {finish_number}/{data_number}')
        tdata = trajectory_data[index]
        wifi_ibeacon_detected = np.concatenate((wifi_ibeacon_detected, np.zeros((1, 2))), axis=0)
        total_wifi_data = np.concatenate((total_wifi_data, np.zeros((1,total_wifi_data.shape[1]))), axis=0)
        total_ibeacon_data = np.concatenate((total_ibeacon_data, np.zeros((1,total_ibeacon_data.shape[1]))), axis=0)

        wifidic = tdata[7]
        if wifidic:
            wifi_ibeacon_detected[-1][0] = 1
        else: 
            no_wifi_ibeacon[0] += 1 
        for bssid, rssi in wifidic.items():
            if bssid not in bssid2index: # for train set, if a bssid did not appear before, we should add it to a new feature.
                bssid2index[bssid] = len(index2bssid)
                index2bssid.append(bssid)
                total_wifi_data = np.concatenate((total_wifi_data, np.zeros((total_wifi_data.shape[0], 1))), axis=1) # add a new feature
            total_wifi_data[-1][bssid2index[bssid]] = (100 + rssi) / 100

        ibeacondic = tdata[8]
        if ibeacondic:
            wifi_ibeacon_detected[-1][1] = 1
        else: 
            no_wifi_ibeacon[1] += 1 
        for uuid, rssi in ibeacondic.items():
            if uuid not in uuid2index: # for train set, if a uuid did not appear before, we should add it to a new feature.
                uuid2index[uuid] = len(index2uuid)
                index2uuid.append(uuid)
                total_ibeacon_data = np.concatenate((total_ibeacon_data, np.zeros((total_ibeacon_data.shape[0], 1))), axis=1) # new feature
            total_ibeacon_data[-1][uuid2index[uuid]] = (100 + rssi) / 100

    # add test data the total data
    for index in test_indices:
        # add one instance to total_data
        finish_number += 1 
        if finish_number % 500 == 0:
            print(f'data processing ... {finish_number}/{data_number}')
        tdata = trajectory_data[index]
        wifi_ibeacon_detected = np.concatenate((wifi_ibeacon_detected, np.zeros((1, 2))), axis=0)
        total_wifi_data = np.concatenate((total_wifi_data, np.zeros((1,total_wifi_data.shape[1]))), axis=0)
        total_ibeacon_data = np.concatenate((total_ibeacon_data, np.zeros((1,total_ibeacon_data.shape[1]))), axis=0)

        wifidic = tdata[7]
        if wifidic:
            wifi_ibeacon_detected[-1][0] = 1
        else: 
            no_wifi_ibeacon[0] += 1 
        for bssid, rssi in wifidic.items():
            if bssid in bssid2index: # For test data, we only caputure the bssid which appeared in the train data before.
                total_wifi_data[-1][bssid2index[bssid]] = (100 + rssi) / 100
            else:
                not_in_train_wifi_ibeacon[0] += 1


        ibeacondic = tdata[8]
        if ibeacondic:
            wifi_ibeacon_detected[-1][1] = 1
        else:
            no_wifi_ibeacon[1] += 1
        for uuid, rssi in ibeacondic.items():
            if uuid in uuid2index: # For test data, we only caputure the bssid which appeared in the train data before.
                total_ibeacon_data[-1][uuid2index[uuid]] = (100 + rssi) / 100
            else:
                not_in_train_wifi_ibeacon[1] += 1


    train_set = np.concatenate((total_posMagn_data[train_indices, :], wifi_ibeacon_detected[:train_number, :], \
                                total_wifi_data[:train_number, :], total_ibeacon_data[:train_number, :]), axis=1)
    test_set = np.concatenate((total_posMagn_data[test_indices, :], wifi_ibeacon_detected[train_number:, :], \
                                total_wifi_data[train_number:, :], total_ibeacon_data[train_number:, :]), axis=1)

    print(f'Total data instance: {data_number}, train number: {train_number}, test number: {test_number}')
    print()    
    print(f'There are {no_wifi_ibeacon[0]} steps that did not find wifi, and {no_wifi_ibeacon[1]} steps that did not find ibeacon.')
    print(f'There are {not_in_train_wifi_ibeacon[0]} bssids and {not_in_train_wifi_ibeacon[1]} uuids which were detected in testset while not detected in trainset, so that they were discard.')
    print(f'Final wifi bssid number: {len(index2bssid)}, ibeacon uuid number: {len(index2uuid)}')

    return train_set, test_set, [bssid2index, uuid2index]


# split_floor_data('site2', 'F4')



