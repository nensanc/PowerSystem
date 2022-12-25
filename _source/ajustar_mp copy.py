
from pandas import read_csv
import pandapower as pp, pandapower.networks as pn

path = r'D:\Documentos\Maestría\Tesis\Pandapower'
name = '24horas'
df_data = read_csv(path+'\\'+name+'.csv', sep=',')


net = pn.case39()

for p in range(1, 25):
    # p = 2 # periodo a evalaur
    print('Periodo: %s'%p)
    net.gen.iloc[:,4] = net.gen.iloc[:,4]*df_data['scaling'][p-1]
    net.load.iloc[:,6] = net.load.iloc[:,6]*df_data['scaling'][p-1]
    net.load.iloc[:,7] = net.load.iloc[:,7]*df_data['scaling'][p-1]

    pp.runpp(net)
    print(net.res_gen)