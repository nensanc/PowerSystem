
import pandapower as pp, pandapower.networks as pn
from pandas import DataFrame
import numpy as np
import skbio
from _source.dsbus_dv import dSbus_dV
from numpy.core.multiarray import array
from sklearn.cluster import KMeans
from sklearn_extensions.fuzzy_kmeans import FuzzyKMeans

# ruta de resultados
path = r'/home/lucy/Documentos/PandaPower/Resultados'

def save_csv(matrix, name, ind_col=None):
    '''
        Función que permite crear y guardar un dataframe
        input: 
            matrix: la matrix que se va a convertir en dataframe
            name: nombre para guardar el datafreme
            ind_col: índice y columna del dataframe
        return: 
            None
    '''
    if (ind_col):
        df = DataFrame(matrix, index=ind_col, columns=ind_col)
    else:
        df = DataFrame(matrix)    
    df.to_csv(path+'/'+name+'.csv', encoding='latin-1')

net = pn.case39()

# print(net._ppc["internal"].keys())  # get keys de losa datos respuesta
pp.runpp(net) # run pf

# get de internal results
Ybus = net._ppc["internal"]["Ybus"]
V = net._ppc["internal"]["V"]
pq = net._ppc["internal"]["pq"]
pv = net._ppc["internal"]["pv"]
ref = net._ppc["internal"]["ref"]

# create dS_dVm matrix 
dS_dVm, dS_dVa = dSbus_dV(Ybus, V)

# tomamos el orden de lso nodos del sistema
nodos = list(pq) + list(ref) + list(pv)
# creamos la matrix J22
J22 = dS_dVm[array([nodos]).T, array(nodos)].imag.todense()
J22 = dS_dVm[:].imag.todense()
# J22 = dS_dVm[array([pq]).T, pq].imag.todense()
save_csv(J22, 'J22') 

# invertimos la matrix J22
invJ22 = np.linalg.inv(J22)
save_csv(invJ22, 'invJ22') # guardamos la matrix

## Matriz de atenuaciones 
m_a = invJ22.copy()
for j in range(invJ22.shape[1]):
    m_a[:,j] = invJ22[:,j]/invJ22[j,j]
save_csv(m_a, 'm_a')

# Matriz de distancia
m_d = invJ22.copy()  
p=1e-6
for i in range(m_d.shape[0]):
    for j in range(m_d.shape[1]):
        if (-p<m_a[i,j]*m_a[j,i]<p):
            m_d[i,j] = 0.0
        else:
            m_d[i,j] = 1*np.log10(m_a[i,j]*m_a[j,i])
save_csv(m_d, 'm_d')

# # Cordenadas principales
PCoA = skbio.stats.ordination.pcoa(m_d, method="eigh", number_of_dimensions=2)
nodos = list(PCoA.samples[['PC1', 'PC2']].index)

## clusterin 
n_clusters = 6
#kmeans
kmeans = KMeans(n_clusters=n_clusters, random_state=1).fit(PCoA.samples[['PC1', 'PC2']])
labels_k = list(kmeans.labels_)

#fuzzy kmeans
fkmeans = FuzzyKMeans(k=n_clusters, m=2).fit(PCoA.samples[['PC1', 'PC2']])
labels_fk = list(fkmeans.labels_)
#centroids = fkmeans.cluster_centers_

# diccionario de clusterings kmeans
d_clusters_k = dict((i, []) for i in range(n_clusters))
for i,n in enumerate(nodos):
    d_clusters_k[labels_k[i]].append(n)
print("Clusters KMeans",d_clusters_k)

# diccionario de clusterings fuzzy kmeans
d_clusters_fk = dict((i, []) for i in range(n_clusters))
for i,n in enumerate(nodos):
    d_clusters_fk[labels_fk[i]].append(n)

print("Clusters Fuzzy KMeans",d_clusters_fk)