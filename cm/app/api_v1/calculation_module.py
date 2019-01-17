
from osgeo import gdal
import uuid
from ..helper import generate_output_file_tif

import numpy as np
""" Entry point of the calculation module function"""

#TODO: CM provider must "change this code"
#TODO: CM provider must "not change input_raster_selection,output_raster  1 raster input => 1 raster output"
#TODO: CM provider can "add all the parameters he needs to run his CM
#TODO: CM provider can "return as many indicators as he wants"


def line(x, xlabel, **kwargs):
    """
    Define the dictionary for defining a multiline plot
    :param x: list of x data
    :param xlabel: string with x label
    :param ylabels: list of strings with y labels of dataset
    :param **kwargs: lists of dataset with their names
    :returns: the dictionary for the app
    """
    dic = []
    for key, value in kwargs.items():
        dic.append({
                    "label": "Calculation module chart",
                    "backgroundColor": ["#3e95cd"],
                    "data": [2478, 5267, 734, 784, 433]})

    graph = {"type": "line",
             "data": {"data": x,
                      "datasets": dic}
             }
    return graph


def lcoe(tot_investment, tot_cost_year, n, i_r, en_gen_per_year):
    """
    Levelized cost of Energy

    Tot_investment = Total investment ( Outflow everything is
                     included in this voice,
    plese refer to the Excel spreadsheet made by Simon) [positive real number]

    Tot_cost_year =  (Outflow) variable cost [positive real number]

    n number of years    [Natural number or positive integer]

    i_r discount rate [0.0< positive real number<1.0]

    EN_gen_per_year = total energy generated during a year
                      [KWH/Y] [ positive real number]
    -- computed as

    Nominal capacity * COP * Load or apacity factor  in whch

    Nominal capacity [KW]
    Hours per year [H/y = hours/year]

    test: geothermal savings oil

    >>> LCOE( 7473340,   4918, 27, 0.03,  6962999)
    0.05926970484809364

    test: geothermal savings gas
    """

    flows = []
    flows.append(float(tot_investment))

    for i in range(1, int(n)+1):

        flow_k = tot_cost_year*np.power(float(1+float(i_r)), float(-i))
        flows.append(float(flow_k))

    tot_inv_and_sum_annual_discounted_costs = sum(flows)

    discounted_ener = []

    for i in range(1, int(n)+1):
        discounted_ener_k = en_gen_per_year*np.power(float(1+float(i_r)), float(-i))
        discounted_ener.append(discounted_ener_k)

    total_discounted_energy = sum(discounted_ener)

    lcoe = tot_inv_and_sum_annual_discounted_costs/total_discounted_energy

    return lcoe


def calculation(output_directory, inputs_raster_selection,
                inputs_parameter_selection):
    # TODO the folowing code must be changed by
    # the code of the calculation module

    # generate the output raster file
    output_suitable = generate_output_file_tif(output_directory)

    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["solar_optimal_total"])
    ds_band = ds.GetRasterBand(1)
    ds_geo = ds.GetGeoTransform()
    irradiation_pixel_area = ds_geo[1] * (-ds_geo[5])
    irradiation_values = ds.ReadAsArray()
    # retrieve the inputs all input defined in the signature
    roof_use_factor = float(inputs_parameter_selection["roof_use_factor"])
    reduction_factor = float(inputs_parameter_selection["reduction_factor"])
    efficiency_pv = float(inputs_parameter_selection['efficiency_pv'])
    peak_power_pv = float(inputs_parameter_selection['peak_power_pv'])

    tot_investment = (inputs_parameter_selection['peak_power_pv'] *
                      int(inputs_parameter_selection['setup_costs']))

    tot_cost_year = (float(inputs_parameter_selection['maintenance_percentage'] )/
                     100 *
                     int(inputs_parameter_selection['setup_costs']))

    e_pv_mean = np.mean(np.nonzero(irradiation_values))
    # the solar irradiation at standard test condition equal to 1 kWm-2
    en_gen_per_year = (e_pv_mean *
                       float(inputs_parameter_selection['peak_power_pv']) *
                       float(inputs_parameter_selection['efficiency_pv']))
    # compute lcoe for a single representative plant
    lcoe_plant = lcoe(tot_investment, tot_cost_year,
                      inputs_parameter_selection['financing_years'],
                      inputs_parameter_selection['discount_rate'],
                      en_gen_per_year)

    area_plant = float(float(inputs_parameter_selection['peak_power_pv']) /
                  float(inputs_parameter_selection['k_pv']))

    building_footprint = float(np.count_nonzero(irradiation_values) *
                          irradiation_pixel_area)

    n_plants = roof_use_factor * reduction_factor * building_footprint / area_plant


    tot_setup_costs = int(inputs_parameter_selection['setup_costs']) * n_plants
    tot_en_gen_per_year = en_gen_per_year * n_plants

    # define the most suitable roofs,
    # compute the energy for each pixel by considering a number of plants
    # for each pixel and selected
    # most suitable pixel to cover the enrgy production
    # TODO: do not consider 0 values in the computation

    # n_plant_pixel potential number of plants in a pixel
    n_plant_pixel = (irradiation_pixel_area/area_plant *
                     roof_use_factor)
    en_values = (irradiation_values *
                 peak_power_pv *
                 efficiency_pv * n_plant_pixel
                 )

    # order the matrix
    ind = np.unravel_index(np.argsort(en_values, axis=None)[::-1],
                           en_values.shape)
    e_cum_sum = np.cumsum(en_values[ind])
    # find the nearest element
    idx = (np.abs(e_cum_sum - tot_en_gen_per_year)).argmin()

    # create new array of zeros and ones
    most_suitable = np.zeros_like(en_values)
    for i, j in zip(ind[0][0:idx], ind[1][0:idx]):
        most_suitable[i][j] = en_values[i][j]
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(output_suitable, ds_band.XSize, ds_band.YSize,
                                 1, gdal.GDT_UInt16, ['compress=DEFLATE',
                                                      'TILED=YES',
                                                      'TFW=YES',
                                                      'ZLEVEL=9',
                                                      'PREDICTOR=1'])
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0, 0, 0, 255))
    ct.SetColorEntry(1, (110, 220, 110, 255))
    out_ds.GetRasterBand(1).SetColorTable(ct)

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(0)
    out_ds_band.WriteArray(most_suitable)

    del out_ds
    # output geneneration of the output
    graphics = []
    vector_layers = []
    result = dict()
    result['name'] = 'CM solar potential'
    result['indicators'] = [{"unit": "MWh/year",
                             "name": "Total energy production",
                             "value": str(tot_en_gen_per_year/1000)},
                            {"unit": "currency",
                            "name": "Total setup costs",
                             "value": str(tot_setup_costs)},
                            {"unit": "currency/kWh",
                             "name": "Levelized Cost of Energy",
                             "value": str(lcoe_plant)}]
    result['graphics'] = graphics
    result['vector_layers'] = vector_layers

    result['raster_layers'] = [{"name":
                                "layers of most suitable roofs",
                                "path": output_suitable}]

    return result


def colorizeMyOutputRaster(out_ds):
    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0,0,0,255))
    ct.SetColorEntry(1, (110,220,110,255))
    out_ds.SetColorTable(ct)
    return out_ds
