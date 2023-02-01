import pandapower.networks as pp_net
import pandapower as pp
import numpy as np

class GetVariablesSystem(object):
    '''
        Class encargada de manejar las ecuaciones del flujo de carga
    '''
    def __init__(self, system, print_sec=False):
        '''
            Está función instancia la clase Equations 
            input
                system: nombre del sistema en pandapower ieee57 o ieee118
                print_sec: para imprimir secuencia de ejecuciones
            return
                Objeto de tipo system
        '''
        self.print_sec = print_sec
        if system=='ieee57':
            self.system = pp_net.case57()
        elif system=='ieee118':
            self.system = pp_net.case118()
        else:
            self.system = None
        self.voltage = dict(
                        (i, self.system.bus['vn_kv'].values[i]) 
                        for i in range(self.system.bus.shape[0])
                        )
        if self.print_sec: print('Se crea el objeto del sistema a trabajar')
    def _get_ijc_from_system(self):
        if self.print_sec: print('Se crea la variables i, j, c del sistema')
        return {'i':list(self.system.bus.index.values),
                'j':list(self.system.bus.index.values),
                'c':list(self.system.line.index.values)}
    def _get_branchstatus(self):
        '''
            Está función entrega el estado de las líneas, si están operativas o no.
            input
                line: dataframe de las líneas de pandapower 
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        if self.print_sec: print('Se crea la variable de branchstatus')
        branchstatus = {}
        c_line = 0
        for i,j in list(zip(list(self.system.line['from_bus']), list(self.system.line['to_bus']))):
            branchstatus[(i, j, c_line)] = True
            c_line +=1
        c_line = 0
        for j,i in list(zip(list(self.system.line['to_bus']), list(self.system.line['from_bus']))):
            branchstatus[(j, i, c_line)] = True
            c_line +=1
        return branchstatus
    def _get_conductance_susceptance(self):
        '''
            Está función entrega el estado de las líneas, si están operativas o no.
            input
                line: dataframe de las líneas de pandapower 
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        if self.print_sec: print('Se crea las variables de conductance y susceptance')
        branchstatus = {}
        c_line = 0
        for i,j in list(zip(list(self.system.line['from_bus']), list(self.system.line['to_bus']))):
            branchstatus[(i, j, c_line)] = True
            c_line +=1
        c_line = 0
        for j,i in list(zip(list(self.system.line['to_bus']), list(self.system.line['from_bus']))):
            branchstatus[(j, i, c_line)] = True
            c_line +=1
        return branchstatus
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
        for c in range(self.system.line.shape[0]):
            row = self.system.line.iloc[c]
            ratio[(row['to_bus'], row['from_bus'], c)]\
                = row['max_i_ka']*self.voltage.get(int(row['from_bus']))
        return ratio