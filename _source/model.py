import pyomo.environ as pyomo
import numpy as np
class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, ijc_values, print_sec=False):
        '''
            Está función instancia la clase CreateModel 
            input
               ijc_values: valores i, j, c del sistema 
               print_sec: para imprimir secuencia de ejecuciones
            return
                Objeto de tipo model
        '''
        # creamos el modelo de optimización
        self.print_sec = print_sec
        self.model = pyomo.ConcreteModel();
        self.model.i = pyomo.Set(initialize=[i for i in ijc_values.get('i')], doc='Terminal i')
        self.model.j = pyomo.Set(initialize=[j for j in ijc_values.get('j')], doc='Terminal j')
        self.model.c = pyomo.Set(initialize=[c for c in ijc_values.get('c')], doc='Lines')
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
        if self.print_sec: print('Se crea el objeto del modelo de optimización')
    def _add_var_p_line(self):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_lineP')
        self.model.V_LineP = pyomo.Var(
                self.model.i,
                self.model.j,
                self.model.c,
                self.model.t, 
                within=pyomo.Reals, 
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
    def _add_var_q_line(self):
        '''
            Está función crea la variable de potencia reactiva de las líneas Q(i,j,c,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_lineQ')
        self.model.V_LineQ = pyomo.Var(
                self.model.i,
                self.model.j,
                self.model.c,
                self.model.t, 
                within=pyomo.Reals, 
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
    def _add_power_s_constraint(self, branchstatus, ratio):
        '''
            Está función crea la restricción de potencia aparente para las líneas (i,j,c)
            imput    
                self: variables de la clase 
                branchstatus: líneas activas del sistema
                ratio: capacidad máxima de potencia de las líneas del sistema
            return
                None
        '''
        def c_SLimit(model, i, j, c , t):
            if branchstatus.get((i,j,c)):
                return (np.power(model.V_LineP[i, j, c, t], 2)\
                        + np.power(model.V_LineQ[i, j, c, t], 2))\
                        <= np.power(ratio[(i, j, c)], 2)
            else:
                return pyomo.Constraint.Skip
        if self.print_sec: print('Se agrega la restricción de potencia aparente')
        self.model.line_s_limit = pyomo.Constraint(self.model.i,
                                                    self.model.j,
                                                    self.model.c,
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
