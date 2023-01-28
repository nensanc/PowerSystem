import pyomo.environ as pyomo

class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, combinations, bounds) -> None:
        '''
            Está función instancia la clase CreateModel 
            input
                
            return
                None
        '''
        # creamos el modelo de optimización
        self.model = pyomo.ConcreteModel();
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
        self.allowed_combinations = pyomo.Set(
            initialize=combinations, 
            doc='Allowed combinations'
            )
    def _get_var_p_line(self, bounds):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        
        self.model.V_LineP = pyomo.Var(
                self.allowed_combinations, 
                self.model.t, 
                within=pyomo.Reals, 
                bounds=bounds, 
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
    def _get_var_q_line(self):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        
        self.model.V_LineP = pyomo.Var(
                self.allowed_combinations, 
                self.model.t, 
                within=pyomo.Reals, 
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
