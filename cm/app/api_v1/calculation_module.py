
from osgeo import gdal
from matplotlib import colors

import uuid
from ..helper import generate_output_file_tif

import numpy as np
""" Entry point of the calculation module function"""


CLRS_SUN = "#F19B03 #F6B13D #F9C774 #FDDBA3 #FFF0CE".split()
CMAP_SUN = colors.LinearSegmentedColormap.from_list('solar', CLRS_SUN)


def quantile_colors(array, output_suitable, proj, transform,
                    qnumb=6,
                    no_data_value=0,
                    no_data_color=(0, 0, 0, 255),
                    gtype=gdal.GDT_Byte,
                    options='compress=DEFLATE TILED=YES TFW=YES'
                            ' ZLEVEL=9 PREDICTOR=1',
                    cmap=CMAP_SUN):
    """Generate a GTiff categorical raster map based on quantiles
    values.
    """
    # define the quantile limits
    qvalues, qstep = np.linspace(0, 1., qnumb, retstep=True)
    valid = array != no_data_value
    quantiles = np.quantile(array[valid], qvalues)
    
    # create a categorical derived map
    array_cats = np.zeros_like(array, dtype=np.uint8)
    qv0 = quantiles[0] - 1.
    array_cats[~valid] = 0
    for i, (qk, qv) in enumerate(zip(qvalues[1:], quantiles[1:])):
        print("{}: {} < valid <= {}".format(i+1, qv0, qv))
        qindex = (qv0 < array) & (array <= qv)
        array_cats[qindex] = i + 1
        qv0 = qv

    # create a color table
    ct = gdal.ColorTable()
    ct.SetColorEntry(no_data_value, no_data_color)
    for i, clr in enumerate(cmap(qvalues)):
        r, g, b, a = (np.array(clr) * 255).astype(np.uint8)
        ct.SetColorEntry(i+1, (r, g, b, a))
    
    # create a new raster map
    gtiff_driver = gdal.GetDriverByName('GTiff')
    ysize, xsize= array_cats.shape
    
    out_ds = gtiff_driver.Create(output_suitable, 
                                 xsize, ysize,
                                 1, gtype, 
                                 options.split())
    out_ds.SetProjection(proj)
    out_ds.SetGeoTransform(transform)

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(no_data_value)
    out_ds_band.SetColorTable(ct)
    out_ds_band.WriteArray(array_cats)
    out_ds.FlushCache()
    return out_ds


#TODO: CM provider must "change this code"
#TODO: CM provider must "not change input_raster_selection,output_raster  1 raster input => 1 raster output"
#TODO: CM provider can "add all the parameters he needs to run his CM
#TODO: CM provider can "return as many indicators as he wants"
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

    # order the matix
    ind = np.unravel_index(np.argsort(en_values, axis=None)[::-1],
                           en_values.shape)
    e_cum_sum = np.cumsum(en_values[ind])
    # find the nearest element
    idx = (np.abs(e_cum_sum - tot_en_gen_per_year)).argmin()

    # create new array of zeros and ones
    most_suitable = np.zeros_like(en_values)
    for i, j in zip(ind[0][0:idx], ind[1][0:idx]):
        most_suitable[i][j] = en_values[i][j]

#    import ipdb; ipdb.set_trace()
    out_ds = quantile_colors(most_suitable, 
                             output_suitable, 
                             proj=ds.GetProjection(), 
                             transform=ds.GetGeoTransform(),
                             qnumb=6,
                             no_data_value=0, 
                             gtype=gdal.GDT_Byte,
                             options='compress=DEFLATE TILED=YES TFW=YES'
                                     ' ZLEVEL=9 PREDICTOR=1',
                             cmap=CMAP_SUN)
    del out_ds

    # output geneneration of the output
    graphics = []
    vector_layers = []
    result = dict()
    result['name'] = 'CM Heat density divider'
    result['indicator'] = [{"unit": "kWh/year",
                            "name": "Total energy production",
                            "value": str(tot_en_gen_per_year)},
                           {"unit": "currency/kWh",
                            "name": "Total setup costs",
                            "value": str(tot_setup_costs)},
                           {"unit": "currency/kWh",
                            "name": "Levelized Cost of Energy",
                            "value": str(lcoe_plant)}
                           ]
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
