import pyomo.environ as pyomo
import numpy as np
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
        self.model.allowed_combinations = pyomo.Set(
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
    def _add_power_s_constraint(self):
        def c_SLimit(model, allowed_combinations, t):
            return (
                np.sqr(model.V_LineP[allowed_combinations,t])\
                + np.sqr(model.V_LineQ[allowed_combinations,t]))\
                <= np.int32sqr(model.rateA[allowed_combinations]
                )

        self.model.line_s_limit = pyomo.Constraint(self.model.allowed_combinations, 
                                                    self.model.t, rule=c_SLimit,
                                                    doc='Apparent power limit on line ijc')
    def _add_power_p_constraint(self):
        def line_constraint(model, i, j, c, t):
            return (model.g[i,j,c] * (model.V_V[i,t]**2) / (model.ratio[i,j,c]**2)) \
                - (model.V_V[i,t] * model.V_V[j,t] / model.ratio[i,j,c]) * \
                    (model.g[i,j,c] * np.cos(model.V_Theta[i,t] - model.V_Theta[j,t] - model.angle[i,j,c]) + 
                    model.b[i,j,c] * np.sin(model.V_Theta[i,t] - model.V_Theta[j,t] - model.angle[i,j,c])) \
                == model.V_LineP[i,j,c,t]
        self.model.line_p_limit = pyomo.Constraint(self.model.allowed_combinations, 
                                                    self.model.t, rule=line_constraint,
                                                    doc='Active power limit on line ijc')
