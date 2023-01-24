import pyomo.environ as pyomo

class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, list_i, list_j, list_c) -> None:
        '''
            Está función instancia la clase CreateModel 
            input
                
            return
                None
        '''
        # creamos el modelo de optimización
        self.model = pyomo.ConcreteModel();
        self.model.i = pyomo.Set(initialize=list_i, doc='Buses')
        self.model.j = pyomo.Set(initialize=list_j, doc='Buses')
        self.model.c = pyomo.Set(initialize=list_c, doc='Lines')
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
    def _get_var_p_line(self, line):
        '''
            Está función crea las variables de las líneas con pyomo
                line: dataframe de las líneas de pandapower 
            return
                branchstatus: diccionario que contiene el estado de línea c, de i a j
                                branchstatus(i, j, c)
        '''
        allowed_combinations = pyomo.Set(initialize=[(0,1,2,3), (1,2,3,4), (4,5,6,7)], doc='Allowed combinations')
        bounds = {(0,1,2,3): (-500, 500), (1,2,3,4): (-800, 800), (4,5,6,7): (-1000, 1000)}
        self.model.V_LineP = pyomo.Var(allowed_combinations, within=pyomo.Reals, bounds=bounds, doc='Real power flowing from bus i towards bus j on line c at time t')
