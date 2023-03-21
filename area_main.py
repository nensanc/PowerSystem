from _source.area_system import GetVariablesSystem
from _source.area_model import CreateModel
print('\n***Inicia el script***\n')
areas = 3
dict_models, dict_net_eq, dict_system = {}, {}, {}
area = 2
for area_ in range(1,areas+1):
    print(f'\n\nCreando el modelo para el área: {area}\n')
    #** istanciamos la clase para obtener las variables del sistema
    system = GetVariablesSystem(
        ['ieee9', 'ieee39', 'ieee57', 'ieee118'][0], 
        print_sec=False
    )
    # get the ward equivalent
    net_eq = system._get_ward_eq_from_system(area)
    #** ------------ Creamos las variables del sistema ---------------#
    system_param = system._get_param_from_system(net_eq)
    genstatus = system._get_genstatus(net_eq)
    ratio_line = system._get_ratio_line(net_eq)
    ratio_trafo = system._get_ratio_trafo(net_eq)
    g, b = system._get_conductance_susceptance(net_eq)
    demandbidmap = system._get_demandbidmap(net_eq)   

    #** instanciamos la clase para el modelo de optimización
    model = CreateModel(system_param, print_sec=True)

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
    model._add_param_model()
    model._add_ward_eq_variable()

    #** ---------- Agregamos las restricciones del modelo ------------#
    model._add_power_s_constraint(ratio_line)
    model._add_power_p_constraint(g,b)
    model._add_power_q_constraint(g, b)
    model._add_p_balanced_constraint(genstatus, demandbidmap)
    model._add_q_balanced_constraint(genstatus, demandbidmap)

    #** ------------- Agregamos la función objetivo ------------------#
    model._add_function_obj()

    #** ------------- Guardamos las variables de interes ------------------#
    dict_models[area] = model
    dict_system[area] = system
    break

for area_ in range(1,areas+1):
    #**-- Cargamos el modelo y agregamos la inicialización y bounds --#
    model = dict_models.get(area)
    system_values = dict_system.get(area)._get_values_from_system(
                        area
                    )
    model._set_variables_model(system_values)
    model._set_adjust_values(
        dict_system.get(area)._get_adjust_values()
    )

    #** ------------------- Resolver el modelo -----------------------#
    is_solve = model.solve_model(area)

    #** ----------------- Exportando las variables -------------------#
    if is_solve: model.save_model_variables(area, system_values)
    break
