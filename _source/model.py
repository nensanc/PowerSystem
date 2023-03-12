import pyomo.environ as pyomo
from pandas import DataFrame
class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, system_param, system_values, adjust_values, print_sec=False):
        '''
            Está función instancia la clase CreateModel 
            input
               system_param: valores i, j del sistema 
               system_values: valores del sistema
               adjust_values: valores de ajuste para ecuaciones de igualdad
               print_sec: para imprimir secuencia de ejecuciones
            return
                Objeto de tipo model
        '''
        self.print_sec = print_sec
        self.system_values = system_values
        self.system_param = system_param
        self.adjust_values = adjust_values
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
        self.error = 1e-6
        self.min_trafo = 0.1
        self.m_trafo = 1
        self.max_trafo = 1.9
        self.model.name = self.system_param.get('model_name')
        self.model.i = pyomo.Set(initialize=[i for i in self.system_param.get('i')], doc='Terminal i')
        self.model.trafo = pyomo.Set(initialize=[bus for bus in self.system_param.get('bus_trafo')], doc='Bus trafo')
        self.model.ij = pyomo.Set(initialize=[ij for ij in self.system_param.get('ij')], doc='Terminal ij')
        self.model.ji = pyomo.Set(initialize=[ji for ji in self.system_param.get('ji')], doc='Terminal ji')
        self.model.a = pyomo.Set(initialize=[a for a in self.system_param.get('a')], doc='áreas')
        self.model.gen = pyomo.Set(initialize=[gen for gen in self.system_param.get('gen')], doc='Gen')
        self.model.slack = pyomo.Set(initialize=[gen for gen in self.system_param.get('slack')], doc='Slack')
        self.model.demandbid = pyomo.Set(initialize=[id_ for id_ in self.system_param.get('demandbid')], doc='Demandbid')
        self.model.bus = pyomo.Set(initialize=[bus for bus in self.system_param.get('bus')], doc='Buses')
        self.model.bus_shunt = pyomo.Set(initialize=[sht for sht in self.system_param.get('bus_shunt')], doc='Shunt')
        self.model.t = pyomo.Set(initialize=[t for t in range(1,25)], doc='Time')
        # init variables  
        self.dict_keys = {
            'init_bus_theta':'Var_V_Theta','init_bus_v':'Var_V_Vbus',
            'init_line_pij':'Var_V_LinePij','init_line_qij':'Var_V_LineQij',
            'init_line_pji':'Var_V_LinePji','init_line_qji':'Var_V_LineQji',
            'init_gen_p':'Var_V_Pgen','init_gen_q':'Var_V_Qgen','Pd':'Pd', 'Qd':'Qd',
            'init_slack_p':'Var_V_Pslack','init_slack_q':'Var_V_Qslack'
        }
    def _add_var_p_line(self):
        '''
            Está función crea la variable de potencia activa de las líneas P(i,j,c,t)
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_lineP')
        self.model.V_LinePij = pyomo.Var(
                self.model.ij,
                self.model.t, 
                within=pyomo.Reals,
                initialize=self.system_values.get('init_line_pij'), 
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
        self.model.V_LinePji = pyomo.Var(
                self.model.ji,
                self.model.t, 
                within=pyomo.Reals,
                initialize=self.system_values.get('init_line_pji'), 
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
        self.model.V_LineQij = pyomo.Var(
                self.model.ij,
                self.model.t, 
                within=pyomo.Reals,
                initialize=self.system_values.get('init_line_qij'), 
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
        self.model.V_LineQji = pyomo.Var(
                self.model.ji,
                self.model.t, 
                within=pyomo.Reals,
                initialize=self.system_values.get('init_line_qji'), 
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
                bounds=self.system_param.get('gen_bound_p'),
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
            return (self.system_param.get('gen_bound_q').get((gen,t)) 
                    if self.system_param.get('gen_bound_q').get((gen,t)) 
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
                self.model.bus_shunt,
                self.model.t, 
                within=pyomo.Integers,
                bounds=(0,5),
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
        self.model.V_Gs = pyomo.Var(
                self.model.bus,
                bounds=(0,1),
                within=pyomo.Reals,
            )
        self.model.V_Bs = pyomo.Var(
                self.model.bus,
                bounds=(0,1),
                within=pyomo.Reals,
            )
        self.model.V_Rtrafo= pyomo.Var(
                self.model.trafo,
                self.model.t,
                bounds=(self.min_trafo,self.max_trafo),
                initialize = self.m_trafo,
                within=pyomo.Reals,
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
                self.model.bus, 
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
        self.model.V_Qd_elastic = pyomo.Var(
                self.model.demandbid,
                self.model.bus, 
                self.model.t,
                within=pyomo.Reals,
                bounds=(-1,1),
                doc='potencia in gen g at time t'
            )
    def _add_power_s_constraint(self, ratio_line):
        '''
            Está función crea la restricción de potencia aparente para las líneas (i,j,c)
            imput    
                branchstatus: líneas activas del sistema
                ratio_line: capacidad máxima de potencia de las líneas del sistema
            return
                None
        '''
        def c_SLimit(model, ij, t):
                return (
                        (model.V_LinePij[ij, t])**2
                        + (model.V_LineQij[ij, t])**2
                        <= (ratio_line[ij])**2 * self.adjust_values.get('adj_slimit_sij').get((ij,t))
                    )
        if self.print_sec: print('Se agrega la restricción de potencia aparente')
        self.model.line_s_limit = pyomo.Constraint(self.model.ij,
                                                    self.model.t, 
                                                    rule=c_SLimit,
                                                    doc='Apparent power limit on line ijc')
    def _add_power_p_constraint(self, g , b):
        '''
            Está función crea la restricción de potencia activa para las líneas (i,j,c)
            imput    
                branchstatus: líneas activas del sistema
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia activa')
        def line_constraint_ij(model, ij, t):
            return (
                    (g[ij] * (model.V_Vbus[ij.split('-')[0],t]**2) 
                     / (model.V_Rtrafo[ij.split('-')[0],t] if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1)**2)
                    - (model.V_Vbus[ij[0],t] * model.V_Vbus[ij.split('-')[1],t] 
                       / (model.V_Rtrafo[ij.split('-')[0],t] if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1))
                    * (g[ij] * pyomo.cos(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]) 
                    + b[ij] * pyomo.sin(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]))
                    ==
                    model.V_LinePij[ij,t] * self.adjust_values.get('adj_line_pij').get((ij,t))
                )
        self.model.line_p_limit_ij = pyomo.Constraint(
                                        self.model.ij,
                                        self.model.t, 
                                        rule=line_constraint_ij,
                                        doc='Active power limit on line ijc'
                                    )

        def line_constraint_ji(model, ji, t):
            return (
                    g[ji] * model.V_Vbus[ji.split('-')[1],t]**2
                    - (model.V_Vbus[ji.split('-')[0],t] * model.V_Vbus[ji.split('-')[1],t] 
                       / (model.V_Rtrafo[ji.split('-')[1],t]) if self.system_param.get('bus_trafo').get(ji.split('-')[1]) else 1)
                    * (g[ji] * pyomo.cos(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t]) 
                    + b[ji] * pyomo.sin(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t]))
                    ==
                    model.V_LinePji[ji,t] * self.adjust_values.get('adj_line_pji').get((ji,t))
                )
        self.model.line_p_limit_ji = pyomo.Constraint(
                                        self.model.ji,
                                        self.model.t, 
                                        rule=line_constraint_ji,
                                        doc='Active power limit on line jic'
                                    )
    def _add_power_q_constraint(self, g , b):
        '''
            Está función crea la restricción de potencia activa para las líneas (i, j,c)
            input    
                branchstatus: líneas activas del sistema
                g: conductance
                b: susceptance,
                angle: ángulo de la linea c en i, j
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de potencia reactiva')
        def line_constraint_ij(model, ij, t):
            return (
                        - model.V_Vbus[ij.split('-')[0],t]**2 * (b[ij]) 
                        / (model.V_Rtrafo[ij.split('-')[0],t] if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1)**2
                        - model.V_Vbus[ij.split('-')[0],t] * model.V_Vbus[ij.split('-')[1],t] 
                        / (model.V_Rtrafo[ij.split('-')[0],t] if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1) 
                        * (g[ij] * pyomo.sin(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t])
                        - b[ij] * pyomo.cos(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]))
                    ==
                        model.V_LineQij[ij,t] * self.adjust_values.get('adj_line_qij').get((ij,t))
                )
        self.model.line_q_limit_ij = pyomo.Constraint(
                                        self.model.ij,
                                        self.model.t, 
                                        rule=line_constraint_ij,
                                        doc='Reactive power limit on line ijc'
                                    )
        def line_constraint_ji(model, ji, t):
            return (
                        - model.V_Vbus[ji.split('-')[1],t]**2 * (b[ji])
                        - model.V_Vbus[ji.split('-')[0],t] * model.V_Vbus[ji.split('-')[1],t] 
                        / (model.V_Rtrafo[ji.split('-')[1],t] if self.system_param.get('bus_trafo').get(ji.split('-')[1]) else 1)
                        * (g[ji] * pyomo.sin(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t])
                        - b[ji] * pyomo.cos(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji[0],t]))
                    ==
                        model.V_LineQji[ji,t] * self.adjust_values.get('adj_line_qji').get((ji,t))
            )
        self.model.line_q_limit_ji = pyomo.Constraint(
                                        self.model.ji,
                                        self.model.t, 
                                        rule=line_constraint_ji,
                                        doc='Reactive power limit on line jic'
                                    )
    def _add_p_balanced_constraint(self, genstatus, demandbidmap):
        '''
            Está función crea la restricción de balance de potencia activa
            input    
                genstatus: estado de los generadores del sistema
                demandbidmap: id de la demanda y bus en el que se conecta
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia activa')
        def balance_eqn_rule(model, bus, t):
            return (
                        abs(sum(model.V_Pgen[gen, t] for gen in self.model.gen if self.system_param.get('atBus').get((gen,bus)) and genstatus.get((gen,bus)))
                        + sum(model.V_Pslack[gen, t] for gen in self.model.slack if self.system_param.get('atBusSlack').get((gen,bus)))
                        - (self.system_values.get('Pd').get((bus,t)) if self.system_values.get('Pd').get((bus,t)) else 0)
                        #- sum(model.V_Pd_elastic[demandbid,bus] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,bus)))
                        )
                    - 
                        abs(sum(model.V_LinePij[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                        + sum(model.V_LinePji[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                        + model.V_Vbus[bus,t]**2 * model.V_Gs[bus]
                        + self.adjust_values.get('adj_p_balance').get((bus,t)))
                )<=self.error
        self.model.c_BalanceP = pyomo.Constraint(
                                        self.model.bus, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Active power balance')
    def _add_q_balanced_constraint(self, genstatus):
        '''
            Está función crea la restricción de balance de potencia reactiva
            input    
                genstatus: estado de los generadores del sistema
            return
                None
        '''
        if self.print_sec: print('Se agrega la restricción de balance de potencia reactiva')
        def balance_eqn_rule(model, bus, t):
            return (
                        abs(sum(model.V_Qgen[gen, t] for gen in self.model.gen if self.system_param.get('atBus').get((gen,bus)) and genstatus.get((gen,bus)))
                        + sum(model.V_Qslack[gen, t] for gen in self.model.slack if self.system_param.get('atBusSlack').get((gen,bus)))
                        - (self.system_values.get('Qd').get((bus,t)) if self.system_values.get('Qd').get((bus,t)) else 0))
                    -
                        abs(sum(model.V_LineQij[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                        + sum(model.V_LineQji[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                        - model.V_Vbus[bus,t]**2
                        - model.V_Vbus[bus,t]**2*(model.V_Shunt[bus, t] if self.system_param.get('bus_shunt').get(bus) else 0)
                        + self.adjust_values.get('adj_q_balance').get((bus,t)))
                )<=self.error
        self.model.c_BalanceQ = pyomo.Constraint(
                                        self.model.bus, 
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
                    + (k1)*sum((model.V_Shunt[bus, t] - model.V_Shunt[bus, t-1])**2
                        for bus in model.bus
                        for t in model.t 
                        if t >= 2 and self.system_param.get('bus_shunt').get(bus))
                    + (k2) * sum((model.V_Vbus[bus, t] - self.system_values.get('init_bus_v').get((bus, t)))**2
                        for bus in model.bus
                        for t in model.t
                        if self.system_param.get('pilot_nodes').get(bus))
                    + (k3)*sum(model.V_Qgen[gen, t]**2 
                        for gen in model.gen
                        for t in model.t)
                )
        if (self.system_param.get('system_name')=='ieee9'):
            k1, k2, k3 = 1e-4, 1e+12, 1e-12
        elif (self.system_param.get('system_name')=='ieee39'):
            k1, k2, k3 = 1e-4, 1e+12, 1e-12
        elif (self.system_param.get('system_name')=='ieee57'):
            k1, k2, k3 = 1e-4, 1e+4, 1e-32
        elif (self.system_param.get('system_name')=='ieee118'):
            k1, k2, k3 = 1e-8, 1e+4, 1e-8
        self.model.obj = pyomo.Objective(rule=obj_rule, sense = pyomo.minimize)
    def solve_model(self):
        '''
            Está función resuelve el modelo de optimización
            input    
                none
            return
                None
        '''
        system_name = self.system_param.get('system_name')
        if self.print_sec: print(f'\n--> Se inicia la solución del modelo {system_name} <--\n')
        solver = pyomo.SolverFactory('solver/bonmin', tee=True)
        solver.options['output_file'] = "bonmin.log" # Especificar el archivo de registro
        solver.options['max_iter'] = 15000
        #self.model.display()
        result = solver.solve(self.model)
        result.write()
        return True if result.solver.status.value=='ok' else False
    def save_model_variables(self):
        '''
            Está función guarda los datos del modelo de optimización
            input    
                path: ruta donde se guardan los datos
            return
                None
        '''
        variables = list(self.model.component_objects(pyomo.Var, active=True))
        if self.print_sec: print('Se guardan todas las variables...\n')
        folder = self.system_param.get('system_name')
        for e in variables:
            df = DataFrame(list(e.get_values().items()), columns=['Var','Value'])
            df.to_csv(f'Resultados/{folder}/Var_{e.name}__res.csv', index=False)
        for key, names in self.dict_keys.items():
            dict_data = {
                'Var':list(self.system_values.get(key).keys()),
                'Value':list(self.system_values.get(key).values())
            }
            df = DataFrame(dict_data)
            df.to_csv(f'Resultados/{folder}/{names}__init.csv', index=False)
                
