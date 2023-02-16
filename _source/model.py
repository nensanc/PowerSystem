import pyomo.environ as pyomo
import numpy as np
from pandas import DataFrame
import logging
# Configurar el nivel de registro
logging.basicConfig(level=logging.INFO)
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
        self.model.name = system_param.get('model_name')
        self.model.i = pyomo.Set(initialize=[i for i in system_param.get('i')], doc='Terminal i')
        self.model.j = pyomo.Set(initialize=[j for j in system_param.get('j')], doc='Terminal j')
        self.model.c = pyomo.Set(initialize=[c for c in system_param.get('c')], doc='Lines')
        self.model.gen = pyomo.Set(initialize=[gen for gen in system_param.get('gen')], doc='Gen')
        self.model.demandbid = pyomo.Set(initialize=[id_ for id_ in system_param.get('demandbid')], doc='Demandbid')
        self.model.bus = pyomo.Set(initialize=[bus for bus in system_param.get('buses')], doc='Buses')
        self.model.shunt = pyomo.Set(initialize=[sht for sht in range(5)], doc='Shunt')
        self.bounds_bus = system_param.get('bounds_bus')
        self.gen_bound_p = system_param.get('gen_bound_p')
        self.gen_bound_q = system_param.get('gen_bound_q')
        self.bounds_theta = system_param.get('bounds_theta')
        self.Pd = system_param.get('Pd')
        self.Qd = system_param.get('Qd')
        self.v_ref = system_param.get('v_ref')
        self.atBus = system_param.get('atBus')
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
        if self.print_sec: print('Se crea el objeto del modelo de optimización')
    def _add_var_p_line(self, init_values):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            imput    
                init_values: valores iniciales de la variable  P
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
                initialize=init_values, 
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
    def _add_var_q_line(self, init_values):
        '''
            Está función crea la variable de potencia reactiva de las líneas Q(i,j,c,t)
            imput    
                init_values: valores iniciales de la variable Q
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
                initialize=init_values, 
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
    def _add_var_v_bus(self, init_values):
        '''
            Está función crea la variable de voltaje para cada una de las barras V_bus(i,t) or V_bus(j,t)
            imput    
                init_values: valores iniciales de la variable  V_bus
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Vbus')
        self.model.V_Vbus = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                bounds=self.bounds_bus,
                initialize=init_values,
                doc='Voltage in bus b at time t'
            )
    def _add_var_theta_bus(self, init_values):
        '''
            Está función crea la variable de ángulo para cada una de las barras V_Theta(i,t) or V_Theta(j,t)
            imput    
                init_values: valores iniciales de la variable  V_Theta
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Theta')
        self.model.V_Theta = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                initialize=init_values,
                doc='angle in bus b at time t'
            )
    def _add_var_p_gen(self, init_values):
        '''
            Está función crea la variable de potencia activa de los generadores V_Pgen(gen,t)
            imput    
                init_values: valores iniciales de la variable  V_Pgen
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Pgen')
        self.model.V_Pgen = pyomo.Var(
                self.model.gen,
                self.model.t, 
                within=pyomo.Reals,
                bounds=self.gen_bound_p,
                initialize=init_values,
                doc='potencia in gen g at time t'
            )
    def _add_var_q_gen(self, init_values):
        '''
            Está función crea la variable de potencia reactiva de los generadores V_Qgen(gen,t)
            imput    
                init_values: valores iniciales de la variable  V_Qgen
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Qgen')
        self.model.V_Qgen = pyomo.Var(
                self.model.gen,
                self.model.t, 
                within=pyomo.Reals,
                bounds=self.gen_bound_q,
                initialize=init_values,
                doc='potencia in gen g at time t'
            )
    def _add_var_Shunt_bus(self):
        '''
            Está función crea la variable de Shunt del sistema  V_Shunt(i,sht,t)
            imput    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Shunt')
        self.model.V_Shunt = pyomo.Var(
                self.model.i,
                self.model.shunt,
                self.model.t, 
                within=pyomo.Binary,
                initialize=0,
                doc='Shunt in nodo i con sht at time t'
            )
    def _add_var_pd_elastic(self):
        '''
            Está función crea la variable de demanda elastica V_Pd_elastic(demandbid,t)
            imput    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Pd_elastic')
        self.model.V_Pd_elastic = pyomo.Var(
                self.model.demandbid,
                self.model.t, 
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
    def _add_power_s_constraint(self, branchstatus, ratio_line):
        '''
            Está función crea la restricción de potencia aparente para las líneas (i,j,c)
            imput    
                branchstatus: líneas activas del sistema
                ratio_line: capacidad máxima de potencia de las líneas del sistema
            return
                None
        '''
        def c_SLimit(model, i, j, c , t):
            if branchstatus.get((i,j,c)):
                return (
                        (model.V_LineP[i, j, c, t])**2
                        + (model.V_LineQ[i, j, c, t])**2
                        <= (ratio_line[(i, j, c)])**2
                    )
            else:
                return pyomo.Constraint.Skip
        if self.print_sec: print('Se agrega la restricción de potencia aparente')
        self.model.line_s_limit = pyomo.Constraint(self.model.i,
                                                    self.model.j,
                                                    self.model.c,
                                                    self.model.t, 
                                                    rule=c_SLimit,
                                                    doc='Apparent power limit on line ijc')
    def _add_power_p_constraint(self, branchstatus, ratio_trafo, g , b, angle=None):
        '''
            Está función crea la restricción de potencia activa para las líneas (i,j,c)
            imput    
                branchstatus: líneas activas del sistema
                ratio_trafo: ratio_trafo de lso tansformadores,
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia activa en la linea c (i, j)')
        def line_constraint(model, i, j, c, t):
            if branchstatus.get((i,j,c)):
                return (g[i,j,c] * (model.V_Vbus[i,t]**2) / (ratio_trafo[i,j,c]**2)) \
                    - (model.V_Vbus[i,t] * model.V_Vbus[j,t] / ratio_trafo[i,j,c]) * \
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
    def _add_power_q_constraint(self, branchstatus, ratio_trafo, g , b, bc=None, angle=None):
        '''
            Está función crea la restricción de potencia activa para las líneas (i, j,c)
            imput    
                branchstatus: líneas activas del sistema
                ratio_trafo: capacidad máxima de potencia de las líneas del sistema,
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia reactiva en la linea c (i, j)')
        def line_constraint(model, i, j, c, t):
            if branchstatus.get((i,j,c)):
                return -(model.V_Vbus[i,t]**2 * b[i,j,c] / ratio_trafo[i,j,c]**2) \
                        - (model.V_Vbus[i,t] * model.V_Vbus[j,t] / ratio_trafo[i,j,c]) \
                        * (g[i,j,c] * pyomo.sin(model.V_Theta[i,t] - model.V_Theta[i,t]) \
                        - b[i,j,c] * pyomo.cos(model.V_Theta[i,t] - model.V_Theta[i,t])) \
                    == model.V_LineQ[i,j,c,t]
            else:
                return pyomo.Constraint.Skip
        self.model.line_q_limit = pyomo.Constraint(
                                        self.model.i,
                                        self.model.j,
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint,
                                        doc='Reactive power limit on line jic'
                                    )
    def _add_p_balanced_constraint(self, branchstatus, genstatus, demandbidmap, Gs=None):
        '''
            Está función crea la restricción de balance de potencia activa
            imput    
                branchstatus: líneas activas del sistema
                genstatus: estado de los generadores del sistema
                demandbidmap: id de la demanda y bus en el que se conecta
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia activa')
        def balance_eqn_rule(model, i, t):
            return (sum(model.V_Pgen[gen, t] for gen in self.model.gen if self.atBus.get((gen,i)) and genstatus.get(gen))
                    - (self.Pd.get((i,t)) if self.Pd.get((i,t)) else 0)
                    - sum(model.V_Pd_elastic[demandbid,t] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,i)))
                    == sum(model.V_LineP[i,j,c,t] for (_,j,c) in branchstatus if branchstatus.get((i,j,c)))
                    + sum(model.V_LineP[j,i,c,t] for (_,j,c) in branchstatus if branchstatus.get((j,i,c)))
                    + model.V_Vbus[i,t]**2)
        self.model.c_BalanceP = pyomo.Constraint(
                                        self.model.i, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Active power balance')
    def _add_q_balanced_constraint(self, branchstatus, genstatus, Bs=None):
        '''
            Está función crea la restricción de balance de potencia reactiva
            imput    
                branchstatus: líneas activas del sistema
                genstatus: estado de los generadores del sistema
                demandbidmap: id de la demanda y bus en el que se conecta
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia reactiva')
        def balance_eqn_rule(model, i, t):
            return (sum(model.V_Qgen[gen, t] for gen in self.model.gen if self.atBus.get((gen,i)) and genstatus.get(gen))
                    - (self.Qd.get((i,t)) if self.Qd.get((i,t)) else 0)
                    == sum(model.V_LineQ[i,j,c,t] for (_,j,c) in branchstatus if branchstatus.get((i,j,c)))
                    + sum(model.V_LineQ[j,i,c,t] for (_,j,c) in branchstatus if branchstatus.get((j,i,c)))
                    + model.V_Vbus[i,t]**2 
                    + model.V_Vbus[i,t]**2*(sum(model.V_Shunt[i, sht, t] for sht in self.model.shunt)))
        self.model.c_BalanceQ = pyomo.Constraint(
                                        self.model.i, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Reactive power balance')
    def _add_function_obj(self, v_ref):
        '''
            Está función crea la función objetivo
            imput    
                v_ref: valores de voltaje referencia de los nodos piloto para el optimizador
            return
                None
        '''
        if self.print_sec: print('Se agrega la función objetivo')
        def obj_rule(model):
            return  (
                    0.01 * sum((model.V_Shunt[bus, sht, t] - model.V_Shunt[bus, sht, t-1])**2
                        for bus in model.i
                        for sht in self.model.shunt
                        for t in model.t 
                        if t >= 2)
                    +300000 * sum((model.V_Vbus[bus, t] - v_ref.get((bus, t)))**2
                        for bus in model.i
                        for t in model.t 
                        if v_ref.get((bus, t)))
                    +100 * sum(model.V_Qgen[gen, t]**2 
                        for gen in model.gen
                        for t in model.t)
                )
        self.model.obj = pyomo.Objective(rule=obj_rule, sense = pyomo.minimize)
    def solve_model(self):
        '''
            Está función resulve el modelo de optimización
            imput    
                none
            return
                None
        '''
        if self.print_sec: print('Se inicia la resolución del modelo...\n')
        solver = pyomo.SolverFactory('solver/bonmin')
        solver.options['output_file'] = "bonmin.log" # Especificar el archivo de registro
        result = solver.solve(self.model)
        result.write()
        return True if result.solver.status.value=='ok' else False
    def save_model_variables(self, path):
        '''
            Está función guarda los datos del modelo de optimización
            imput    
                path: ruta donde se guardan los datos
            return
                None
        '''
        variables = list(self.model.component_objects(pyomo.Var, active=True))
        if self.print_sec: print('Se guardan todas las variables...\n')
        for e in variables:
            df = DataFrame(list(e.get_values().items()))
            df.to_csv(f'{path}/Var_{e.name}.csv', index=False)
