import pandapower.networks as pp_net
import pandapower as pp
import numpy as np

class GetVariablesSystem(object):
    '''
        Class encargada de manejar las ecuaciones del flujo de carga
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
        if system=='ieee57':
            self.system = pp_net.case57()
        elif system=='ieee118':
            self.system = pp_net.case118()
        else:
            self.system = None
        pp.runpp(self.system)
        self.voltage = dict(
                        (i, self.system.bus['vn_kv'].values[i]) 
                        for i in range(self.system.bus.shape[0])
                        )
        if self.print_sec: print(f'Se crea el objeto del sistema a trabajar {system}')
    def _get_param_from_system(self):
        '''
            Está función entrega los parámetros del sistema necesarias en el modelo de optimización
            input
                self
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
        bounds_theta = {}
        for c in range(self.system.res_line.shape[0]):
            row = self.system.line.iloc[c]
            res_row = self.system.res_line.iloc[c]
            bounds_theta[(row['from_bus'], row['to_bus'], c)]\
                = res_row['va_from_degree']*np.pi/180
            bounds_theta[(row['to_bus'], row['from_bus'], c)]\
                = res_row['va_to_degree']*np.pi/180
        return {'i':buses,
                'j':buses,
                'c':list(self.system.line.index.values),
                'buses': buses,
                'bounds_bus':bounds_bus,
                'bounds_theta': bounds_theta}
    def _get_branchstatus(self):
        '''
            Está función entrega el estado de las líneas, si están operativas o no.
            input
                self
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
                self
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
    def _get_ratio(self):
        '''
            Está función entrega los mva de la líneas 
            input
                self
            return
                ratio: valores de capacidad máxima de las líneas
        '''
        if self.print_sec: print('Se crea la variable ratio')
        ratio = {}
        for c in range(self.system.line.shape[0]):
            row = self.system.line.iloc[c]
            ratio[(row['from_bus'], row['to_bus'], c)]\
                = row['max_i_ka']*self.voltage.get(int(row['from_bus']))
            ratio[(row['to_bus'], row['from_bus'], c)]\
                = row['max_i_ka']*self.voltage.get(int(row['from_bus']))
        return ratio
