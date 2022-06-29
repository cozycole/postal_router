import networkx as nx
import graphviz as gv
import matplotlib as plt


plt.figure(figsize=(14, 10))

visit_colors = {1:'lightgray', 2:'blue'}

fp = open("graph_output.csv", 'r')
line = fp.readline()
temp = line.split(',')
n = temp[0]
edge_list = []
for i in range(n):
    line = fp.readline()
    temp = line.split(',')
    edge = [int(temp[0]), int(temp[1]), int(temp)]

