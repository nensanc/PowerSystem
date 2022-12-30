

def separate(red, bus):
    # Seleccionamos las barras del área 
    red.bus = red.bus.loc[red.bus["name"].isin(bus)]
    # Seleccionamos las líneas del área
    bus_r = [i-1 for i in bus]
    red.line = red.line.loc[red.line["from_bus"].isin(bus_r) & red.line["to_bus"].isin(bus_r)]
    # Seleccionamos las cargas del área 
    red.load = red.load.loc[red.load["bus"].isin(bus_r)]
    # Seleccionamos los generadores del área
    red.gen = red.gen.loc[red.gen["bus"].isin(bus_r)]
    # Seleccionamos external grid
    red.ext_grid = red.ext_grid.loc[red.ext_grid["bus"].isin(bus)]
    # Seleccionamos los transformadores del área
    red.trafo = red.trafo.loc[red.trafo["hv_bus"].isin(bus_r) & red.trafo["lv_bus"].isin(bus_r)]
    # filtramos por Coordenadas
    red.bus_geodata = red.bus_geodata.filter(items=bus_r, axis=0)
    # filtramos por costos de generadores
    red.poly_cost = red.poly_cost.filter(items=bus_r, axis=0)
    return red