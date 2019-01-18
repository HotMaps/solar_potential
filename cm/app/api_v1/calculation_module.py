import os
import sys
from osgeo import gdal
import numpy as np
from ..helper import generate_output_file_tif

# TODO:  chane with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)
from my_calculation_module_directory.energy_production import costs, raster_suitable
from my_calculation_module_directory.visualization import quantile_colors, line

""" Entry point of the calculation module function"""


def calculation(output_directory, inputs_raster_selection,
                inputs_parameter_selection):

    # generate the output raster file
    output_suitable = generate_output_file_tif(output_directory)

    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["solar_optimal_total"])
    ds_geo = ds.GetGeoTransform()
    irradiation_pixel_area = ds_geo[1] * (-ds_geo[5])
    irradiation_values = ds.ReadAsArray()

    # retrieve the inputs all input defined in the signature
    roof_use_factor = float(inputs_parameter_selection["roof_use_factor"])
    reduction_factor = float(inputs_parameter_selection["reduction_factor"])
    efficiency_pv = float(inputs_parameter_selection['efficiency_pv'])
    peak_power_pv = float(inputs_parameter_selection['peak_power_pv'])
    setup_costs = int(inputs_parameter_selection['setup_costs'])
    k_pv = float(inputs_parameter_selection['k_pv'])

    tot_investment = int(peak_power_pv * setup_costs)

    tot_cost_year = (float(inputs_parameter_selection['maintenance_percentage']) /
                     100 * setup_costs)

    financing_years = int(inputs_parameter_selection['financing_years'])

    discount_rate = float(inputs_parameter_selection['discount_rate'])

    # compute the indicators and the output raster

    n_plants, tot_en_gen_per_year, lcoe_plant = costs(irradiation_values, peak_power_pv, efficiency_pv, k_pv,
                    tot_investment, tot_cost_year, discount_rate,
                    financing_years, irradiation_pixel_area, roof_use_factor,
                    reduction_factor, setup_costs)

    most_suitable, n_plant_pixel, e_cum_sum = raster_suitable(roof_use_factor, peak_power_pv, efficiency_pv, k_pv,
                  irradiation_pixel_area, irradiation_values,
                  tot_en_gen_per_year)

    tot_setup_costs = setup_costs * n_plants

    out_ds = quantile_colors(most_suitable,
                             output_suitable,
                             proj=ds.GetProjection(),
                             transform=ds.GetGeoTransform(),
                             qnumb=6,
                             no_data_value=0,
                             gtype=gdal.GDT_Byte,
                             options='compress=DEFLATE TILED=YES TFW=YES'
                                     ' ZLEVEL=9 PREDICTOR=1')
    del out_ds

    # output geneneration of the output
    non_zero = np.count_nonzero(irradiation_values)
    step = int(non_zero/10)
    y_energy = e_cum_sum[0:non_zero:step]/1000000  # GWh/year
    x_cost = [(i+1) * n_plant_pixel *
              int(inputs_parameter_selection['setup_costs']) / 1000000
              for i in range(0, non_zero, step)]
    y_costant = np.ones(np.shape(y_energy)) * tot_en_gen_per_year/1000000

#    import matplotlib.pyplot as plt
#    fig = plt.figure()
#    ax = plt.axes()
#    ax.plot(x_cost, y_energy) # GWh
#    ax.plot(x_cost, y_costant) # GWh
#    fig.savefig('prova.png')
#
#    import ipdb; ipdb.set_trace()
    roof_energy = "Energy produced by covering the {p}% of roofs".format(p=roof_use_factor)
    graphics = line(x=x_cost, y_labels=['Energy production [GWh/year]',
                                        roof_energy],
                    y_values=[y_energy, y_costant])

    vector_layers = []
    result = dict()
    result['name'] = 'CM solar potential'
    result['indicator'] = [{"unit": "GWh/year",
                             "name": "Total energy production",
                             "value": str(tot_en_gen_per_year/1000000)},
                            {"unit": "Million of currency",
                            "name": "Total setup costs",
                             "value": str(tot_setup_costs/1000000)},
                            {"unit": "-",
                             "name": "Number of installed systems",
                             "value": str(n_plants)},
                            {"unit": "currency/kWh",
                             "name": "Levelized Cost of Energy",
                             "value": str(lcoe_plant)}]
    result['graphics'] = graphics
    result['vector_layers'] = vector_layers

    result['raster_layers'] = [{"name":
                                "layers of most suitable roofs",
                                "path": output_suitable}]

    return result

