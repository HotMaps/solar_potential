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
from my_calculation_module_directory.energy_production import indicators, raster_suitable, mean_plant
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
    discount_rate = float(inputs_parameter_selection['discount_rate'])

    pv_plant = mean_plant(inputs_parameter_selection)

    n_plants, n_plant_pixel, pv_plant = indicators(irradiation_values,
                                                   irradiation_pixel_area,
                                                   roof_use_factor,
                                                   reduction_factor/100,
                                                   pv_plant)

    lcoe_plant = pv_plant.financial.lcoe(pv_plant.energy_production,
                                         i_r=discount_rate/100)

    tot_en_gen_per_year = n_plants * pv_plant.energy_production

    most_suitable, e_cum_sum = raster_suitable(n_plant_pixel,
                                               tot_en_gen_per_year,
                                               irradiation_values,
                                               pv_plant)

    tot_setup_costs = pv_plant.financial.investement_cost * n_plants

    out_ds, symbology = quantile_colors(most_suitable,
                                        output_suitable,
                                        proj=ds.GetProjection(),
                                        transform=ds.GetGeoTransform(),
                                        qnumb=6,
                                        no_data_value=0,
                                        gtype=gdal.GDT_Byte,
                                        options='compress=DEFLATE TILED=YES '
                                                'TFW=YES '
                                                'ZLEVEL=9 PREDICTOR=1')
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
    roof_energy = "Energy produced by covering the {p}% of roofs".format(p=reduction_factor)
    graphics = [line(x=x_cost, y_labels=['Energy production [GWh/year]',
                                        roof_energy],
                    y_values=[y_energy, y_costant])]

    # vector_layers = []
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
    #result['vector_layers'] = vector_layers

    result['raster_layers'] = [
        {
          "name": "layers of most suitable roofs",
          "path": output_suitable,
          "type": "custom",
          "symbology": symbology
        }
    ]
    # import ipdb; ipdb.set_trace()
    return result
