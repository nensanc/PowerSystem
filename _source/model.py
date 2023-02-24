import pyomo.environ as pyomo
import numpy as np
from pandas import DataFrame
# import logging
# # Configurar el nivel de registro
# logging.basicConfig(level=logging.INFO)
class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, system_param, system_values, print_sec=False):
        '''
            Está función instancia la clase CreateModel 
            input
               system_param: valores i, j, c del sistema 
               print_sec: para imprimir secuencia de ejecuciones
            return
                Objeto de tipo model
        '''
        self.print_sec = print_sec
        self.system_values = system_values
        self.system_param = system_param
    def init_model(self):
        '''
            Está función crea el modelo de optimización y los Sets del modelo
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se crea el objeto del modelo de optimización y los Sets')
        self.model = pyomo.ConcreteModel()
        self.model.name = self.system_param.get('model_name')
        self.model.i = pyomo.Set(initialize=[i for i in self.system_param.get('i')], doc='Terminal i')
        self.model.j = pyomo.Set(initialize=[j for j in self.system_param.get('j')], doc='Terminal j')
        self.model.a = pyomo.Set(initialize=[a for a in self.system_param.get('a')], doc='áreas')
        self.model.c = pyomo.Set(initialize=[c for c in self.system_param.get('c')], doc='Lines')
        self.model.gen = pyomo.Set(initialize=[gen for gen in self.system_param.get('gen')], doc='Gen')
        self.model.slack = pyomo.Set(initialize=[gen for gen in self.system_param.get('slack')], doc='Slack')
        self.model.demandbid = pyomo.Set(initialize=[id_ for id_ in self.system_param.get('demandbid')], doc='Demandbid')
        self.model.bus = pyomo.Set(initialize=[bus for bus in self.system_param.get('buses')], doc='Buses')
        self.model.shunt = pyomo.Set(initialize=[sht for sht in range(2)], doc='Shunt')
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
    def _add_var_p_line(self):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            input    
                None
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
                initialize=self.system_values.get('init_line_p'), 
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
    def _add_var_q_line(self):
        '''
            Está función crea la variable de potencia reactiva de las líneas Q(i,j,c,t)
            input    
                None
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
                initialize=self.system_values.get('init_line_q'), 
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
    def _add_var_v_bus(self):
        '''
            Está función crea la variable de voltaje para cada una de las barras V_bus(i,t) or V_bus(j,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Vbus')
        self.model.V_Vbus = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                bounds=self.system_param.get('bounds_bus'),
                initialize=self.system_values.get('init_bus_v'),
                doc='Voltage in bus b at time t'
            )
    def _add_var_theta_bus(self):
        '''
            Está función crea la variable de ángulo para cada una de las barras V_Theta(i,t) or V_Theta(j,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Theta')
        self.model.V_Theta = pyomo.Var(
                self.model.bus,
                self.model.t, 
                within=pyomo.Reals,
                initialize=self.system_values.get('init_bus_theta'),
                #bounds=self.system_param.get('bounds_theta')
                doc='angle in bus b at time t'
            )
    def _add_var_p_gen(self):
        '''
            Está función crea la variable de potencia activa de los generadores V_Pgen(gen,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Pgen')
        self.model.V_Pgen = pyomo.Var(
                self.model.gen,
                self.model.t, 
                within=pyomo.Reals,
                #bounds=self.system_param.get('gen_bound_p'),
                initialize=self.system_values.get('init_gen_p'),
                doc='potencia in gen g at time t'
            )
        self.model.V_Pslack = pyomo.Var(
                self.model.slack,
                self.model.t, 
                within=pyomo.Reals,
                #bounds=self.system_param.get('gen_bound_p'),
                initialize=self.system_values.get('init_slack_p'),
                doc='potencia in gen g at time t'
            )
    def _add_var_q_gen(self):
        '''
            Está función crea la variable de potencia reactiva de los generadores V_Qgen(gen,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Qgen')
        def _add_gen_bound(model, gen, t):
            return (self.system_values.get('bound_gen_q').get((gen,t)) 
                    if self.system_values.get('bound_gen_q').get((gen,t)) 
                    else (0,0))
        self.model.V_Qgen = pyomo.Var(
                self.model.gen,
                self.model.t, 
                within=pyomo.Reals,
                bounds=_add_gen_bound,
                initialize=self.system_values.get('init_gen_q'),
                doc='potencia in gen g at time t'
            )
        self.model.V_Qslack = pyomo.Var(
                self.model.slack,
                self.model.t, 
                within=pyomo.Reals,
                #bounds=self.system_values.get('bound_gen_q'),
                initialize=self.system_values.get('init_slack_q'),
                doc='potencia in gen g at time t'
            )
    def _add_var_Shunt_bus(self):
        '''
            Está función crea la variable de Shunt del sistema  V_Shunt(i,sht,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Shunt')
        self.model.V_Shunt = pyomo.Var(
                self.model.i,
                self.model.shunt,
                self.model.t, 
                within=pyomo.Boolean,
                initialize=0,
                doc='Shunt in nodo i con sht at time t'
            )
    def _add_var_slack_variable(self):
        '''
            Está función crea la variable de holgura del problema de optimizacion
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable Slack Variables')
        self.model.V_bc = pyomo.Var(
                self.model.i,
                self.model.j, 
                self.model.c,
                bounds=(0,1),
                within=pyomo.Reals,
            )
        self.model.V_angle = pyomo.Var(
                self.model.i,
                self.model.j, 
                self.model.t,
                bounds=(0,2*np.pi),
            )
        self.model.V_Gs = pyomo.Var(
                self.model.i,
                bounds=(0,1),
                within=pyomo.Reals,
            )
        self.model.V_Bs = pyomo.Var(
                self.model.i,
                self.model.t,
                bounds=(0,1),
                within=pyomo.Reals,
            )
        self.model.delta_Q = pyomo.Var(
                self.model.i,
                self.model.j,
                self.model.c,
                self.model.t,
                # bounds=(-1,1),
                within=pyomo.Reals,
            )
        self.model.V_Rtrafo= pyomo.Var(
                self.model.i,
                self.model.j,
                self.model.t,
                bounds=(1,21),
                initialize = 9,
                within=pyomo.Integers,
            )
    def _add_var_pd_elastic(self):
        '''
            Está función crea la variable de demanda elastica V_Pd_elastic(demandbid,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Pd_elastic')
        self.model.V_Pd_elastic = pyomo.Var(
                self.model.demandbid,
                self.model.i, 
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
        self.model.V_Qd_elastic = pyomo.Var(
                self.model.demandbid,
                self.model.i, 
                self.model.t,
                within=pyomo.Reals,
                bounds=(-1,1),
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
        if self.print_sec: print('Se agrega la restricción de potencia activa')
        def line_constraint_ij(model, i, j, c, t):
            if branchstatus.get((i,j,c)):
                return ((g[i,j,c] * (model.V_Vbus[i,t]**2) / model.V_Rtrafo[i,j,t]**2)
                    - (model.V_Vbus[i,t] * model.V_Vbus[j,t] / model.V_Rtrafo[i,j,t])
                    * (g[i,j,c] * pyomo.cos(model.V_Theta[i,t] - model.V_Theta[j,t] - model.V_angle[i,j,t]) 
                    + b[i,j,c] * pyomo.sin(model.V_Theta[i,t] - model.V_Theta[j,t] - model.V_angle[i,j,t]))
                    == model.V_LineP[i,j,c,t])
            else:
                return pyomo.Constraint.Skip
        self.model.line_p_limit_ij = pyomo.Constraint(
                                        self.model.i,
                                        self.model.j,
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint_ij,
                                        doc='Active power limit on line ijc'
                                    )

        def line_constraint_ji(model, j, i, c, t):
            if branchstatus.get((i, j, c)):
                return (g[i,j,c] * model.V_Vbus[j,t]**2
                    - (model.V_Vbus[i,t] * model.V_Vbus[j,t] / model.V_Rtrafo[i,j,t])
                    * (g[i,j,c] * pyomo.cos(model.V_Theta[j,t] - model.V_Theta[i,t] + model.V_angle[i,j,t]) 
                    + b[i,j,c] * pyomo.sin(model.V_Theta[j,t] - model.V_Theta[i,t] + model.V_angle[i,j,t]))
                    == model.V_LineP[j,i,c,t])
            else:
                return pyomo.Constraint.Skip
        self.model.line_p_limit_ji = pyomo.Constraint(
                                        self.model.j,
                                        self.model.i,
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint_ji,
                                        doc='Active power limit on line jic'
                                    )
    def _add_power_q_constraint(self, branchstatus, ratio_trafo, g , b, bc=None, angle=None):
        '''
            Está función crea la restricción de potencia activa para las líneas (i, j,c)
            input    
                branchstatus: líneas activas del sistema
                ratio_trafo: capacidad máxima de potencia de las líneas del sistema,
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia reactiva')
        def line_constraint_ij(model, i, j, c, t):
            if branchstatus.get((i,j,c)):
                return (
                        -model.V_Vbus[i,t]**2 * (b[i,j,c] + model.V_bc[i,j,c]/2) / model.V_Rtrafo[i,j,t]**2
                        - model.V_Vbus[i,t] * model.V_Vbus[j,t] / model.V_Rtrafo[i,j,t] 
                        * model.delta_Q[i,j,c,t]
                        * (g[i,j,c] * pyomo.sin(model.V_Theta[i,t] - model.V_Theta[j,t] - model.V_angle[i,j,t])
                        - b[i,j,c] * pyomo.cos(model.V_Theta[i,t] - model.V_Theta[j,t] - model.V_angle[i,j,t]))
                    == model.V_LineQ[i,j,c,t])
            else:
                return pyomo.Constraint.Skip
        self.model.line_q_limit_ij = pyomo.Constraint(
                                        self.model.i,
                                        self.model.j,
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint_ij,
                                        doc='Reactive power limit on line ijc'
                                    )
        def line_constraint_ji(model, j, i, c, t):
            if branchstatus.get((i,j,c)):
                return (
                        -model.V_Vbus[j,t]**2 * (b[i,j,c] +  model.V_bc[i,j,c]/2)
                        - model.V_Vbus[i,t] * model.V_Vbus[j,t] / model.V_Rtrafo[i,j,t]
                        * model.delta_Q[j,i,c,t]
                        * (g[i,j,c] * pyomo.sin(model.V_Theta[j,t] - model.V_Theta[i,t] + model.V_angle[i,j,t])
                        - b[i,j,c] * pyomo.cos(model.V_Theta[j,t] - model.V_Theta[i,t] + model.V_angle[i,j,t]))
                    == model.V_LineQ[j,i,c,t])
            else:
                return pyomo.Constraint.Skip
        self.model.line_q_limit_ji = pyomo.Constraint(
                                        self.model.j,
                                        self.model.i,                                        
                                        self.model.c,
                                        self.model.t, 
                                        rule=line_constraint_ji,
                                        doc='Reactive power limit on line jic'
                                    )
    def _add_p_balanced_constraint(self, branchstatus, genstatus, demandbidmap, Gs=None):
        '''
            Está función crea la restricción de balance de potencia activa
            input    
                branchstatus: líneas activas del sistema
                genstatus: estado de los generadores del sistema
                demandbidmap: id de la demanda y bus en el que se conecta
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia activa')
        def balance_eqn_rule(model, i, t):
            return (sum(model.V_Pgen[gen, t] for gen in self.model.gen if self.system_param.get('atBus').get((gen,i)) and genstatus.get((gen,i)))
                    + sum(model.V_Pslack[gen, t] for gen in self.model.slack if self.system_param.get('atBusSlack').get((gen,i)))
                    - (self.system_values.get('Pd').get((i,t)) if self.system_values.get('Pd').get((i,t)) else 0)
                    - sum(model.V_Pd_elastic[demandbid,i] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,i)))
                    == sum(model.V_LineP[i,j,c,t] for (_,j,c) in branchstatus if branchstatus.get((i,j,c)))
                    + sum(model.V_LineP[i,j,c,t] for (j,_,c) in branchstatus if branchstatus.get((j,i,c)))
                    + model.V_Vbus[i,t]**2 * model.V_Gs[i])
        self.model.c_BalanceP = pyomo.Constraint(
                                        self.model.i, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Active power balance')
    def _add_q_balanced_constraint(self, branchstatus, genstatus, demandbidmap, Bs=None):
        '''
            Está función crea la restricción de balance de potencia reactiva
            input    
                branchstatus: líneas activas del sistema
                genstatus: estado de los generadores del sistema
                demandbidmap: id de la demanda y bus en el que se conecta
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia reactiva')
        def balance_eqn_rule(model, i, t):
            return (
                    sum(model.V_Qgen[gen, t] for gen in self.model.gen if self.system_param.get('atBus').get((gen,i)) and genstatus.get((gen,i)))
                    + sum(model.V_Qslack[gen, t] for gen in self.model.slack if self.system_param.get('atBusSlack').get((gen,i)))
                    #* sum(model.V_Qd_elastic[demandbid,i,t] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,i)))
                    - (self.system_values.get('Qd').get((i,t)) if self.system_values.get('Qd').get((i,t)) else 0)
                    == 
                    (sum(model.V_LineQ[i,j,c,t] for (_,j,c) in branchstatus if branchstatus.get((i,j,c)))
                    + sum(model.V_LineQ[i,j,c,t] for (j,_,c) in branchstatus if branchstatus.get((j,i,c))))
                    - model.V_Vbus[i,t]**2 * model.V_Bs[i,t]
                    - model.V_Vbus[i,t]**2*(sum(model.V_Shunt[i, sht, t] for sht in self.model.shunt if self.system_param.get('bus_shunt').get(i)))
                    )
        self.model.c_BalanceQ = pyomo.Constraint(
                                        self.model.i, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Reactive power balance')
    def _add_function_obj(self):
        '''
            Está función crea la función objetivo
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la función objetivo')
        def obj_rule(model):
            return  (
                    sum((model.V_Shunt[bus, sht, t] - model.V_Shunt[bus, sht, t-1])**2
                        for bus in model.i
                        for sht in self.model.shunt
                        for t in model.t 
                        if t >= 2 and self.system_param.get('bus_shunt').get(bus))
                    + 1e6 * sum((model.V_Vbus[bus, t] - self.system_values.get('init_bus_v').get((bus, t)))**2
                        for bus in model.i
                        for t in model.t 
                        if self.system_values.get('init_bus_v').get((bus, t)))
                    + sum(model.V_Qgen[gen, t]**2 
                        for gen in model.gen
                        for t in model.t)
                )
        self.model.obj = pyomo.Objective(rule=obj_rule, sense = pyomo.minimize)
    def solve_model(self):
        '''
            Está función resulve el modelo de optimización
            input    
                none
            return
                None
        '''
        if self.print_sec: print('\n--> Se inicia la solución del modelo <--\n')
        solver = pyomo.SolverFactory('solver/bonmin', tee=True)
        solver.options['output_file'] = "bonmin.log" # Especificar el archivo de registro
        solver.options['max_iter'] = 15000
        result = solver.solve(self.model)
        result.write()
        return True if result.solver.status.value=='ok' else False
    def save_model_variables(self, path):
        '''
            Está función guarda los datos del modelo de optimización
            input    
                path: ruta donde se guardan los datos
            return
                None
        '''
        variables = list(self.model.component_objects(pyomo.Var, active=True))
        if self.print_sec: print('Se guardan todas las variables...\n')
        for e in variables:
            df = DataFrame(list(e.get_values().items()))
            df.to_csv(f'Var_{e.name}.csv', index=False)
