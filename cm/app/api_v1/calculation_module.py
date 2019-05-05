import os
import sys
from osgeo import gdal
import numpy as np
import pandas as pd
import warnings

# TODO:  change with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)
from my_calculation_module_directory.energy_production import get_plants, get_profile, get_raster, get_indicators
from my_calculation_module_directory.visualization import line, reducelabels
from ..helper import generate_output_file_tif
from my_calculation_module_directory.utils import best_unit
import my_calculation_module_directory.plants as plant


def run_source(kind, pl, data_in,
               irradiation_values,
               building_footprint,
               reduction_factor,
               output_suitable,
               discount_rate,
               ds,
               ds_geo):
    """
    Run the simulation and get indicators for the single source
    """
    pl.financial = plant.Financial(investement_cost=int(pl.peak_power *
                                                        data_in['setup_costs']),
                                   yearly_cost=data_in['tot_cost_year'],
                                   plant_life=data_in['financing_years'])

    n_plant_raster, most_suitable = get_plants(pl, data_in['target'],
                                               irradiation_values,
                                               building_footprint,
                                               data_in['roof_use_factor'],
                                               reduction_factor)

    result = dict()
    result['name'] = 'CM Solar Potential'
    if most_suitable.max() > 0:
        result['raster_layers'] = get_raster(most_suitable, output_suitable,
                                             ds)
        result['indicator'] = get_indicators(kind, pl, most_suitable,
                                             n_plant_raster, discount_rate)
        pv_profile = get_profile(irradiation_values, ds,
                                 most_suitable, n_plant_raster, pl)

        # hourl profile

        hourly_profile, unit, con = best_unit(pv_profile['output'].values,
                                              'kW', no_data=0,
                                              fstat=np.median,
                                              powershift=0)

        graph_hours = line(x= reducelabels(pv_profile.index.strftime('%d-%b %H:%M')),
                           y_labels=['PV hourly profile [{}]'.format(unit)],
                           y_values=[hourly_profile], unit=unit,
                           xLabel="Hours",
                           yLabel='PV hourly profile [{}]'.format(unit))

        # monthly profile of energy production

        df_month = pv_profile.groupby(pd.Grouper(freq='M')).sum()
        monthly_profile, unit, con = best_unit(df_month['output'].values,
                                               'kWh', no_data=0,
                                               fstat=np.median,
                                               powershift=0)
        graph_month = line(x=df_month.index.strftime('%b'),
                           y_labels=['PV monthly energy production [{}]'.format(unit)],
                           y_values=[monthly_profile], unit=unit,
                           xLabel="Months",
                           yLabel='PV monthly profile [{}]'.format(unit))

        graphics = [graph_hours, graph_month]

        result['graphics'] = graphics

    else:
        # TODO: How to manage message
        result = dict()
        warnings.warn("Not suitable pixels have been identified.")
    return result


def calculation(output_directory, inputs_raster_selection,
                inputs_parameter_selection):
    """
    Main function
    """
    # generate the output raster file
    output_suitable = generate_output_file_tif(output_directory)

    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["solar_optimal_total"])
    ds_geo = ds.GetGeoTransform()
    irradiation_pixel_area = ds_geo[1] * (-ds_geo[5])
    irradiation_values = ds.ReadAsArray()
    irradiation_values = np.nan_to_num(irradiation_values)

    # retrieve the inputs all input defined in the signature
    pv_in = {'roof_use_factor':
             float(inputs_parameter_selection["roof_use_factor_pv"]),
             'target': float(inputs_parameter_selection["PV_target"]),
             'setup_costs': int(inputs_parameter_selection['setup_costs_pv']),
             'tot_cost_year':
             (float(inputs_parameter_selection['maintenance_percentage_pv']) /
              100 * int(inputs_parameter_selection['setup_costs_pv'])),
             'financing_years': int(inputs_parameter_selection['financing_years']),
             'efficiency': float(inputs_parameter_selection['efficiency_pv']),
             'peak_power': float(inputs_parameter_selection['peak_power_pv'])
             }
    st_in = {'roof_use_factor':
             float(inputs_parameter_selection["roof_use_factor_st"]),
             'target': float(inputs_parameter_selection["ST_target"]),
             'setup_costs': int(inputs_parameter_selection['setup_costs_st']),
             'tot_cost_year':
             (float(inputs_parameter_selection['maintenance_percentage_st']) /
              100 * int(inputs_parameter_selection['setup_costs_st'])),
             'financing_years': int(inputs_parameter_selection['financing_years']),
             'efficiency': float(inputs_parameter_selection['efficiency_pv']),
             'area': float(inputs_parameter_selection['area_st'])
             }

    reduction_factor = float(inputs_parameter_selection["reduction_factor"])
    discount_rate = float(inputs_parameter_selection['discount_rate'])
    # TODO:the building footprint is now equal to the pixel area
    building_footprint = np.zeros(irradiation_values.shape)
    building_footprint[irradiation_values > 0] = irradiation_pixel_area

    if (pv_in['roof_use_factor'] + st_in['roof_use_factor']) > 1:
        st_in['roof_use_factor'] = 1.0 - pv_in['roof_use_factor']
        warnings.warn("""Sum of roof use factors greater than 1.
                      The roof use factor of the solar thermal has been
                      reduced to {}""".format())

    # define a pv plant with input features
    pv_plant = plant.PV_plant('mean',
                              peak_power=pv_in['peak_power'],
                              efficiency=pv_in['efficiency']
                              )
    pv_plant.k_pv = float(inputs_parameter_selection['k_pv'])
    pv_plant.area = pv_plant.area()

    # define a st plant with input features
#
#    st_plant = plant.PV_plant('mean',
#                              area=st_in['area'],
#                              efficiency=st_in['efficiency']
#                              )
#    st_plant.financial = plant.Financial(investement_cost=int(st_plant.area *
#                                                              st_in['setup_costs']),
#                                         yearly_cost=st_in['tot_cost_year'],
#                                         plant_life=financing_years)

    result = run_source('PV', pv_plant, pv_in,
                        irradiation_values, building_footprint,
                        reduction_factor, output_suitable, discount_rate,
                        ds, ds_geo)

    # import ipdb; ipdb.set_trace()
    return result
