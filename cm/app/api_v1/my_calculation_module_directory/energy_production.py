#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 07:17:34 2019

@author: ggaregnani
"""
import os
import sys
import math
import numpy as np
import reslib.planning as plan

# TODO:  chane with try and better define the path
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, "app", "api_v1")
if path not in sys.path:
    sys.path.append(path)


def get_plants(
    plant,
    target,
    irradiation_values,
    building_footprint,
    roof_use_factor,
    reduction_factor,
):
    """
    Return a raster with most suitable roofs and the number of plants
    for each pixel
    """
    # TODO: split in two functions
    n_plants, plant = constraints(
        target,
        irradiation_values,
        building_footprint,
        roof_use_factor,
        reduction_factor,
        plant,
    )
    tot_en_gen_per_year = n_plants * plant.energy_production
    # compute the raster with the number of plant per pixel
    n_plant_raster = np.floor(
        (building_footprint * reduction_factor * roof_use_factor) / plant.area
    )
    most_suitable = raster_suitable(
        n_plant_raster, tot_en_gen_per_year, irradiation_values, plant
    )
    n_plant_raster[most_suitable <= 0] = 0
    return n_plant_raster, most_suitable, plant


def constraints(
    PV_target,
    irradiation_values,
    building_footprint,
    roof_use_factor,
    reduction_factor,
    pv_plant,
):
    """
    Define planning rules accounting for area availability and
    target defined by the user
    """
    e_pv_mean = irradiation_values[irradiation_values > 0].mean()
    footprint_sum = building_footprint.sum()
    # the solar irradiation at standard test condition equal to 1 kWm-2
    pv_plant.energy_production = pv_plant.compute_energy(e_pv_mean)
    area_available = reduction_factor * footprint_sum
    area_usable_by_pv = area_available * roof_use_factor
    n_plants = math.floor(area_usable_by_pv / pv_plant.area)
    energy_available = n_plants * pv_plant.energy_production
    print(f"{footprint_sum} -> {area_available} -> {area_usable_by_pv}")
    print(f"{n_plants} * {pv_plant.energy_production} = {energy_available}")
    if PV_target != 0:
        # constraints:
        # (area_target <= area_available) and (energy_target <= energy_available)
        rules = plan.PlanningRules(
            area_usable_by_pv,  # area_target
            PV_target,  # energy_target
            area_available,  # area_available
            energy_available,
        )  # energy available
        n_plants = rules.n_plants(pv_plant)

    return n_plants, pv_plant


def raster_suitable(n_plant_raster, tot_en_gen_per_year, irradiation_values, pv_plant):
    """ Define the most suitable roofs,
    by computing the energy for each pixel by considering a number of plants
    for each pixel and selected
    most suitable pixel to cover the enrgy production
    """
    # TODO: do not consider 0 values in the computation
    en_values = (
        irradiation_values * pv_plant.peak_power * pv_plant.efficiency * n_plant_raster
    )
    # order the matrix
    ind = np.unravel_index(np.argsort(en_values, axis=None)[::-1], en_values.shape)
    e_cum_sum = np.cumsum(en_values[ind])
    # find the nearest element
    idx = (np.abs(e_cum_sum - tot_en_gen_per_year)).argmin()

    # create new array of zeros and ones
    most_suitable = np.zeros_like(en_values)
    for i, j in zip(ind[0][0:idx], ind[1][0:idx]):
        most_suitable[i][j] = en_values[i][j]
    return most_suitable


if __name__ == "__main__":
    import doctest

    doctest.testmod()
