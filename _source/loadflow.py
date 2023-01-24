

class Equations(object):
    '''
        Class encargada de manejar las ecuaciones del flujo de carga
    '''
    def __init__(self, voltage, baseMVA) -> None:
        '''
            Está función instancia la clase Equations 
            input
                voltage: voltaje del sistema
                baseMVA: MVA base de la red de pandapower
            return
                None
        '''
        self.voltage = voltage
        self.baseMVA = baseMVA
    def get_branchstatus(self, line):
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
        for i,j in list(zip(list(line['from_bus'], list(line['to_bus'])))):
            branchstatus.append((i, j, c_line))
            c_line +=1
        c_line = 0
        for j,i in list(zip(list(line['to_bus'], list(line['from_bus'])))):
            branchstatus.append((j, i, c_line))
            c_line +=1
        return branchstatus
    def get_rate(self, line):
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