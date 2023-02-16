from _source.model import CreateModel
from _source.system import GetVariablesSystem

print('\n***Inicia el script***\n')

#** istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem('ieee57', print_sec=False)

#** ------------ Creamos las variables del sistema ---------------#
system_param = system._get_param_from_system()
system_values = system._get_values_from_system()
branchstatus = system._get_branchstatus()
genstatus = system._get_genstatus()
ratio_line = system._get_ratio_line()
ratio_trafo = system._get_ratio_trafo()
g,b = system._get_conductance_susceptance()
demandbidmap = system._get_demandbidmap()

#** instanciamos la clase para el modelo de optimización
model = CreateModel(system_param, print_sec=True)

#** -------------- Creamos las variables del modelo --------------#
model._add_var_p_line(system_values.get('init_line_p'))
model._add_var_q_line(system_values.get('init_line_q'))
model._add_var_v_bus(system_values.get('init_bus_v'))
model._add_var_theta_bus(system_values.get('init_bus_theta'))
model._add_var_p_gen(system_values.get('init_gen_p'))
model._add_var_q_gen(system_values.get('init_gen_q'))
model._add_var_Shunt_bus()
model._add_var_pd_elastic()

#** ---------- Agregamos las restricciones del modelo ------------#
model._add_power_s_constraint(branchstatus, ratio_line)
model._add_power_p_constraint(branchstatus, ratio_trafo, g, b)
model._add_power_q_constraint(branchstatus, ratio_trafo, g, b)
# model._add_p_balanced_constraint(branchstatus, genstatus, demandbidmap)
# model._add_q_balanced_constraint(branchstatus, genstatus)

#** ------------- Agregamos la función objetivo ------------------#
model._add_function_obj(system_values.get('init_bus_v'))

#** ------------------- Resolver el modelo -----------------------#
is_solve = model.solve_model()

#** ----------------- Exportando las variables -------------------#
if is_solve:
    path = r"/home/lucy/Documentos/State of Art/Resultados"
    model.save_model_variables(path)