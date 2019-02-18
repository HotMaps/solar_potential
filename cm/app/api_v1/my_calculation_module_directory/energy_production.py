#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 07:17:34 2019

@author: ggaregnani
"""
import os
import sys
import numpy as np
# TODO:  chane with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)
import my_calculation_module_directory.plants as plant


def mean_plant(inputs_parameter_selection):
    setup_costs = int(inputs_parameter_selection['setup_costs'])
    tot_cost_year = (float(inputs_parameter_selection['maintenance_percentage']) /
                     100 * setup_costs)
    financing_years = int(inputs_parameter_selection['financing_years'])

    # compute the indicators and the output raster

    pv_plant = plant.PV_plant('mean',
                              peak_power=float(inputs_parameter_selection['peak_power_pv']),
                              efficiency=float(inputs_parameter_selection['efficiency_pv'])
                              )
    pv_plant.k_pv = float(inputs_parameter_selection['k_pv'])
    tot_investment = int(pv_plant.peak_power * setup_costs)
    pv_plant.financial = plant.Financial(investement_cost=tot_investment,
                                         yearly_cost=tot_cost_year,
                                         plant_life=financing_years)
    return pv_plant


def indicators(PV_target, irradiation_values, irradiation_pixel_area,
               roof_use_factor, reduction_factor, pv_plant):
    no_zero = irradiation_values[np.nonzero(irradiation_values)]
    e_pv_mean = float(np.mean(no_zero[~np.isnan(no_zero)]))
    # the solar irradiation at standard test condition equal to 1 kWm-2
    pv_plant.energy_production = (e_pv_mean * pv_plant.peak_power *
                                  pv_plant.efficiency)
    building_footprint = (float(np.count_nonzero(irradiation_values) *
                          irradiation_pixel_area))
    area_available = roof_use_factor * building_footprint
    energy_available = (area_available / pv_plant.area *
                        pv_plant.energy_production)

    if PV_target == 0:
        PV_target = energy_available

    rules = plant.Planning_rules(area_target=reduction_factor*area_available,
                                 PV_target,
                                 area_available, energy_available)
    n_plants = rules.n_plants(pv_plant)
    n_plant_pixel = (irradiation_pixel_area/pv_plant.area() *
                     roof_use_factor)

    return n_plants, n_plant_pixel, pv_plant, building_footprint


def raster_suitable(n_plant_pixel, tot_en_gen_per_year,
                    irradiation_values, pv_plant):
    # define the most suitable roofs,
    # compute the energy for each pixel by considering a number of plants
    # for each pixel and selected
    # most suitable pixel to cover the enrgy production
    # TODO: do not consider 0 values in the computation
    en_values = (irradiation_values * pv_plant.peak_power *
                 pv_plant.efficiency * n_plant_pixel)
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
    return most_suitable, e_cum_sum
