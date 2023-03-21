import pyomo.environ as pyomo
from pandas import DataFrame
class CreateModel(object):
    '''
        Class encargada de crar el modelo de optimización
    '''
    def __init__(self, system_param, print_sec=False):
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
        self.error = 1e-8
        self.min_trafo = 1
        self.m_trafo = 3
        self.max_trafo = 5
        self.max_shunt = 5
        self.model.name = self.system_param.get('model_name')
        self.model.i = pyomo.Set(initialize=[i for i in self.system_param.get('i')], doc='Terminal i')
        self.model.trafo = pyomo.Set(initialize=[bus for bus in self.system_param.get('bus_trafo')], doc='Bus trafo')
        self.model.ij = pyomo.Set(initialize=[ij for ij in self.system_param.get('ij')], doc='Terminal ij')
        self.model.ji = pyomo.Set(initialize=[ji for ji in self.system_param.get('ji')], doc='Terminal ji')
        self.model.gen = pyomo.Set(initialize=[gen for gen in self.system_param.get('gen')], doc='Gen')
        self.model.slack = pyomo.Set(initialize=[gen for gen in self.system_param.get('slack')], doc='Slack')
        self.model.demandbid = pyomo.Set(initialize=[id_ for id_ in self.system_param.get('demandbid')], doc='Demandbid')
        self.model.bus = pyomo.Set(initialize=[bus for bus in self.system_param.get('bus')], doc='Buses')
        self.model.bus_load = pyomo.Set(initialize=[bus for bus in self.system_param.get('bus_load')], doc='Buses Load')
        self.model.bus_shunt = pyomo.Set(initialize=[sht for sht in self.system_param.get('bus_shunt')], doc='Shunt')
        self.model.border_node = pyomo.Set(initialize=[bus for bus in self.system_param.get('ward_bus')], doc='Ward Bus')
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
                doc='Real power flowing from bus i towards bus j on line c at time t'
            )
        self.model.V_LinePji = pyomo.Var(
                self.model.ji,
                self.model.t, 
                within=pyomo.Reals,
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
                doc='Reactive power flowing from bus i towards bus j on line c at time t'
            )
        self.model.V_LineQji = pyomo.Var(
                self.model.ji,
                self.model.t, 
                within=pyomo.Reals,
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
                bounds=(0.9,1.1),
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
                doc='potencia in gen g at time t'
            )
        self.model.V_Pslack = pyomo.Var(
                self.model.slack,
                self.model.t, 
                within=pyomo.Reals,
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
        self.model.V_Qgen = pyomo.Var(
                self.model.gen,
                self.model.t, 
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
        self.model.V_Qslack = pyomo.Var(
                self.model.slack,
                self.model.t, 
                within=pyomo.Reals,
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
                bounds=(-self.max_shunt,self.max_shunt),
                initialize=0,
                doc='Shunt in nodo i con sht at time t'
            )
    def _add_ward_eq_variable(self):
        '''
            Está función crea las variables de los equivalentes ward
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega la variable V_Ward_eq')
        self.model.V_Pward = pyomo.Var(
                self.model.border_node,
                self.model.t, 
                within=pyomo.Reals,
                doc='Ward value border p'
            )
        self.model.V_Qward = pyomo.Var(
                self.model.border_node,
                self.model.t, 
                within=pyomo.Reals,
                doc='Ward value border q'
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
        self.model.V_Rtrafo= pyomo.Var(
                self.model.trafo,
                self.model.t,
                bounds=(self.min_trafo,self.max_trafo),
                initialize = self.m_trafo,
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
                self.model.bus, 
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
        self.model.V_Qd_elastic = pyomo.Var(
                self.model.demandbid,
                self.model.bus, 
                self.model.t,
                within=pyomo.Reals,
                doc='potencia in gen g at time t'
            )
    def _add_param_model(self):
        '''
            Está función crea los parámetros del modelo de optimization
            input    
                None
            return
                None
        '''
        if self.print_sec: print('Se agrega los parametros del modelo')
        # Create a mutable parameter named 'c'
        self.model.Pd = pyomo.Param(
            self.model.bus_load,
            self.model.t,
            mutable=True
        )
        self.model.Qd = pyomo.Param(
            self.model.bus_load,
            self.model.t,
            mutable=True
        )
        self.model.Init_bus_v = pyomo.Param(
            self.model.bus,
            self.model.t,
            mutable=True
        )  
        self.model.Adj_p_balance = pyomo.Param(
            self.model.bus,
            self.model.t,
            mutable=True
        )
        self.model.Adj_q_balance = pyomo.Param(
            self.model.bus,
            self.model.t,
            mutable=True
        )
        self.model.Adj_slimit_sij = pyomo.Param(
            self.model.ij,
            self.model.t,
            mutable=True
        )
        self.model.Adj_line_pij = pyomo.Param(
            self.model.ij,
            self.model.t,
            mutable=True
        )
        self.model.Adj_line_pji = pyomo.Param(
            self.model.ji,
            self.model.t,
            mutable=True
        )
        self.model.Adj_line_qij = pyomo.Param(
            self.model.ij,
            self.model.t,
            mutable=True
        )
        self.model.Adj_line_qji = pyomo.Param(
            self.model.ji,
            self.model.t,
            mutable=True
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
                        <= (ratio_line[ij])**2 * model.Adj_slimit_sij[ij,t]
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
                    / (model.V_Rtrafo[ij.split('-')[0],t]**2 if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1))
                    - (model.V_Vbus[ij.split('-')[0],t] * model.V_Vbus[ij.split('-')[1],t]
                    / (model.V_Rtrafo[ij.split('-')[0],t] if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1))
                    * (g[ij] * pyomo.cos(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]) 
                    + b[ij] * pyomo.sin(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]))
                    ==
                    model.V_LinePij[ij,t] + model.Adj_line_pij[ij,t]
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
                    / (model.V_Rtrafo[ji.split('-')[1],t]**2 if self.system_param.get('bus_trafo').get(ji.split('-')[1]) else 1))
                    * (g[ji] * pyomo.cos(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t]) 
                    + b[ji] * pyomo.sin(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t]))
                    ==
                    model.V_LinePji[ji,t] + model.Adj_line_pji[ji,t]
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
        if (self.system_param.get('system_name') in ['ieee39','ieee118']):
            def line_constraint_ij(model, ij, t):
                return (
                            abs(- model.V_Vbus[ij.split('-')[0],t]**2 * (b[ij])
                            / (model.V_Rtrafo[ij.split('-')[0],t]**2 if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1)
                            - model.V_Vbus[ij.split('-')[0],t] * model.V_Vbus[ij.split('-')[1],t]
                            / (model.V_Rtrafo[ij.split('-')[0],t]**2 if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1)
                            * (g[ij] * pyomo.sin(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t])
                            - b[ij] * pyomo.cos(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t])))
                        -
                            abs(model.V_LineQij[ij,t] + model.Adj_line_qij[ij,t])
                        <= self.error
                    )
        else:
            def line_constraint_ij(model, ij, t):
                return (
                            - model.V_Vbus[ij.split('-')[0],t]**2 * (b[ij])
                            / (model.V_Rtrafo[ij.split('-')[0],t]**2 if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1)
                            - model.V_Vbus[ij.split('-')[0],t] * model.V_Vbus[ij.split('-')[1],t]
                            / (model.V_Rtrafo[ij.split('-')[0],t]**2 if self.system_param.get('bus_trafo').get(ij.split('-')[0]) else 1) 
                            * (g[ij] * pyomo.sin(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t])
                            - b[ij] * pyomo.cos(model.V_Theta[ij.split('-')[0],t] - model.V_Theta[ij.split('-')[1],t]))
                        ==
                            model.V_LineQij[ij,t] + model.Adj_line_qij[ij,t]
                    )
        self.model.line_q_limit_ij = pyomo.Constraint(
                                        self.model.ij,
                                        self.model.t, 
                                        rule=line_constraint_ij,
                                        doc='Reactive power limit on line ijc'
                                    )
        if (self.system_param.get('system_name') in ['ieee39','ieee118']):
            def line_constraint_ji(model, ji, t):
                return (
                            abs(- model.V_Vbus[ji.split('-')[1],t]**2 * (b[ji])
                            - model.V_Vbus[ji.split('-')[0],t] * model.V_Vbus[ji.split('-')[1],t]
                            / (model.V_Rtrafo[ji.split('-')[1],t]**2 if self.system_param.get('bus_trafo').get(ji.split('-')[1]) else 1)
                            * (g[ji] * pyomo.sin(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t])
                            - b[ji] * pyomo.cos(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t])))
                        -
                            abs(model.V_LineQji[ji,t] + model.Adj_line_qji[ji,t])
                        <= self.error
                    )
        else:
            def line_constraint_ji(model, ji, t):
                return (
                            - model.V_Vbus[ji.split('-')[1],t]**2 * (b[ji])
                            - model.V_Vbus[ji.split('-')[0],t] * model.V_Vbus[ji.split('-')[1],t]
                            / (model.V_Rtrafo[ji.split('-')[1],t]**2 if self.system_param.get('bus_trafo').get(ji.split('-')[1]) else 1)
                            * (g[ji] * pyomo.sin(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t])
                            - b[ji] * pyomo.cos(model.V_Theta[ji.split('-')[1],t] - model.V_Theta[ji.split('-')[0],t]))
                        ==
                            model.V_LineQji[ji,t] + model.Adj_line_qji[ji,t]
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
                        - (model.Pd[bus,t] if self.system_param.get('bus_load').get(bus) else 0)
                        - sum(model.V_Pd_elastic[demandbid,bus] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,bus)))
                        #- (model.V_Pward[bus,t] if self.system_param.get('ward_bus').get(bus) else 0)
                        )
                    - 
                        abs(sum(model.V_LinePij[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                        + sum(model.V_LinePji[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                        + model.V_Vbus[bus,t]**2 * model.V_Gs[bus]
                        + model.Adj_p_balance[bus,t])
                )<=self.error
        self.model.c_BalanceP = pyomo.Constraint(
                                        self.model.bus, 
                                        self.model.t, 
                                        rule=balance_eqn_rule,
                                        doc='Active power balance')
    def _add_q_balanced_constraint(self, genstatus, demandbidmap):
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
                        abs(
                        sum(model.V_Qgen[gen, t] for gen in self.model.gen if self.system_param.get('atBus').get((gen,bus)) and genstatus.get((gen,bus)))
                        + sum(model.V_Qslack[gen, t] for gen in self.model.slack if self.system_param.get('atBusSlack').get((gen,bus)))
                        - model.Qd[bus,t] if self.system_param.get('bus_load').get(bus) else 0
                        - sum(model.V_Qd_elastic[demandbid,bus] for demandbid in self.model.demandbid if demandbidmap.get((demandbid,bus)))
                        - (model.V_Qward[bus,t] if self.system_param.get('ward_bus').get(bus) else 0)
                        )
                    -
                        abs(sum(model.V_LineQij[ij,t] for ij in self.system_param.get('branchij_bus').get(bus, {}))
                        + sum(model.V_LineQji[ji,t] for ji in self.system_param.get('branchji_bus').get(bus, {}))
                        - model.V_Vbus[bus,t]**2
                        - model.V_Vbus[bus,t]**2*(model.V_Shunt[bus, t]/self.max_shunt if self.system_param.get('bus_shunt').get(bus) else 0)
                        + model.Adj_q_balance[bus,t]
                        )
                   <=self.error
            )
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
                    + (k1) * sum((model.V_Shunt[bus, t] - model.V_Shunt[bus, t-1])**2
                        for bus in model.bus
                        for t in model.t 
                        if t >= 2 and self.system_param.get('bus_shunt').get(bus))
                    + (k2) * sum((model.V_Vbus[bus, t] - model.Init_bus_v[bus, t])**2
                        for bus in model.bus
                        for t in model.t
                        if self.system_param.get('pilot_nodes').get(bus))
                    + (k3)*sum(model.V_Qgen[gen, t]**2 
                        for gen in model.gen
                        for t in model.t)
                )
        if (self.system_param.get('system_name')=='ieee9'):
            k1, k2, k3 = 1e-2, 3e+2, 1e+1
        elif (self.system_param.get('system_name')=='ieee39'):
            k1, k2, k3 = 1e-2, 3e+2, 1e+1
        elif (self.system_param.get('system_name')=='ieee57'):
            k1, k2, k3 = 1e-2, 3e+2, 1e+1
        elif (self.system_param.get('system_name')=='ieee118'):
            k1, k2, k3 = 1e-2, 3e+2, 1e+1
        if self.print_sec: print(f'k1: {k1} - k2: {k2} - k3: {k3}')
        self.model.obj = pyomo.Objective(rule=obj_rule, sense = pyomo.minimize)
    def _set_variables_model(self, system_values):
        '''
            Está función cambia cambia los valores de bounds y inicializaciones de todas las variables
            input    
                none
            return
                None
        '''
        #if self.print_sec: print('Se agrega la inicialización y los bounds')
        def change_bounds(model_var, dict_values):
            for var,value in dict_values.items():
                model_var[var].setlb(value[0])
                model_var[var].setub(value[1])
        def change_initialize(model_var, dict_values):
            for var,value in dict_values.items():
                model_var[var].set_value(value)
        def initialize_param(model_param, dict_values):
            for var,value in dict_values.items():
                model_param[var].set_value(value)
        # para lineas pij
        change_bounds(self.model.V_LinePij, system_values.get('bound_line_pij'))
        change_initialize(self.model.V_LinePij, system_values.get('init_line_pij'))
        change_bounds(self.model.V_LinePji, system_values.get('bound_line_pji'))
        change_initialize(self.model.V_LinePji, system_values.get('init_line_pji'))
        # para lineas qij
        change_initialize(self.model.V_LineQij, system_values.get('init_line_qij'))
        change_initialize(self.model.V_LineQji, system_values.get('init_line_qji'))
        # para buses V
        change_initialize(self.model.V_Vbus, system_values.get('init_bus_v'))
        # para buses theta 
        change_initialize(self.model.V_Theta, system_values.get('init_bus_theta'))
        # para gen p
        change_initialize(self.model.V_Pgen, system_values.get('init_gen_p'))
        change_initialize(self.model.V_Pslack, system_values.get('init_slack_p'))
        # para gen q
        change_bounds(self.model.V_Qgen, system_values.get('gen_bound_q'))
        change_initialize(self.model.V_Qgen, system_values.get('init_gen_q'))
        change_initialize(self.model.V_Qslack, system_values.get('init_slack_q'))
        # ward values 
        initialize_param(self.model.V_Pward, system_values.get('bus_ward_p'))
        initialize_param(self.model.V_Qward, system_values.get('bus_ward_q'))
        # para parametros
        initialize_param(self.model.Pd, system_values.get('Pd'))
        initialize_param(self.model.Qd, system_values.get('Qd'))
        initialize_param(self.model.Init_bus_v, system_values.get('init_bus_v'))
    def _set_adjust_values(self, adjust_values):
        '''
            Está función cambia cambia los valores de inicializaciones de todas los parametros
            input    
                none
            return
                None
        '''
        def initialize_param(model_param, dict_values):
            for var,value in dict_values.items():
                model_param[var].set_value(value)
        initialize_param(self.model.Adj_line_pij, adjust_values.get('adj_line_pij'))
        initialize_param(self.model.Adj_line_pji, adjust_values.get('adj_line_pji'))
        initialize_param(self.model.Adj_line_qij, adjust_values.get('adj_line_qij'))
        initialize_param(self.model.Adj_line_qji, adjust_values.get('adj_line_qji'))
        initialize_param(self.model.Adj_p_balance, adjust_values.get('adj_p_balance'))
        initialize_param(self.model.Adj_q_balance, adjust_values.get('adj_q_balance'))
        initialize_param(self.model.Adj_slimit_sij, adjust_values.get('adj_slimit_sij'))
    def solve_model(self, area):
        '''
            Está función resuelve el modelo de optimización
            input    
                none
            return
                None
        '''
        system_name = self.system_param.get('system_name')
        if self.print_sec: print(f'\n--> Se inicia la solución del modelo {system_name} - area {area} <--\n')
        solver = pyomo.SolverFactory('solver/bonmin', tee=True)
        solver.options['output_file'] = "bonmin.log" # Especificar el archivo de registro
        solver.options['max_iter'] = 1000
        solver.options['bonmin.integer_tolerance'] = 1e-5
        solver.options['bonmin.allowable_fraction_gap'] = 1e-5
        solver.options['bonmin.allowable_gap'] = 1e-5
        solver.options['bonmin.algorithm'] = 'B-OA'
        result = solver.solve(self.model)
        result.write()
        return True if result.solver.status.value=='ok' else False
    def save_model_variables(self, area, system_values):
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
            df.to_csv(f'ResultadosAreas/{folder}/Var_{e.name}_area_{area}__res.csv', index=False)
        for key, names in self.dict_keys.items():
            dict_data = {
                'Var':list(system_values.get(key).keys()),
                'Value':list(system_values.get(key).values())
            }
            df = DataFrame(dict_data)
            df.to_csv(f'ResultadosAreas/{folder}/{names}_area_{area}__init.csv', index=False)
                