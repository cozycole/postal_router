import codecs
import osm2geojson
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

""" with codecs.open('qgis_streetsv2.osm', 'r', encoding='utf-8') as data:
    xml = data.read()
# dict with all nodes and ways
geojson = osm2geojson.xml2geojson(xml, filter_used_refs=False, log_level='INFO') """

"""
File Format
===========
# vertices, # edges
source, target, cost, oneway, st_name
"""
conn = psycopg2.connect(f'dbname={os.getenv("DATABASE")} user={os.getenv("DB_USER")}')
cur = conn.cursor()

cur.execute("SELECT source, target, length_m, oneway, name FROM ways;")
ways = [list(edge) for edge in cur.fetchall()]
# print(ways)

cur.execute("SELECT id, row_num FROM ways_vertices_pgr ORDER BY id ASC")
vertices = [list(vert) for vert in cur.fetchall()]

for i, vert in enumerate(vertices):
    # java code has it 1 indexed for vert labels
    vert[1] = i + 1


# Goal here is to renumber the source and target
# based on the new ascending vertex ids (i.e. their row number)
# This is done since vertex ids need to be ascending from 1, and when
# cleaning the data, some vertices are removed
for i, edge in enumerate(ways):
    new_source = None
    new_target = None
    one_way = 1 if edge[3] == 'YES' else 0
    for vert in vertices:
        if edge[0] == vert[0]:
            new_source = vert[1]
        if edge[1] == vert[0]:
            new_target = vert[1]
    ways[i] = [new_source, new_target, int(edge[2]), one_way, edge[4]]

# f = open("graph_output.csv", 'w')
# f.write(f"{len(vertices)},{len(ways)}\n")
# for edge in ways:
#     f.write(f"{edge[0]},{edge[1]},{edge[2]},{edge[3]},{edge[4]}\n")

# f.close()

# This is to get directions based on the path

np = open("node_path.txt", 'r')
pd = open("path_directions.txt", 'w')

line = np.readline()
temp = line.split('-')
temp_len = len(temp)
prev_edge = None
edge_list = []
deadhead_sum = 0
for i, s in enumerate(temp):
    if temp_len == i + 1:
        break
    source = int(s)
    target = int(temp[i+1])
    curr_edge = None
    for edge in ways:
        if edge[0] in (source, target) and edge[1] in (source, target):
            curr_edge = edge
    
    if curr_edge in edge_list and prev_edge == curr_edge:
        pd.write("DEA  DHEAD: ")
        deadhead_sum += curr_edge[2]
    edge_list.append(curr_edge)

    if i == 0:
        pd.write(f"Start on {curr_edge[4]}\n")
    elif prev_edge == curr_edge:
        # if target = source and source = target 
        pd.write(f"U-turn out of {curr_edge[4]}\n")
    elif prev_edge[4] == curr_edge[4]:
        # if street name is the same
        pd.write(f"Continue on {curr_edge[4]}\n")
    else:
        pd.write(f"Turn on to {curr_edge[4]}\n")
    prev_edge = curr_edge
pd.write(f"DEADHEAD SUM: {deadhead_sum}")


cur.close()
conn.close()