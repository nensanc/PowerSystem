import pandapower.networks as pp_net
import pandapower as pp

class GetVariablesSystem(object):
    '''
        Class encargada de manejar las ecuaciones del flujo de carga
    '''
    def __init__(self, system) -> None:
        '''
            Está función instancia la clase Equations 
            input
                voltage: voltaje del sistema
                baseMVA: MVA base de la red de pandapower
            return
                None
        '''
        if system=='ieee57':
            self.system = pp_net.case57()
        elif system=='ieee118':
            self.system = pp_net.case118()
        else:
            self.system = None
    def _get_ijc_from_system(self):
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
        branchstatus = []
        c_line = 0
        for i,j in list(zip(list(self.system.line['from_bus']), list(self.system.line['to_bus']))):
            branchstatus.append((i, j, c_line))
            c_line +=1
        c_line = 0
        for j,i in list(zip(list(self.system.line['to_bus']), list(self.system.line['from_bus']))):
            branchstatus.append((j, i, c_line))
            c_line +=1
        return branchstatus
    def _get_rate(self, line):
        '''
            Está función entrega los mva de la líneas 
            input
                line: dataframe de las líneas de pandapower 
                voltage: voltaje del sistema
                baseMVA: MVA base de la red de pandapower
            return
                branchstatus: diccionario que contiene los MVA de línea c, en i, j
                                rate(i, j, c)
        '''
        rate = dict((
            (line.iloc[c]['from_bus'], line.iloc[c]['to_bus'], c), 
            line.iloc[c]['max_i_ka']*self.voltage/self.baseMVA) 
        for c in range(line.shape[0])
        )
        return rate