from _source.model import CreateModel
from _source.system import GetVariablesSystem


# istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem('ieee57')

# get las variables i, j, c del sistema
ijc_values = system._get_ijc_from_system()

# get branchstatus
branchstatus = system._get_branchstatus()
print(branchstatus)