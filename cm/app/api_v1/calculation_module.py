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
from my_calculation_module_directory.utils import best_unit, xy2latlong
from my_calculation_module_directory.time_profiles import pv_profile

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
    irradiation_values = np.nan_to_num(irradiation_values)

    # retrieve the inputs all input defined in the signature
    roof_use_factor = float(inputs_parameter_selection["roof_use_factor"])
    reduction_factor = float(inputs_parameter_selection["reduction_factor"])
    discount_rate = float(inputs_parameter_selection['discount_rate'])
    PV_target = float(inputs_parameter_selection["PV_target"])

    pv_plant = mean_plant(inputs_parameter_selection)
    
    # TODO:the building footprint is now equal to the pixel area
    building_footprint = np.zeros(irradiation_values.shape)
    building_footprint[irradiation_values>0] = irradiation_pixel_area
    
    n_plants, pv_plant = indicators(PV_target,
                                    irradiation_values,
                                    building_footprint,
                                    roof_use_factor,
                                    reduction_factor/100,
                                    pv_plant)
    
    tot_en_gen_per_year = n_plants * pv_plant.energy_production
    
    # compute the raster with the number of plant per pixel
    n_plant_raster = (building_footprint/pv_plant.area() * roof_use_factor *
                      reduction_factor / 100)
    n_plant_raster = n_plant_raster.astype(int)
    
    most_suitable, e_cum_sum = raster_suitable(n_plant_raster,
                                               tot_en_gen_per_year,
                                               irradiation_values,
                                               pv_plant)
    # TODO: I am creating a raster with the number of plants in a pixel,
    # this will be obtained as a transformation of the input file with 
    # square mater available from building footprint

    most_suitable, unit, factor = best_unit(most_suitable,
                                            current_unit="kWh/pixel/year",
                                            no_data=0, fstat=np.min,
                                            powershift=0)

    # fix e_cum_sum to have the same unit
    # if sum the unit is not for pixel
    # TODO: this is a brutal change by deleting pixel
    unit_sum = unit.replace("/pixel", "")
    e_cum_sum = e_cum_sum * factor
    tot_en_gen_per_year = tot_en_gen_per_year * factor

    tot_setup_costs = pv_plant.financial.investement_cost * n_plants

    out_ds, symbology = quantile_colors(most_suitable,
                                        output_suitable,
                                        proj=ds.GetProjection(),
                                        transform=ds.GetGeoTransform(),
                                        qnumb=6,
                                        no_data_value=0,
                                        gtype=gdal.GDT_Byte,
                                        unit=unit,
                                        options='compress=DEFLATE TILED=YES '
                                                'TFW=YES '
                                                'ZLEVEL=9 PREDICTOR=1')
    del out_ds

    # look for the post representative point
    e_pv_mean = irradiation_values[most_suitable>0].mean()
    
    # reclassifiy array
    bins = 3
    e_bins = np.histogram(irradiation_values[most_suitable>0], bins=bins)
    n_plant_bins = [n_plant_raster[(irradiation_values >= e_bins[1][0]) &
                                   (irradiation_values <= e_bins[1][1])].sum()]
    for low, high in zip(e_bins[1][1:-1], e_bins[1][2:]):
        n_plant_bins.append(n_plant_raster[(irradiation_values > low) &
                                           (irradiation_values <= high)].sum())
    pv_plant.energy_production =  pv_plant.compute_energy(e_pv_mean)
    lcoe_plant = pv_plant.financial.lcoe(pv_plant.energy_production,
                                         i_r=discount_rate/100)

    i, j = np.unravel_index((np.abs(most_suitable - e_pv_mean)).argmin(),
                            (np.abs(most_suitable - e_pv_mean)).shape)
    x = ds_geo[0] + i * ds_geo[1] 
    y = ds_geo[3] + j * ds_geo[5]
    long, lat = xy2latlong(x, y, ds)
    
    # generation of the output time profile
    capacity = float(inputs_parameter_selection['peak_power_pv'])
    system_loss = 100 * (1-float(inputs_parameter_selection['efficiency_pv']))
    df_profile = pv_profile(lat, long, 
                            capacity,
                            system_loss)
    # check with pvgis data
    tot_energy_rn =  df_profile.sum() * factor * n_plants
    diff = pv_plant.energy_production - df_profile.sum()
    # transform unit
    hourly_profile, unit_capacity, con = best_unit(df_profile['output'].values,
                                                   'kW', no_data=0,
                                                    fstat=np.median,
                                                    powershift=0)
    graph_hours = line(x=df_profile.index,
                       y_labels=['Hourly profile [{}]'.format(unit_capacity)],
                       y_values=[hourly_profile], unit=unit_capacity)

    # output geneneration of the output
    non_zero = np.count_nonzero(irradiation_values)
    step = int(non_zero/10)

    y_energy = np.round(e_cum_sum[0:non_zero:step],2)
    x_cost = [(i+1)/non_zero *100 for i in range(0, non_zero, step)]
    graph_energy_tot = line(x=x_cost, y_labels=['Energy production [{}]'.format(unit_sum)],
                       y_values=[y_energy], unit=unit_sum)
    
    graphics = [graph_hours, graph_energy_tot]
    # vector_layers = []
    result = dict()
    result['name'] = 'CM solar potential'
    result['indicator'] = [{"unit": unit_sum,
                             "name": "Total energy production",
                             "value": str(round(tot_en_gen_per_year,2))},
                            {"unit": "Million of currency",
                            "name": "Total setup costs",  # M€
                             "value": str(round(tot_setup_costs/1000000))},
                            {"unit": "-",
                             "name": "Number of installed systems",
                             "value": str(round(n_plants))},
                            {"unit": "currency/kWh",
                             "name": "Levelized Cost of Energy",
                             "value": str(round(lcoe_plant,2))}]
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
    print(result)
    # import ipdb; ipdb.set_trace()
    return result
