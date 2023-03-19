from _source.area_system import GetVariablesSystem
from _source.area_model import CreateModel
print('\n***Inicia el script***\n')

#** istanciamos la clase para obtener las variables del sistema
system = GetVariablesSystem('ieee9', print_sec=False)

dict_init_param = {}
for area in system.sep_areas:
    # get the ward equivalent
    net_eq, ward_borders_p, ward_borders_q = system._get_ward_eq_from_system(area=area)

    #** ------------ Creamos las variables del sistema ---------------#
    dict_init_param[f'system_param_a{area}'] = system._get_param_from_system(net_eq)
    dict_init_param[f'genstatus_a{area}'] = system._get_genstatus(net_eq)
    dict_init_param[f'ratio_line_a{area}'] = system._get_ratio_line(net_eq)
    dict_init_param[f'ratio_trafo_a{area}'] = system._get_ratio_trafo(net_eq)
    g, b = system._get_conductance_susceptance(net_eq)
    dict_init_param[f'g_a{area}'] = g
    dict_init_param[f'b_a{area}'] = b
    dict_init_param[f'demandbidmap_a{area}'] = system._get_demandbidmap(net_eq)   

for area in system.sep_areas:
    system_values = system._get_values_from_system()
    adjust_values = system._get_adjust_values()

    #** instanciamos la clase para el modelo de optimización
    model = CreateModel(
            dict_init_param.get(f'system_param_a{area}'), 
            system_values, 
            adjust_values, 
            print_sec=False
    )

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
    model._add_power_s_constraint(dict_init_param.get(f'ratio_line_a{area}'))
    model._add_power_p_constraint(
        dict_init_param.get(f'g_a{area}'), 
        dict_init_param.get(f'b_a{area}')
        )
    model._add_power_q_constraint(
        dict_init_param.get(f'a_a{area}'), 
        dict_init_param.get(f'b_a{area}')
        )
    model._add_p_balanced_constraint(
        dict_init_param.get(f'genstatus_a{area}') , 
        dict_init_param.get(f'demandbidmap_a{area}')
        )
    model._add_q_balanced_constraint(
        dict_init_param.get(f'genstatus_a{area}')
        )

    #** ------------- Agregamos la función objetivo ------------------#
    model._add_function_obj()

    #** ------------------- Resolver el modelo -----------------------#
    is_solve = model.solve_model()

    #** ----------------- Exportando las variables -------------------#
    if is_solve: model.save_model_variables()
