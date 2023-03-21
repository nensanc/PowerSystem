import pandapower.networks as pp_net
from pandapower.grid_equivalents import get_equivalent
import pandapower as pp
import numpy as np

class GetVariablesSystem(object):
    '''
        Class encargada de obtener las ecuaciones del flujo de carga
    '''
    def __init__(self, system, print_sec=False):
        '''
            Está función instancia la clase system, para obtener los parámetros y variables del sistema\n
            input\n
                system: nombre del sistema en pandapower ieee9, ieee39, ieee57 o ieee118
                print_sec: para imprimir secuencia de ejecuciones
            return\n
                Objeto de tipo system
        '''
        self.print_sec = print_sec
        self.model_name = f'--- Model -> {system} ---'
        self.system_name = system
        if self.system_name=='ieee9':
            self.system = pp_net.case9()
            self.bus_shunt = [6,8,4]
            self.pilot_nodes = [i for i in range(9)]
            self.sep_areas = {  1:{
                                    'name':'A1','border_node':[6, 8],'internal_node':[7]
                                },
                                2:{
                                    'name':'A2','border_node':[6, 8],'internal_node':[5]
                                }
                            }
        elif self.system_name=='ieee39':
            self.system = pp_net.case39()
            self.bus_shunt = [14,2,22,25]
            self.pilot_nodes = [1,25,7,5,22,18]
            self.sep_areas = {  1:{
                                    'name':'A1','border_node':[38, 2, 16],'internal_node':[25]
                                },
                                2:{
                                    'name':'A2','border_node':[38, 2, 13],'internal_node':[4]
                                },
                                3:{
                                    'name':'A3','border_node':[16, 13],'internal_node':[22]
                                }
                            }
        elif self.system_name=='ieee57':
            self.system = pp_net.case57()
            self.bus_shunt = [22,34,24,52,29,30]
            self.pilot_nodes = [0,3,9,11,12,21,28,30,35,40,47]
        elif self.system_name=='ieee118':
            self.system = pp_net.case118()
            self.bus_shunt = [51,50,21,56,78]
            self.pilot_nodes = [68,4,36,55,76,65,45,22,11,69,16,62,79,7,48,31]
        else:
            self.system = None
        self.voltage = dict(
                        (i, self.system.bus['vn_kv'].values[i]) 
                        for i in range(self.system.bus.shape[0])
                        )
        self.scaling = {1:.63, 2:.62, 3:.6, 4:.58, 5:.59, 6:.65, 7:.72, 8:.85, 
                        9:.95, 10:.99, 11:1, 12:.99, 13:.93, 14:.92, 15:.9,16:.88, 
                        17:.9, 18:.9, 19:.96, 20:.98, 21:.96, 22:.9, 23:.8, 24:.7 }
        self.multiplier = 1.15
        self.sn_mva = self.system.sn_mva
        self.system.bus.iloc[:, list(self.system.bus.columns).index('max_vm_pu')] = 1.1
        self.system.bus.iloc[:, list(self.system.bus.columns).index('min_vm_pu')] = 0.9
        self.id_load_p = list(self.system.load.columns).index('p_mw')
        self.id_load_q = list(self.system.load.columns).index('q_mvar')
        self.id_gen_p = list(self.system.gen.columns).index('p_mw')
        if self.print_sec: print(f'Se crea el objeto del sistema a trabajar * {system} *')
    def _get_ward_eq_from_system(self, area):
        '''
            Está función entrega el equivalente ward del sitema
            input
                None
            return
                net_eq: sistema equivalante
        '''
        self.border_node = self.sep_areas.get(area).get('border_node')
        net_eq = get_equivalent(self.system, 'ward', 
                                    self.sep_areas.get(area).get('border_node'), 
                                    self.sep_areas.get(area).get('internal_node'),
                                )
        self.ward_borders_p, self.ward_borders_q = {},{}
        for i in range(net_eq.ward.shape[0]):
            row = net_eq.ward.iloc[i]
            res_row = net_eq.res_ward.iloc[i]
            if int(row['bus']) in self.border_node:
                self.ward_borders_p[(str(row['bus']))] = res_row['p_mw']
                self.ward_borders_q[(str(row['bus']))] = res_row['q_mvar']
        return net_eq
    def _get_param_from_system(self, system_area):
        '''
            Está función entrega los parámetros del sistema necesarias en el modelo de optimización
            input
                None
            return
                dict: diccionario que contiene los parámetros del sistema, i, j , c, buses, bounds. 
        '''
        if self.print_sec: print('Se obtienen la variables del sistema')
        slack_bound_p, slack_bound_q, bounds_bus = {}, {}, {}
        for t in range(1,25):
            for i in range(system_area.ext_grid.shape[0]):
                row = system_area.ext_grid.iloc[i]
                slack_bound_p[(str(i), t)] = (row['min_p_mw']/self.sn_mva, 
                                              row['max_p_mw']/self.sn_mva)
                slack_bound_q[(str(i), t)] = (row['min_q_mvar']/self.sn_mva, 
                                              row['max_q_mvar']/self.sn_mva)
            for bus in range(system_area.bus.shape[0]):
                row = system_area.bus.iloc[bus]
                bounds_bus[(str(bus), t)] = (row['min_vm_pu'], row['max_vm_pu'])
        atBus = {}
        for gen,bus in enumerate(list(system_area.gen['bus'])):
            atBus[(str(gen),bus)] = True
        atBusSlack = {}
        for gen,bus in enumerate(list(system_area.ext_grid['bus'])):
            atBusSlack[(str(gen),bus)] = True
        list_i,ij, ji, branchij_bus, branchji_bus = [],[],[],{},{}
        for i, j in list(zip(list(system_area.line['from_bus']),
                            list(system_area.line['to_bus']))):
            if not str(i) in list_i: 
                list_i.append(str(i))
            ij.append(f'{i}-{j}') 
            ji.append(f'{j}-{i}')
            if branchij_bus.get(str(i)):
                branchij_bus[str(i)].append(f'{i}-{j}')
            else:
                branchij_bus[str(i)] = [f'{i}-{j}']
            if branchji_bus.get(str(j)):
                branchji_bus[str(j)].append(f'{j}-{i}')
            else:
                branchji_bus[str(j)] = [f'{j}-{i}']
        bus_trafo = {}
        for bus in list(self.system.trafo['hv_bus']):
            bus_trafo[str(bus)] = True
        bus_load = {}
        for bus in list(system_area.load['bus']):
            bus_load[str(bus)] = True
        ward_bus = {}
        for bus in list(self.border_node):
            ward_bus[str(bus)] = True
        bus_shunt = {}
        for bus in self.bus_shunt:
            if bus in self.border_node:
                bus_shunt[str(bus)] = True
        self.system_param = {
                'ij':ij,
                'ji':ji,
                'i': list_i,
                'branchij_bus': branchij_bus,
                'branchji_bus': branchji_bus,
                'bus': [str(bus-1) for bus in list(system_area.bus['name'])],
                'bus_trafo': bus_trafo,
                'bus_load': bus_load,
                'bounds_bus':bounds_bus,
                'atBus': atBus,
                'ward_bus': ward_bus,
                'atBusSlack': atBusSlack,
                'demandbid': [str(bus) for bus in list(system_area.load['bus'])],
                'gen':[str(gen) for gen in list(system_area.gen['bus'])],
                'slack':[str(gen) for gen in list(system_area.ext_grid['bus'])],
                'slack_bound_p': slack_bound_p,
                'slack_bound_q': slack_bound_q,
                'model_name': self.model_name,
                'system_name': self.system_name,
                'bus_shunt': bus_shunt,
                'pilot_nodes': dict((str(node), True) for node in self.pilot_nodes),
            }
        return self.system_param
    def _get_values_from_system(self, area):
        '''
            Está función entrega los valores calculados del sistema necesarias en el modelo de optimización
            input
                None
            return
                dict: diccionario que contiene los parámetros del sistema, i, j , c, buses, bounds. 
        '''
        if self.print_sec: print('Se obtienen la valores del sistema')
        init_bus_v, init_bus_theta = {},{}
        init_line_pij, init_line_qij, init_line_pji, init_line_qji = {},{},{},{}
        bound_line_pij, bound_line_pji = {}, {} 
        init_slack_p, init_slack_q = {},{}
        init_gen_p, init_gen_q, gen_bound_q = {},{},{}
        Pd, Qd = {}, {}
        bus_ward_p, bus_ward_q = {},{}
        load_init_p = list(self.system.load.iloc[:,self.id_load_p])
        load_init_q = list(self.system.load.iloc[:,self.id_load_q])
        gen_init_p = list(self.system.gen.iloc[:,self.id_gen_p])
        for t in range(1,25):
            self.system.gen.iloc[:,self.id_gen_p] = list(np.array(gen_init_p)*self.scaling.get(t)*self.multiplier)
            self.system.load.iloc[:,self.id_load_p] = list(np.array(load_init_p)*self.scaling.get(t)*self.multiplier)
            self.system.load.iloc[:,self.id_load_q] = list(np.array(load_init_q)*self.scaling.get(t)*self.multiplier)
            system_eq = self._get_ward_eq_from_system(area)
            for i in range(system_eq.res_load.shape[0]):
                row = system_eq.load.iloc[i]
                res_row = system_eq.res_load.iloc[i]
                Pd[(str(row['bus']),t)] = res_row['p_mw']/self.sn_mva
                Qd[(str(row['bus']),t)] = res_row['q_mvar']/self.sn_mva
            for i in range(system_eq.res_bus.shape[0]):
                res_row = system_eq.res_bus.iloc[i]
                row = system_eq.bus.iloc[i]
                init_bus_v[(str(row['name']-1), t)] = res_row['vm_pu']
                init_bus_theta[(str(row['name']-1), t)] = res_row['va_degree']*np.pi/180
            c_line = 0
            for i,j in list(zip(list(system_eq.line['from_bus']), 
                            list(system_eq.line['to_bus']))):
                row = system_eq.res_line.iloc[c_line]
                p_from = row['p_from_mw']/self.sn_mva
                p_to = row['p_to_mw']/self.sn_mva
                init_line_pij[(f'{i}-{j}',t)] = p_from
                init_line_pji[(f'{j}-{i}',t)] = p_to
                bound_line_pij[(f'{i}-{j}',t)] = (0.9*p_from, 1.1*p_from) if p_from>0 else (1.1*p_from, 0.9*p_from)
                bound_line_pji[(f'{j}-{i}',t)] = (0.9*p_to, 1.1*p_to) if p_to>0 else (1.1*p_to, 0.9*p_to)
                init_line_qij[(f'{i}-{j}',t)] = row['q_from_mvar']/self.sn_mva
                init_line_qji[(f'{j}-{i}',t)] = row['q_to_mvar']/self.sn_mva
                c_line+=1
            c_gen = 0
            gen_bus = list(system_eq.gen['bus'])
            for p, q in list(zip(list(system_eq.res_gen['p_mw']),
                            list(system_eq.res_gen['q_mvar']))):
                init_gen_p[(str(gen_bus[c_gen]), t)] = p/self.sn_mva
                init_gen_q[(str(gen_bus[c_gen]), t)] = q/self.sn_mva
                row = self.system.gen.iloc[c_gen]
                if q>0:
                    min_q = row['min_q_mvar'] if row['min_q_mvar']<q else q
                    max_q = row['max_q_mvar'] if row['max_q_mvar']>q else q
                else:
                    min_q = row['min_q_mvar'] if row['min_q_mvar']<q else q
                    max_q = row['max_q_mvar'] if row['max_q_mvar']>q else q
                gen_bound_q[(str(gen_bus[c_gen]), t)] = (min_q/self.sn_mva, 
                                            max_q/self.sn_mva)
                c_gen+=1
            c_gen=0
            gen_bus = list(system_eq.ext_grid['bus'])
            for p, q in list(zip(list(system_eq.res_ext_grid['p_mw']),
                            list(system_eq.res_ext_grid['q_mvar']))):
                init_slack_p[(str(gen_bus[c_gen]), t)] = p/self.sn_mva
                init_slack_q[(str(gen_bus[c_gen]), t)] = q/self.sn_mva
                c_gen+=1
            for bus, value in self.ward_borders_p.items():
                bus_ward_p[(str(bus),t)] = value/self.sn_mva
            for bus, value in self.ward_borders_q.items():
                bus_ward_q[(str(bus),t)] = value/self.sn_mva
        self.system_values = {
                'Pd': Pd,
                'Qd': Qd,
                'init_bus_theta': init_bus_theta,
                'init_bus_v': init_bus_v,
                'init_line_pij': init_line_pij,
                'init_line_qij': init_line_qij,
                'bound_line_pij': bound_line_pij,
                'bound_line_pji': bound_line_pji,
                'init_line_pji': init_line_pji,
                'init_line_qji': init_line_qji,
                'init_gen_p': init_gen_p,
                'init_gen_q': init_gen_q,
                'gen_bound_q': gen_bound_q,
                'init_slack_p': init_slack_p,
                'init_slack_q': init_slack_q,
                'bus_ward_p': bus_ward_p,
                'bus_ward_q': bus_ward_q
            }
        return self.system_values
    def _get_conductance_susceptance(self, system_area):
        '''
            Está función entrega el calculo de la conductance y la susceptance.
            input
                None
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        if self.print_sec: print('Se crea las variables de conductance y susceptance')
        self.g, self.b = {}, {}
        def calculate_g_b(tipe, d, r, x):
                return d*(r if tipe=='g' else -x)/(np.power(r,2) + np.power(x,2))
        for c in range(system_area.line.shape[0]):
            row = system_area.line.iloc[c]
            value_g = calculate_g_b(
                    'g',
                     row['length_km'],
                     row['r_ohm_per_km'] if row['r_ohm_per_km']!=0 else system_area.line['r_ohm_per_km'].mean(),
                     row['x_ohm_per_km'] if row['x_ohm_per_km']!=0 else system_area.line['x_ohm_per_km'].mean()
                    )
            i, j = row['from_bus'], row['to_bus']
            self.g[f'{i}-{j}'] = value_g
            self.g[f'{j}-{i}'] = value_g
            value_b = calculate_g_b(
                    'b',
                     row['length_km'],
                     row['r_ohm_per_km'] if row['r_ohm_per_km']!=0 else system_area.line['r_ohm_per_km'].mean(),
                     row['x_ohm_per_km'] if row['x_ohm_per_km']!=0 else system_area.line['x_ohm_per_km'].mean()
                    )
            self.b[f'{i}-{j}'] = value_b
            self.b[f'{j}-{i}'] = value_b
        return self.g, self.b
    def _get_ratio_line(self, system_area):
        '''
            Está función entrega los mva de la líneas 
            input
                None
            return
                ratio: valores de capacidad máxima de las líneas
        '''
        if self.print_sec: print('Se crea la variable ratio líneas')
        self.ratio_line = {}
        for c in range(system_area.line.shape[0]):
            row = system_area.line.iloc[c]
            i, j = row['from_bus'], row['to_bus']
            self.ratio_line[f'{i}-{j}']\
                = np.sqrt(3)*row['max_i_ka']*self.voltage.get(int(row['from_bus']))/self.sn_mva
        return self.ratio_line
    def _get_ratio_trafo(self, system_area):
        '''
            Está función entrega los tap de los trafos
            input
                None
            return
                ratio: valores de taps de los trafos
        '''
        if self.print_sec: print('Se crea la variable ratio trafos')
        self.ratio = {}
        for c in range(system_area.line.shape[0]):
            row = system_area.line.iloc[c]
            i, j = row['from_bus'], row['to_bus']
            self.ratio[f'{i}-{j}'] = 1
            self.ratio[f'{j}-{i}'] = 1
        return self.ratio
    def _get_genstatus(self, system_area):
        '''
            Está función entrega el estado de generadores, si están operativas o no.
            input
                None
            return
                genstatus: diccionario que contiene el estado de los generadores g
                                genstatus(gen)
        '''
        if self.print_sec: print('Se crea la variable de genstatus')
        self.genstatus = dict(((gen, bus), True) for gen,bus in enumerate(list(system_area.gen['bus'])))
        return self.genstatus
    def _get_demandbidmap(self, system_area):
        '''
            Está función entrega el id de la demanda y su nodo de conexión
            input
                None
            return
                demandbidmap: diccionario que contiene la el id de la demanda y el nodo de conexión
                                demandbidmap(load_id, bus)
        ''' 
        if self.print_sec: print('Se crea la variable de demandbidmap')
        self.demandbidmap = dict(((load_id, bus), True) for load_id,bus in enumerate(list(system_area.load['bus'])))
        return self.demandbidmap
    def _get_adjust_values(self):
        '''
            Está función entrega las variables de ajuste del modelo
            input
                None
            return
                dict: diccionario que contiene los ajustes de las ecuaciones de igualdad
        ''' 
        ## ajuste de la potencia aparente
        adj_slimit_sij = {}
        for t in range(1,25):
            for ij in self.system_param.get('ij'):
                s_v1 = (self.ratio_line[ij])**2
                s_v2 = (
                    self.system_values.get('init_line_pij')[ij, t]**2
                    + self.system_values.get('init_line_qij')[ij, t]**2      
                )
                signo_sij = -1 if (s_v1>0 and s_v2<0 or s_v1<0 and s_v2>0) else 1
                adj_slimit_sij[(ij,t)] = abs(s_v2/s_v1)*signo_sij
        ## ajuste de los flujos de potencia      
        adj_line_pij, adj_line_pji = {},{}
        adj_line_qij, adj_line_qji = {},{}
        for t in range(1,25):
            for ij in self.system_param.get('ij'):
                # para Pij
                p_v1 = (
                    (self.g[ij] * (self.system_values.get('init_bus_v')[ij.split('-')[0],t]**2) / 1**2)
                    - (self.system_values.get('init_bus_v')[ij.split('-')[0],t] * self.system_values.get('init_bus_v')[ij.split('-')[1],t] / 1)
                    * (self.g[ij] * np.cos(self.system_values.get('init_bus_theta')[ij.split('-')[0],t] - self.system_values.get('init_bus_theta')[ij.split('-')[1],t]) 
                    + self.b[ij] * np.sin(self.system_values.get('init_bus_theta')[ij.split('-')[0],t] - self.system_values.get('init_bus_theta')[ij.split('-')[1],t]))
                    )
                p_v2 = self.system_values.get('init_line_pij').get((ij,t))
                adj_line_pij[(ij,t)] = p_v1 - p_v2
                # para Qij
                q_v1 = (
                    - self.system_values.get('init_bus_v')[ij.split('-')[0],t]**2 * (self.b[ij]) / 1**2
                    - self.system_values.get('init_bus_v')[ij.split('-')[0],t] * self.system_values.get('init_bus_v')[ij.split('-')[1],t] /1 
                    * (self.g[ij] * np.sin(self.system_values.get('init_bus_theta')[ij.split('-')[0],t] - self.system_values.get('init_bus_theta')[ij.split('-')[1],t])
                    - self.b[ij] * np.cos(self.system_values.get('init_bus_theta')[ij.split('-')[0],t] - self.system_values.get('init_bus_theta')[ij.split('-')[1],t]))
                    )
                q_v2 = self.system_values.get('init_line_qij').get((ij,t))
                adj_line_qij[(ij,t)] = q_v1 - q_v2
            for ji in self.system_param.get('ji'):
                # para Pji
                p_v1 = (
                    (self.g[ji] * (self.system_values.get('init_bus_v')[ji.split('-')[0],t]**2) / 1**2)
                    - (self.system_values.get('init_bus_v')[ji.split('-')[0],t] * self.system_values.get('init_bus_v')[ji.split('-')[1],t] / 1)
                    * (self.g[ji] * np.cos(self.system_values.get('init_bus_theta')[ji.split('-')[0],t] - self.system_values.get('init_bus_theta')[ji.split('-')[1],t]) 
                    + self.b[ji] * np.sin(self.system_values.get('init_bus_theta')[ji.split('-')[0],t] - self.system_values.get('init_bus_theta')[ji.split('-')[1],t]))
                    )
                p_v2 = self.system_values.get('init_line_pji').get((ji,t))
                adj_line_pji[(ji,t)] = p_v1 - p_v2
                # para Qji
                q_v1 = (
                    - self.system_values.get('init_bus_v')[ji.split('-')[1],t]**2 * (self.b[ji])
                    - self.system_values.get('init_bus_v')[ji.split('-')[0],t] * self.system_values.get('init_bus_v')[ji.split('-')[1],t] / 1
                    * (self.g[ji] * np.sin(self.system_values.get('init_bus_theta')[ji.split('-')[1],t] - self.system_values.get('init_bus_theta')[ji.split('-')[0],t])
                    - self.b[ji] * np.cos(self.system_values.get('init_bus_theta')[ji.split('-')[1],t] - self.system_values.get('init_bus_theta')[ji.split('-')[0],t]))
                    )
                q_v2 = self.system_values.get('init_line_qji').get((ji,t))
                adj_line_qji[(ji,t)] = q_v1 - q_v2
        # para balance de potencia
        adj_p_balance, adj_q_balance = {}, {}
        for t in range(1,25):
            for bus in self.system_param.get('bus'):
                # para P
                p_b1 = (
                    sum(self.system_values.get('init_gen_p')[gen, t] for gen in self.system_param.get('gen') if self.system_param.get('atBus').get((gen,bus)) and self.genstatus.get((gen,bus)))
                    + sum(self.system_values.get('init_slack_p')[gen, t] for gen in self.system_param.get('slack') if self.system_param.get('atBusSlack').get((gen,bus)))
                    - (self.system_values.get('Pd').get((bus,t)) if self.system_values.get('Pd').get((bus,t)) else 0)
                    #- (self.system_values.get('bus_ward_p').get((bus,t)) if self.system_values.get('bus_ward_p').get((bus,t)) else 0)
                )
                p_b2 = (
                    sum(self.system_values.get('init_line_pij')[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                    + sum(self.system_values.get('init_line_pji')[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                    + self.system_values.get('init_bus_v')[bus,t]**2 
                )
                adj_p_balance[(bus,t)] = p_b1-p_b2
                # para Q
                q_b1 = (
                    sum(self.system_values.get('init_gen_q')[gen, t] for gen in self.system_param.get('gen') if self.system_param.get('atBus').get((gen,bus)) and self.genstatus.get((gen,bus)))
                    + sum(self.system_values.get('init_slack_q')[gen, t] for gen in self.system_param.get('slack') if self.system_param.get('atBusSlack').get((gen,bus)))
                    - (self.system_values.get('Qd').get((bus,t)) if self.system_values.get('Qd').get((bus,t)) else 0)
                    #- (self.system_values.get('bus_ward_q').get((bus,t)) if self.system_values.get('bus_ward_q').get((bus,t)) else 0)
                )
                q_b2 = (
                    sum(self.system_values.get('init_line_pij')[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                    + sum(self.system_values.get('init_line_pji')[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                    + self.system_values.get('init_bus_v')[bus,t]**2 
                )
                adj_q_balance[(bus,t)] = q_b1-q_b2
        return{
            'adj_line_pij': adj_line_pij,
            'adj_line_pji': adj_line_pji,
            'adj_line_qij': adj_line_qij,
            'adj_line_qji': adj_line_qji,
            'adj_slimit_sij': adj_slimit_sij,
            'adj_p_balance': adj_p_balance,
            'adj_q_balance': adj_q_balance          
        }