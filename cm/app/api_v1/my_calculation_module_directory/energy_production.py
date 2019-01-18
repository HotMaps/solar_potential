#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 07:17:34 2019

@author: ggaregnani
"""
import numpy as np


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


def costs(irradiation_values, peak_power_pv, efficiency_pv, k_pv,
          tot_investment, tot_cost_year, discount_rate,
          financing_years, irradiation_pixel_area, roof_use_factor,
          reduction_factor, setup_costs):
    e_pv_mean = float(np.mean(np.nonzero(irradiation_values)))
    # the solar irradiation at standard test condition equal to 1 kWm-2
    en_gen_per_year = (e_pv_mean * peak_power_pv * efficiency_pv)
    # compute lcoe for a single representative plant
    lcoe_plant = lcoe(tot_investment, tot_cost_year,
                      financing_years,
                      discount_rate,
                      en_gen_per_year)

    area_plant = peak_power_pv / k_pv

    building_footprint = (float(np.count_nonzero(irradiation_values) *
                          irradiation_pixel_area))

    n_plants = (roof_use_factor * reduction_factor * building_footprint /
                area_plant)
    tot_en_gen_per_year = en_gen_per_year * n_plants

    return n_plants, tot_en_gen_per_year, lcoe_plant


def raster_suitable(roof_use_factor, peak_power_pv, efficiency_pv, k_pv,
                    irradiation_pixel_area, irradiation_values,
                    tot_en_gen_per_year):
    # define the most suitable roofs,
    # compute the energy for each pixel by considering a number of plants
    # for each pixel and selected
    # most suitable pixel to cover the enrgy production
    # TODO: do not consider 0 values in the computation

    # n_plant_pixel potential number of plants in a pixel
    area_plant = peak_power_pv / k_pv
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
    return most_suitable, n_plant_pixel, e_cum_sum
