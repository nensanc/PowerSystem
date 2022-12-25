
import numpy as np
import networkx as nx

def create_matrix(net):
    bus = [i for i in net.bus.index]
    lines = [[net.line.iloc[i][2], net.line.iloc[i][12]] for i in range(net.line.shape[0])] +\
            [[net.trafo.iloc[i][1], net.trafo.iloc[i][4]] for i in range(net.trafo.shape[0])]

    G = nx.DiGraph()
    G.add_nodes_from(bus)
    G.add_edges_from(lines)
    incidence_matrix = -nx.incidence_matrix(G, oriented=True) 
    # ^ this returns a scipy sparse matrix, can convert into the full array as below
    # (as long as your node count is reasonable: this'll have that squared elements)
    return incidence_matrix.toarray().T

def validate_clusters(d_cluster, matrix_conn):
    for key in d_cluster:
        vector = [int(i) for i in d_cluster.get(key)]
        sub_matrix = np.dot(matrix_conn[:,vector].T,matrix_conn[:,vector])
        _, r = np.linalg.qr(sub_matrix)
        
        if not(np.any(r)):
            return False
        index = np.where(abs(np.sum(r,axis=1)- r.diagonal())<1e-5)
        if (len(index)>1):
            return False
    return True