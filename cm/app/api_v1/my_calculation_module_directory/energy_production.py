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


def indicators(PV_target, irradiation_values, building_footprint,
               roof_use_factor, reduction_factor, pv_plant):
    e_pv_mean = irradiation_values[irradiation_values > 0].mean()
    footprint_sum = building_footprint[building_footprint > 0].sum()
    # the solar irradiation at standard test condition equal to 1 kWm-2
    pv_plant.energy_production = pv_plant.compute_energy(e_pv_mean)
    area_available = roof_use_factor * footprint_sum
    energy_available = (area_available / pv_plant.area() *
                        pv_plant.energy_production)

    if PV_target == 0:
        PV_target = energy_available
    rules = plant.Planning_rules(reduction_factor*area_available,
                                 PV_target, area_available, energy_available)
    n_plants = rules.n_plants(pv_plant)

    return n_plants, pv_plant


def raster_suitable(n_plant_raster, tot_en_gen_per_year,
                    irradiation_values, pv_plant):
    # define the most suitable roofs,
    # compute the energy for each pixel by considering a number of plants
    # for each pixel and selected
    # most suitable pixel to cover the enrgy production
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
    return most_suitable, e_cum_sum


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
