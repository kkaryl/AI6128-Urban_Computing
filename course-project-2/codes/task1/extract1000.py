templines = []
with open('../../data/train.csv', 'r') as f:
    for i in range(1001):
        templines.append(f.readline())

with open('../../data/train-1000.csv', 'w') as f:
    f.write(''.join(templines))


