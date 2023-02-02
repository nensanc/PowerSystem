from _source.model import CreateModel
from _source.system import GetVariablesSystem

print('\n***Inicia el script***\n')

# istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem('ieee57', print_sec=True)


# ------------ Creamos las variables del sistema ---------------#
system_param = system._get_param_from_system()
branchstatus = system._get_branchstatus()
ratio = system._get_ratio()
g,b = system._get_conductance_susceptance()

# instanciamos la clase para el model ode optimización
model = CreateModel(system_param, print_sec=True)


# -------------- Creamos las variables del modelo --------------#
model._add_var_p_line()
model._add_var_q_line()
model._add_var_v_bus()
model._add_var_theta_bus()

# ------------ Agregamos las restricciones del modelo ---------------#
model._add_power_s_constraint(branchstatus, ratio)
model._add_power_p_constraint(branchstatus, ratio, g, b)

