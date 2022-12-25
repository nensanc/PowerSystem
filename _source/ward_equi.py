
import pandapower as pp, pandapower.networks as pn


net = pn.case39()


# names = ["bus",
# "load",
# "gen",
# "ext_grid",
# "line",
# "trafo",
# "poly_cost",
# "bus_geodata"]

# #ward = pp.create_ward(net, 2, 50, 20, 50, 20)
# path = r'/home/lucy/Documentos/Git-Hub/PowerSystem/files'
# for name in names:
#     net.get(name).to_csv(f'{path}/{name}.csv')   

print(net)