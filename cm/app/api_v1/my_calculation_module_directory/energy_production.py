#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 07:17:34 2019

@author: ggaregnani
"""
import os
import sys
import numpy as np
import warnings
from osgeo import gdal
import reslib.planning as plan
# TODO:  chane with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)

from my_calculation_module_directory.visualization import quantile_colors
from my_calculation_module_directory.utils import best_unit, xy2latlong
from my_calculation_module_directory.time_profiles import pv_profile


def get_plants(plant, target, irradiation_values,
               building_footprint, roof_use_factor,
               reduction_factor):
    """
    Return a raster with most suitable roofs and the number of plants
    for each pixel
    """
    # TODO: split in two functions
    n_plants, plant = constraints(target,
                                  irradiation_values,
                                  building_footprint,
                                  roof_use_factor,
                                  reduction_factor/100,
                                  plant)

    tot_en_gen_per_year = n_plants * plant.energy_production
    # compute the raster with the number of plant per pixel
    n_plant_raster = (building_footprint / plant.area * roof_use_factor *
                      reduction_factor / 100)
    n_plant_raster = n_plant_raster.astype(int)
    most_suitable = raster_suitable(n_plant_raster,
                                    tot_en_gen_per_year,
                                    irradiation_values,
                                    plant)
    n_plant_raster[most_suitable <= 0] = 0
    return n_plant_raster, most_suitable, plant


def get_indicators(kind, plant, most_suitable,
                   n_plant_raster, discount_rate):
    """
    Return a dictionary with main indicator of the specific source
    """
    n_plants = n_plant_raster.sum()
    plant.energy_production = (most_suitable.sum() / n_plants)
    tot_en_gen_per_year = plant.energy_production * n_plants
    error = abs(tot_en_gen_per_year -
                most_suitable.sum())/(tot_en_gen_per_year)
    if abs(error) > 0.01:
        warnings.warn("""Difference between raster value sum and
                      total energy greater than {}%""".format(int(error)))

    tot_en_gen, unit, factor = best_unit(tot_en_gen_per_year,
                                         current_unit='kWh/year',
                                         no_data=0,
                                         fstat=np.min,
                                         powershift=0)
    tot_setup_costs = plant.financial.investement_cost * n_plants
    lcoe_plant = plant.financial.lcoe(plant.energy_production,
                                      i_r=discount_rate/100)
    return [{"unit": unit,
             "name": "{} total energy production".format(kind),
             "value": str(round(tot_en_gen, 2))},
            {"unit": "Million of currency",
             "name": "{} total setup costs".format(kind),  # M€
             "value": str(round(tot_setup_costs/1000000))},
            {"unit": "-",
             "name": "Number of installed {} Systems".format(kind),
             "value": str(round(n_plants))},
            {"unit": "currency/kWh",
             "name": "Levelized Cost of {} Energy".format(kind),
             "value": str(round(lcoe_plant, 2))}]


def get_raster(most_suitable, output_suitable, ds, kind):
    """
    Return a dictionary with the output raster and the simbology
    """
    most_suitable, unit, factor = best_unit(most_suitable,
                                            current_unit="kWh/pixel/year",
                                            no_data=0, fstat=np.min,
                                            powershift=0)
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

    return [{"name": "layers of most suitable roofs for {}".format(kind),
             "path": output_suitable,
             "type": "custom",
             "symbology": symbology
             }]


def get_lat_long(ds, most_suitable):
    """
    Return the lat_long of the pixel with mean value of the resources
    """
    diff = most_suitable - np.mean(most_suitable[most_suitable > 0])
    i, j = np.unravel_index(np.abs(diff).argmin(), diff.shape)
    ds_geo = ds.GetGeoTransform()
    x = ds_geo[0] + i * ds_geo[1]
    y = ds_geo[3] + j * ds_geo[5]
    long, lat = xy2latlong(x, y, ds)
    # generation of the output time profile
    return lat, long


def constraints(PV_target, irradiation_values, building_footprint,
                roof_use_factor, reduction_factor, pv_plant):
    """
    Define planning rules accounting for area availability and
    target defined by the user
    """
    e_pv_mean = irradiation_values[irradiation_values > 0].mean()
    footprint_sum = building_footprint.sum()
    # the solar irradiation at standard test condition equal to 1 kWm-2
    pv_plant.energy_production = pv_plant.compute_energy(e_pv_mean)
    area_available = roof_use_factor * footprint_sum
    energy_available = (area_available / pv_plant.area *
                        pv_plant.energy_production)

    if PV_target == 0:
        PV_target = energy_available
    rules = plan.Planning_rules(reduction_factor*area_available,
                                PV_target, area_available, energy_available)
    n_plants = rules.n_plants(pv_plant)

    return n_plants, pv_plant


def raster_suitable(n_plant_raster, tot_en_gen_per_year,
                    irradiation_values, pv_plant):
    """ Define the most suitable roofs,
    by computing the energy for each pixel by considering a number of plants
    for each pixel and selected
    most suitable pixel to cover the enrgy production
    """
    # TODO: do not consider 0 values in the computation
    en_values = (irradiation_values * pv_plant.peak_power *
                 pv_plant.efficiency * n_plant_raster)
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
    return most_suitable


def hourly_indicators(df, capacity):
    """
    Compute the indicators based on the df profile

    >>> df = pd.Series([0.2, 0, 0, 1] , index=pd.date_range('2000',
    ...                freq='h', periods=4))
    >>> hourly_indicators(df, 1)
    (1.2, 2, 1.2)
    """

    # there is no difference by using integration methods such as
    # trap integration
    tot_energy = df.sum()
    working_hours = df[df > 0].count()
    equivalent_hours = tot_energy/capacity
    return (tot_energy, working_hours, equivalent_hours)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
