import pyomo.environ as pyomo
import numpy as np
class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, system_param, print_sec=False):
        '''
            Está función instancia la clase CreateModel 
            input
               system_param: valores i, j, c del sistema 
               print_sec: para imprimir secuencia de ejecuciones
            return
                Objeto de tipo model
        '''
        # creamos el modelo de optimización
        self.print_sec = print_sec
        self.model = pyomo.ConcreteModel();
        self.model.i = pyomo.Set(initialize=[i for i in system_param.get('i')], doc='Terminal i')
        self.model.j = pyomo.Set(initialize=[j for j in system_param.get('j')], doc='Terminal j')
        self.model.c = pyomo.Set(initialize=[c for c in system_param.get('c')], doc='Lines')
        self.model.bus = pyomo.Set(initialize=[b for b in system_param.get('buses')], doc='Buses')
        self.bounds_bus = system_param.get('bounds_bus')
        self.bounds_theta = system_param.get('bounds_theta')
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
    def _add_var_v_bus(self):
        '''
            Está función crea la variable de voltaje para cada una de las barras V_bus(i,t) or V_bus(j,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Vbus')
        def bounds_func(model,bus, t):
            return self.bounds_bus[(bus, t)]
        self.model.V_Vbus = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                bounds=bounds_func,
                doc='Voltage in bus b at time t'
            )
    def _add_var_theta_bus(self):
        '''
            Está función crea la variable de ángulo para cada una de las barras V_Theta(i,t) or V_Theta(j,t)
            imput    
                self: variables de la clase 
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Theta')
        self.model.V_Theta = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                #initialize=self.bounds_theta,
                doc='angle in bus b at time t'
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
                                                    self.model.t, 
                                                    rule=c_SLimit,
                                                    doc='Apparent power limit on line ijc')
    def _add_power_p_constraint(self, branchstatus, ratio, g , b, angle=None):
        '''
            Está función crea la restricción de potencia activa para las líneas (i,j,c)
            imput    
                self: variables de la clase 
                branchstatus: líneas activas del sistema
                ratio: capacidad máxima de potencia de las líneas del sistema,
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia activa en la linea c (i, j)')
        def line_constraint(model, i, j, c, t):
            if branchstatus.get((i,j,c)):
                return (g[i,j,c] * (model.V_Vbus[i,t]**2) / (ratio[i,j,c]**2)) \
                    - (model.V_Vbus[i,t] * model.V_Vbus[j,t] / ratio[i,j,c]) * \
                        (g[i,j,c] * pyomo.cos(model.V_Theta[i,t] - model.V_Theta[j,t]) + 
                        b[i,j,c] * pyomo.sin(model.V_Theta[i,t] - model.V_Theta[j,t])) \
                    == model.V_LineP[i,j,c,t]
            else:
                return pyomo.Constraint.Skip
        self.model.line_p_limit = pyomo.Constraint(
                                        self.model.i,
                                        self.model.j,
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint,
                                        doc='Active power limit on line ijc'
                                    )
