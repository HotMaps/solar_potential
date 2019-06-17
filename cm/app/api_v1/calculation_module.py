import os
import sys
from osgeo import gdal
import numpy as np
import pandas as pd
import warnings
from collections import defaultdict
import reslib.pv as pv
import reslib.st as st
import reslib.plant as plant

# TODO:  change with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)
from my_calculation_module_directory.energy_production import get_plants, get_lat_long, get_raster, get_indicators
from my_calculation_module_directory.visualization import line, reducelabels
from ..helper import generate_output_file_tif
from my_calculation_module_directory.utils import best_unit

TOKEN = 'c5d1b5720336748d23f137ed7f8c9a008057f0c7'


def get_integral_error(pl, interval):
    """
    Compute the integrale of the production profile and compute
    the error with respect to the total energy production
    obtained by the raster file
    :parameter pl: plant
    :parameter interval: step over computing the integral

    :returns: the relative error
    """
    error = abs((pl.energy_production -
                 pl.prof.sum() * interval) /
                pl.energy_production) * 100
    if error[0] > 5:
        message = """Difference between raster value sum and {}
                      total energy greater than {}%""".format(pl.id,
                                                              int(error))
        warnings.warn(message)
        return message


def run_source(kind, pl, data_in,
               most_suitable,
               n_plant_raster,
               output_suitable,
               discount_rate,
               ds):
    """
    Run the simulation and get indicators for the single source
    """
    pl.financial = plant.Financial(investement_cost=int(data_in['setup_costs']
                                                        * pl.peak_power),
                                   yearly_cost=data_in['tot_cost_year'],
                                   plant_life=data_in['financing_years'])

    result = dict()
    if most_suitable.max() > 0:
        result['raster_layers'] = get_raster(most_suitable, output_suitable,
                                             ds, kind)
        result['indicator'] = get_indicators(kind, pl, most_suitable,
                                             n_plant_raster, discount_rate)

        # default profile
        tot_profile = pl.prof['output'].values * pl.n_plants
        default_profile, unit, con = best_unit(tot_profile,
                                               'kW', no_data=0,
                                               fstat=np.median,
                                               powershift=0)

        graph = line(x=reducelabels(pl.prof.index.strftime('%d-%b %H:%M')),
                     y_labels=['{} {} profile [{}]'.format(kind,
                                                           pl.resolution[1],
                                                           unit)],
                     y_values=[default_profile], unit=unit,
                     xLabel=pl.resolution[0],
                     yLabel='{} {} profile [{}]'.format(kind,
                                                        pl.resolution[1],
                                                        unit))

        # monthly profile of energy production

        df_month = pl.prof.groupby(pd.Grouper(freq='M')).sum()
        df_month['output'] = df_month['output'] * pl.n_plants
        monthly_profile, unit, con = best_unit(df_month['output'].values,
                                               'kWh', no_data=0,
                                               fstat=np.median,
                                               powershift=0)
        graph_month = line(x=df_month.index.strftime('%b'),
                           y_labels=[""""{} monthly energy
                                      production [{}]""".format(kind, unit)],
                           y_values=[monthly_profile], unit=unit,
                           xLabel="Months",
                           yLabel='{} monthly profile [{}]'.format(kind, unit))

        graphics = [graph, graph_month]

        result['graphics'] = graphics
    return result


def calculation(output_directory, inputs_raster_selection,
                inputs_parameter_selection):
    """
    Main function
    """
    # list of error messages
    # TODO: to be fixed according to CREM format
    messages = []
    # generate the output raster file
    output_suitable_pv = generate_output_file_tif(output_directory)
    output_suitable_st = generate_output_file_tif(output_directory)
    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["climate_solar_radiation"])
    ds_geo = ds.GetGeoTransform()
    irradiation_values = ds.ReadAsArray()
    irradiation_values = np.nan_to_num(irradiation_values)

    ds = gdal.Open(inputs_raster_selection["gross_floor_area"])
    ds_geo = ds.GetGeoTransform()
    pixel_area = ds_geo[1] * (-ds_geo[5])
    building_footprint = ds.ReadAsArray()
    building_footprint = np.nan_to_num(building_footprint)
    building_footprint[building_footprint > 0] = pixel_area

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

    if (pv_in['roof_use_factor'] + st_in['roof_use_factor']) > 1:
        st_in['roof_use_factor'] = 1.0 - pv_in['roof_use_factor']
        warnings.warn("""Sum of roof use factors greater than 1.
                      The roof use factor of the solar thermal has been
                      reduced to {}""".format())

    # define a pv plant with input features
    pv_plant = pv.PV_plant('PV',
                           peak_power=pv_in['peak_power'],
                           efficiency=pv_in['efficiency']
                           )
    pv_plant.k_pv = float(inputs_parameter_selection['k_pv'])
    pv_plant.area = pv_plant.area()
    # add information to get the time profile

    pv_plant_raster, most_suitable, pv_plant = get_plants(pv_plant,
                                                          pv_in['target'],
                                                          irradiation_values,
                                                          building_footprint,
                                                          pv_in['roof_use_factor'],
                                                          reduction_factor)
    pv_plant.n_plants = pv_plant_raster.sum()
    if pv_plant.n_plants > 0:
        pv_plant.lat, pv_plant.long = get_lat_long(ds, most_suitable)
        pv_plant.prof = pv_plant.profile(token=TOKEN)
        messages.append(get_integral_error(pv_plant, 1))
        pv_plant.resolution = ['Hours', 'hourly']
        res_pv = run_source('PV', pv_plant, pv_in, most_suitable,
                            pv_plant_raster,
                            output_suitable_pv,
                            discount_rate,
                            ds)
    else:
        # TODO: How to manage message
        res_pv = dict()
        warnings.warn("Not suitable pixels have been identified.")

    building_available = building_footprint - pv_plant_raster * pv_plant.area
    st_plant = st.ST_plant(id='ST',
                           area=st_in['area'],
                           efficiency=st_in['efficiency']
                           )
    # add a default peak power of 1kW in order to get raw data from ninja
    st_plant.peak_power = 1
    st_plant_raster, most_suitable, st_plant = get_plants(st_plant, st_in['target'],
                                                          irradiation_values,
                                                          building_available,
                                                          st_in['roof_use_factor'],
                                                          reduction_factor)
    st_plant.n_plants = st_plant_raster.sum()
    if st_plant.n_plants > 0:
        st_plant.lat, st_plant.long = get_lat_long(ds, most_suitable)
        st_plant.prof = st_plant.profile(mean='day', token=TOKEN)
        st_plant.resolution = ['Days', 'dayly']
        res_st = run_source('ST', st_plant, st_in, most_suitable,
                            st_plant_raster,
                            output_suitable_st,
                            discount_rate,
                            ds)
    else:
        # TODO: How to manage message
        res_st = dict()
        warnings.warn("Not suitable pixels have been identified.")
    # import ipdb; ipdb.set_trace()
    dd = defaultdict(list)
    dd['name'] = 'CM Solar Potential'
    # merge of the results
    dics = [res_pv, res_st]
    for dic in dics:
        for d in dic:
            for u in dic[d]:
                dd[d].append(u)

    print

    return dd
