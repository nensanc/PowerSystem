
import pandapower as pp, pandapower.networks as pn
from pandas import read_excel, DataFrame
import numpy as np
from sklearn.decomposition import PCA

path = r'D:\Documentos\Maestría\Tesis\Pandapower'
name = 'businfo'
df_load = read_excel(path+'\\'+name+'.xlsx')
name = 'geninfo'
df_gen = read_excel(path+'\\'+name+'.xlsx')

def save_csv(matrix, name):
    df = DataFrame(matrix)
    df.to_csv(path+'\\'+name+'.csv')

net = pn.case39()


# net.gen.iloc[:,4] = df_gen['P_6']
# net.load.iloc[:,6] = df_load['P_6']
# net.load.iloc[:,7] = df_load['Q_6']


pp.runpp(net)

J = net._ppc["internal"]["J"].todense()
save_csv(J, 'J')
invJ = np.linalg.inv(J)
save_csv(invJ, 'invJ')
# get pv and pq values from newtonpf()
pv = net._ppc["internal"]["pv"]
pq = net._ppc["internal"]["pq"]
# stack these as done in newtonpf()
pvpq = np.hstack((pv, pq))

# print("pv and pq nodes as in the newtonpf() function")
# print(f"pv buses: {pv}\npq buses: {pq}\npvpq buses: {pvpq}")

# get len of pv and pq
n_pvpq = len(pvpq)
# get J11, J12, J21, and J22
# j22 = J[n_pvpq:, n_pvpq:]
# invJ22 = np.linalg.inv(j22)
invJ22 = invJ[n_pvpq:, n_pvpq:]
save_csv(invJ22, 'invJ22')
# print(f"j22 = {invJ22.shape}")
# print(invJ22)

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
            m_d[i,j] = -1*np.log10(m_a[i,j]*m_a[j,i])
save_csv(m_d, 'm_d')
# Matriz de distnacias normalizada
p=1e-10
m_d_n = m_d.copy()
for i in range(m_d.shape[0]):
    for j in range(m_d.shape[1]):
        if not(-p<np.amax(m_d[i,:])<p):
            if not(-p<m_d[i,j]<p):
                m_d_n[i,j] = m_d[i,j]/np.amax(m_d[i,:])
save_csv(m_d_n, 'm_d_n')

# # Componentes principales
# pca = PCA(n_components=10)
# cp = pca.fit(np.asarray(m_d_n))
# print(cp.singular_values_)