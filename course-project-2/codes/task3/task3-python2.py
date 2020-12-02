import os
import csv
from fmm import FastMapMatch,Network,NetworkGraph,UBODTGenAlgorithm,UBODT,FastMapMatchConfig
from fmm import Network,NetworkGraph,STMATCH,STMATCHConfig

network = Network("./data/Porto/edges.shp","fid", "u", "v")
print "Nodes {} edges {}".format(network.get_node_count(),network.get_edge_count())
graph = NetworkGraph(network)


if os.path.isfile("./data/Porto/ubodt.txt"):
    ubodt = UBODT.read_ubodt_csv("./data/Porto/ubodt.txt")
    print 'read the ubodt file'
else:
    print 'generate and read the ubodt file'
    ubodt_gen = UBODTGenAlgorithm(network,graph)
    status = ubodt_gen.generate_ubodt("./data/Porto/ubodt.txt", 0.03, binary=False, use_omp=True)
    print status
    ubodt = UBODT.read_ubodt_csv("./data/Porto/ubodt.txt")

fmm_model = FastMapMatch(network,graph,ubodt)
k = 16
radius = 0.005
gps_error = 0.0005
fmm_config = FastMapMatchConfig(k,radius,gps_error)

stmatch_model = STMATCH(network,graph)
k = 8
gps_error = 0.0005
radius = 0.005
vmax = 0.0003
factor = 1.5
stmatch_config = STMATCHConfig(k, radius, gps_error, vmax, factor)

train1000 = []
with open("./data/train-1000.csv","r") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        train1000.append(line[8]) #POLYLINES

results = []
for t_number in range(1,1001):
    gps_points = eval(train1000[t_number])
    wkt = 'LINESTRING('+','.join([' '.join([str(j) for j in i]) for i in gps_points])+')'
    result = fmm_model.match_wkt(wkt, fmm_config)
    if list(result.cpath)==[]:
        print('stmatching')
        result = stmatch_model.match_wkt(wkt, stmatch_config)
    candidates = list(result.candidates)
    results.append(dict(
        cpath=str(list(result.cpath)), mgeom=result.mgeom.export_wkt(), opath=str(list(result.opath)),
        offset=str([c.offset for c in candidates]), length=str([c.length for c in candidates]),
        spdist=str([c.spdist for c in candidates])
        ))

# cpath, opath, offset, length, spdist, mgeom
with open("./data/match_result.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["t_number", "cpath", "opath", "offset", "length", "spdist", "mgeom"])

    write_list = []
    for t_number in range(1000):
        tr = results[t_number]
        write_list.append([t_number+1, tr['cpath'], tr['opath'], tr['offset'], tr['length'], tr['spdist'], tr['mgeom']])
    writer.writerows(write_list)
