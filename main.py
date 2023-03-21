from _source.model import CreateModel
from _source.system import GetVariablesSystem
print('\n***Inicia el script***\n')

#** istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem(
    ['ieee9', 'ieee39', 'ieee57', 'ieee118'][0], 
    print_sec=False
)

#** ------------ Creamos las variables del sistema ---------------#
system_param = system._get_param_from_system()
system_values = system._get_values_from_system()
genstatus = system._get_genstatus()
ratio_line = system._get_ratio_line()
ratio_trafo = system._get_ratio_trafo()
g, b = system._get_conductance_susceptance()
demandbidmap = system._get_demandbidmap()   
adjust_values = system._get_adjust_values()

#** instanciamos la clase para el modelo de optimización
model = CreateModel(system_param, system_values, adjust_values, print_sec=True)

#** -------------- Creamos las variables del modelo --------------#
model.init_model()
model._add_var_p_line()
model._add_var_q_line()
model._add_var_v_bus()
model._add_var_theta_bus()
model._add_var_p_gen()
model._add_var_q_gen()
model._add_var_Shunt_bus()
model._add_var_pd_elastic()
model._add_var_slack_variable()

#** ---------- Agregamos las restricciones del modelo ------------#
model._add_power_s_constraint(ratio_line)
model._add_power_p_constraint(g, b)
model._add_power_q_constraint(g, b)
model._add_p_balanced_constraint(genstatus, demandbidmap)
model._add_q_balanced_constraint(genstatus, demandbidmap)

#** ------------- Agregamos la función objetivo ------------------#
model._add_function_obj()

#** ------------------- Resolver el modelo -----------------------#
is_solve = model.solve_model()

#** ----------------- Exportando las variables -------------------#
if is_solve: model.save_model_variables()