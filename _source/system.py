import pandapower.networks as pp_net
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
                system: nombre del sistema en pandapower ieee57 o ieee118
                print_sec: para imprimir secuencia de ejecuciones
            return\n
                Objeto de tipo system
        '''
        self.print_sec = print_sec
        self.model_name = f'--- Model -> {system} ---'
        if system=='ieee57':
            self.system = pp_net.case57()
            self.system.line.iloc[:, 6] = self.system.line.iloc[:, 6]/100
            self.system.bus.iloc[:, 1] = 1.1
            self.system.bus.iloc[:, 2] = 0.8
        elif system=='ieee118':
            self.system = pp_net.case118()
        else:
            self.system = None
        self.voltage = dict(
                        (i, self.system.bus['vn_kv'].values[i]) 
                        for i in range(self.system.bus.shape[0])
                        )
        self.scaling = {1:.63, 2:.62, 3:.6, 4:.58, 5:.59, 6:.65, 7:.72, 8:.85, 
                        9:.95, 10:.99, 11:1, 12:.99, 13:.93, 14:.92, 15:.9,16:.88, 
                        17:.9, 18:.9, 19:.96, 20:.98, 21:.96, 22:.9, 23:.8, 24:.7 }
        if self.print_sec: print(f'Se crea el objeto del sistema a trabajar * {system} *')
    def _get_param_from_system(self):
        '''
            Está función entrega los parámetros del sistema necesarias en el modelo de optimización
            input
                None
            return
                dict: diccionario que contiene los parámetros del sistema, i, j , c, buses, bounds. 
        '''
        if self.print_sec: print('Se obtienen la variables del sistema')
        buses, bounds_bus = [], {}
        for b in range(self.system.bus.shape[0]):
            row = self.system.bus.iloc[b]
            buses.append(int(row['name'])-1)
            for t in range(1, 25):
                bounds_bus[(int(row['name'])-1, t)] = (row['min_vm_pu'], row['max_vm_pu'])
        Pd, Qd, gen_bound_p, gen_bound_q = {}, {}, {}, {}
        for t in range(1,25):
            for i in range(self.system.load.shape[0]):
                row = self.system.load.iloc[i]
                Pd[(t,row['bus'])] = row['p_mw']*self.scaling[t]
                Qd[(t,row['bus'])] = row['q_mvar']*self.scaling[t]
            for i in range(self.system.gen.shape[0]):
                row = self.system.gen.iloc[i]
                gen_bound_p[(i, t)] = (row['min_p_mw'], row['max_p_mw'])
                gen_bound_q[(i, t)] = (row['min_q_mvar'], row['max_q_mvar'])
        atBus = {}
        for gen,bus in enumerate(list(self.system.gen['bus'])):
            atBus[(gen,bus)] = True
        return {'i':buses,
                'j':buses,
                'c':list(self.system.line.index.values),
                'Pd': Pd,
                'Qd': Qd,
                'buses': buses,
                'bounds_bus':bounds_bus,
                'atBus': atBus,
                'demandbid': list(self.system.load.index.values),
                'gen':list(self.system.gen.index.values),
                'gen_bound_p': gen_bound_p,
                'gen_bound_q': gen_bound_q,
                'model_name': self.model_name,
                }
    def _get_values_from_system(self):
        '''
            Está función entrega los valores calculados del sistema necesarias en el modelo de optimización
            input
                None
            return
                dict: diccionario que contiene los parámetros del sistema, i, j , c, buses, bounds. 
        '''
        if self.print_sec: print('Se obtienen la valores del sistema')
        init_bus_v, init_bus_theta = {},{}
        buses_line = list(
                        zip(
                            list(self.system.line['from_bus']), 
                            list(self.system.line['to_bus'])
                            )
                        )
        init_line_p, init_line_q = {},{}
        init_gen_p, init_gen_q = {},{}
        for t in range(1,25):
            self.system.gen.iloc[:,4] = self.system.gen.iloc[:,4]*self.scaling.get(t)
            self.system.load.iloc[:,6] = self.system.load.iloc[:,6]*self.scaling.get(t)
            self.system.load.iloc[:,7] = self.system.load.iloc[:,7]*self.scaling.get(t)
            pp.runpp(self.system)
            for i in range(self.system.res_bus.shape[0]):
                row = self.system.res_bus.iloc[i]
                init_bus_v[(i, t)] = row['vm_pu']
                init_bus_theta[(i, t)] = row['va_degree']*np.pi/180
            c_line = 0
            for i,j in buses_line:
                row = self.system.res_line.iloc[c_line]
                init_line_p[i,j,c_line,t] = row['p_from_mw']
                init_line_p[j,i,c_line,t] = row['p_to_mw']
                init_line_q[i,j,c_line,t] = row['q_from_mvar']
                init_line_q[j,i,c_line,t] = row['q_to_mvar']
                c_line+=1
            c_gen = 0
            for p, q in list(zip(list(self.system.res_gen['p_mw']),
                            list(self.system.res_gen['q_mvar']))):
                init_gen_p[(c_gen, t)] = p
                init_gen_q[(c_gen, t)] = q
        return {
                'init_bus_theta': init_bus_theta,
                'init_bus_v': init_bus_v,
                'init_line_p': init_line_p,
                'init_line_q': init_line_q,
                'init_gen_p': init_gen_p,
                'init_gen_q': init_gen_q
                }
    def _get_branchstatus(self):
        '''
            Está función entrega el estado de las líneas, si están operativas o no.
            input
                None
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        if self.print_sec: print('Se crea la variable de branchstatus')
        branchstatus = {}
        c_line = 0
        buses_line = list(
                        zip(
                            list(self.system.line['from_bus']), 
                            list(self.system.line['to_bus'])
                            )
                        )
        for i,j in buses_line:
            branchstatus[(i, j, c_line)] = True
            branchstatus[(j, i, c_line)] = True
            c_line +=1
        return branchstatus
    def _get_conductance_susceptance(self):
        '''
            Está función entrega el calculo de la conductance y la susceptance.
            input
                None
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        if self.print_sec: print('Se crea las variables de conductance y susceptance')
        g, b = {}, {}
        def calculate_g_b(tipe, d, r, x):
                return d*(r if tipe=='g' else -x)/(np.power(r,2) + np.power(x,2))
        for c in range(self.system.line.shape[0]):
            row = self.system.line.iloc[c]
            value_g = calculate_g_b(
                    'g',
                     row['length_km'],
                     row['r_ohm_per_km'],
                     row['x_ohm_per_km']
                    )
            g[(row['from_bus'], row['to_bus'], c)]\
                = value_g
            g[(row['to_bus'], row['from_bus'], c)]\
                = value_g
            value_b = calculate_g_b(
                    'b',
                     row['length_km'],
                     row['r_ohm_per_km'],
                     row['x_ohm_per_km']
                    )
            b[(row['from_bus'], row['to_bus'], c)]\
                = value_b
            b[(row['to_bus'], row['from_bus'], c)]\
                = value_b
        return g, b
    def _get_ratio_line(self):
        '''
            Está función entrega los mva de la líneas 
            input
                None
            return
                ratio: valores de capacidad máxima de las líneas
        '''
        if self.print_sec: print('Se crea la variable ratio líneas')
        ratio = {}
        for c in range(self.system.line.shape[0]):
            row = self.system.line.iloc[c]
            ratio[(row['from_bus'], row['to_bus'], c)]\
                = row['max_i_ka']*self.voltage.get(int(row['from_bus']))
            ratio[(row['to_bus'], row['from_bus'], c)]\
                = row['max_i_ka']*self.voltage.get(int(row['from_bus']))
        return ratio
    def _get_ratio_trafo(self):
        '''
            Está función entrega los tap de los trafos
            input
                None
            return
                ratio: valores de taps de los trafos
        '''
        if self.print_sec: print('Se crea la variable ratio trafos')
        ratio = {}
        for c in range(self.system.line.shape[0]):
            row = self.system.line.iloc[c]
            ratio[(row['from_bus'], row['to_bus'], c)] = 1
            ratio[(row['to_bus'], row['from_bus'], c)] = 1
        return ratio
    def _get_genstatus(self):
        '''
            Está función entrega el estado de generadores, si están operativas o no.
            input
                None
            return
                genstatus: diccionario que contiene el estado de los generadores g
                                genstatus(gen)
        '''
        if self.print_sec: print('Se crea la variable de genstatus')
        return dict(((bus, gen), True) for gen,bus in enumerate(list(self.system.gen['bus'])))
    def _get_demandbidmap(self):
        '''
            Está función entrega el id de la demanda y su nodo de conexión
            input
                None
            return
                demandbidmap: diccionario que contiene la el id de la demanda y el nodo de conexión
                                demandbidmap(load_id, bus)
        ''' 
        if self.print_sec: print('Se crea la variable de demandbidmap')
        return dict(((load_id, bus), True) for load_id,bus in enumerate(list(self.system.load['bus'])))