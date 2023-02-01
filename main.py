from _source.model import CreateModel
from _source.system import GetVariablesSystem

print('\n***Inicia el script***\n')

# istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem('ieee57', print_sec=True)

# get las variables i, j, c del sistema
ijc_values = system._get_ijc_from_system()

# get branchstatus
branchstatus = system._get_branchstatus()

# get rate lines
ratio = system._get_ratio()

# instanciamos el modelo
model = CreateModel(ijc_values, print_sec=True)

# ------------ Creamos las variables del modelo ---------------#
model._add_var_p_line()
model._add_var_q_line()

# ------------ Agregamos las restricciones del modelo ---------------#
model._add_power_s_constraint(branchstatus, ratio)

