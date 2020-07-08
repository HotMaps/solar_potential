# -*- coding: utf-8 -*-
import os

CELERY_BROKER_URL_DOCKER = "amqp://admin:mypass@rabbit:5672/"
CELERY_BROKER_URL_LOCAL = "amqp://localhost/"


# CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'
CM_REGISTER_Q = "rpc_queue_CM_register"  # Do no change this value
CM_NAME = "CM - Solar thermal and PV potential"
RPC_CM_ALIVE = "rpc_queue_CM_ALIVE"  # Do no change this value
RPC_Q = "rpc_queue_CM_compute"  # Do no change this value
CM_ID = 4
PORT_LOCAL = int("500" + str(CM_ID))
PORT_DOCKER = 80
# TODO:**********************************************************
CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER
# TODO:**********************************************************
TRANFER_PROTOCOLE = "http://"

"""
Info from: http://pvcalc.org/files/pvcalc.org/pvcalc2/help.php?lang=en

General Information: First of all the appropriate base unit has
    to be identified. For small projects (kWp) a factor of 1 is
    best used, for large projects (MWp) a factor of 1000 is better.
    A PV project has a certain useful life after which it is
    considered worthless. The nominal power is given in kWp (kilo
    Watt peak). The annual yield, measured in kWh per kWp, depends
    on the annual irradiation average of the particular location,
    an estimate can be obtained by using the PVGIS PV Estimation
    Utility. Since solar panels degrade over time the degradation
    per year has to be specified.

Feed in tariff: Governments worldwide give a price guarantee over
    a period of time, usually 20 years. Enter the duration of the
    guarantee and the compensation for electricity fed into the grid.

Income after Guarantee: After the income guarantee expires
    elcetricity can be sold on the energy market. The achievable
    price is unknown but can be estimated by taking today's energy
    price (€ per kWh) and applying an energy price inflation (%/year).

Setup Cost: The fixed cost to build the project has to be entered per kWp.

Running Cost: The running cost is constituted by the lease for
    land, the insurance premium and maintenance costs.
    Insurance premium and maintenance cost have to be given as
    a percentage of the fixed cost.
    Next the inflation rate is needed to to make a forecast for
    the future nprice increase in costs.

Financing: Unless the project is wholly financed by own funds
    financing costs will have to be taken into account.
    Three loan types are available: "Simple", "annuity" and
    "redeemable".
    "Simple" refers to a loan without any featurures such as
    redemptions. In this case a reserve has to b built to allow
    paying off the loan at maturity.
    "Annuity" refers to a loan that works like a mortgage.
    "Redeemable" refers to a loan that allows arbitrary redemptions.
    In this case redemption schedule can be specified.
    "Uniform" means that the redemptions are chosen such that
    a uniform dividend can be paid.
    "Maximum" means that all income is used to redeem the loan
    as quickly as possible. The costs are determined by the
    length of the loan in years the interest rate charged,
    by the fraction of money that is provided by the owner,
    i.e. own funds.
    The disagio specifies what amount is actually paid out.
    The investment yield that the owner can achieve when putting
    aside reserves in order to pay back the loan at maturity
    (only required for loan type "simple").

Tax: Linear depreciation over 20 years is used in order to
    determine the deductible amount. The taxable income is
    determined by the income before redemption less the
    deduction.
    Then the tax rate is applied to the taxable income.


"""
INPUTS_CALCULATION_MODULE = [
    {
        "input_name": "Percentage of potential area covered by solar "
        "panels (PhotoVoltaic – PV and Solar thermal – ST) "
        "[% of total area]"
        "the area used by default is the buildings "
        "footprint raster map.",
        "input_type": "input",
        "input_parameter_name": "reduction_factor",
        "input_value": "30",
        "input_priority": "0",
        "input_unit": "%",
        "input_min": "0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
    #
    # PV
    #
    {
        "input_name": "Percentage of available area covered by "
        "Photovoltaics pannels (PV) [% of the available area]",
        "input_type": "input",
        "input_priority": "1",
        "input_parameter_name": "roof_use_factor_pv",
        "input_value": "15",
        "input_unit": "%",
        "input_min": "0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
    {
        "input_name": "PV energy target of the region if available",
        "input_type": "input",
        "input_parameter_name": "PV_target",
        "input_value": "0",
        "input_priority": "1",
        "input_unit": "GWh",
        "input_min": "0",
        "input_max": "10000000000000",
        "cm_id": CM_ID,
    },
    {
        "input_name": "PV average installed peak power per plant [kW_p]",
        "input_type": "input",
        "input_parameter_name": "peak_power_pv",
        "input_value": "3",
        "input_priority": "1",
        "input_unit": "kW",
        "input_min":"0",
        "input_max": "20",
        "cm_id": CM_ID,
    },
    {
        "input_name": "PV module efficiency at Standard Test Conditions [kW m^{-2}]",
        "input_type": "input",
        "input_parameter_name": "k_pv",
        "input_value": "0.15",
        "input_priority": "1",
        "input_unit": " ",
        "input_min": "0",
        "input_max": "0.6",
        "cm_id": CM_ID,
    },
    {
        "input_name": "Efficiency of the PV system (i.e. inverter)",
        "input_type": "input",
        "input_parameter_name": "efficiency_pv",
        "input_value":"0.85",
        "input_priority": "1",
        "input_unit": " ",
        "input_min": "0",
        "input_max": "1",
        "cm_id": CM_ID,
    },
    {
        "input_name": "PV Setup costs (all inclusive) price [Euro/kWp]",
        "input_type": "input",
        "input_parameter_name": "setup_costs_pv",
        "input_value": "2000",
        "input_priority": "1",
        "input_unit": "Euro/kWp",
        "input_min": "0.0",
        "input_max": "10000",
        "cm_id": CM_ID,
    },
    {
        "input_name": "PV maintenance and operation costs [% of the setup cost]",
        "input_type": "input",
        "input_parameter_name": "maintenance_percentage_pv",
        "input_value": "2",
        "input_priority": "1",
        "input_unit": "%",
        "input_min": "0.0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
    #
    # ST
    #
    {
        "input_name": "Percentage of available area covered by "
        "Solar thermal (ST) pannels [% of the available roof]. "
        "ST and PV cannot share the same surface and are mutually exclusive, "
        "e.g. if the PV %  is set to 90% and the ST % is set to 20% the ST % "
        "is reduced to 10%, to guarantee that no more than 100% of "
        "the surface is used.",
        "input_type": "input",
        "input_priority": "2",
        "input_parameter_name": "roof_use_factor_st",
        "input_value": "15",
        "input_unit": "%",
        "input_min": "0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
    {
        "input_name": "ST energy target of the region if available",
        "input_type": "input",
        "input_parameter_name": "ST_target",
        "input_value": "0",
        "input_priority": "2",
        "input_unit": "GWh",
        "input_min": "0",
        "input_max": "10000000000000",
        "cm_id": CM_ID,
    },
    {
        "input_name": "Solar Thermal average installed surface per plant [m2]",
        "input_type": "input",
        "input_parameter_name": "area_st",
        "input_value": "5",
        "input_priority": "2",
        "input_unit": "m2",
        "input_min": "0",
        "input_max": "20",
        "cm_id": CM_ID,
    },
    {
        "input_name": "Efficiency of the Solar Thermal system",
        "input_type": "input",
        "input_parameter_name": "efficiency_st",
        "input_value": "0.85",
        "input_priority": "2",
        "input_unit": " ",
        "input_min": "0",
        "input_max": "1",
        "cm_id": CM_ID,
    },
    {
        "input_name": "Solar Thermal Setup costs (all inclusive) price [Euro/m2]",
        "input_type": "input",
        "input_parameter_name": "setup_costs_st",
        "input_value": "1000",
        "input_priority": "2",
        "input_unit": "Euro/m2",
        "input_min": "0.0",
        "input_max": "5000",
        "cm_id": CM_ID,
    },

    {
        "input_name": "Solar Thermal maintenance and operation costs [% of the setup cost]",
        "input_type": "input",
        "input_parameter_name": "maintenance_percentage_st",
        "input_value": "2",
        "input_priority": "2",
        "input_unit": "%",
        "input_min": "0.0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
    #
    # Common financial parameters
    #
    {
        "input_name": "Financing years [year]",
        "input_type": "input",
        "input_parameter_name": "financing_years",
        "input_value": "20",
        "input_priority": "3",
        "input_unit": "year",
        "input_min": "0.0",
        "input_max": "40",
        "cm_id": CM_ID,
    },
    {
        "input_name": "Discount rate [%]",
        "input_type": "input",
        "input_parameter_name": "discount_rate",
        "input_value": "4.0",
        "input_priority": "3",
        "input_unit": "%",
        "input_min": "0",
        "input_max": "100",
        "cm_id": CM_ID,
    },
]

WIKIURL = os.environ.get("WIKIURL", "https://wiki.hotmaps.hevs.ch/en/")

SIGNATURE = {
    "category": "Supply",
    "cm_name": CM_NAME,
    "layers_needed": ["building_footprint_tot_curr", "solar_radiation"],  # kWh/m²/year
    "type_layer_needed": [
            {"type": "building_footprint_tot_curr",
             "description": "Area available to host a PV/ST system"},
            {"type": "climate_solar_radiation",
             "description": "Raster map with the annual solar radiation [kWh/m²/year]"}
            ],
    "cm_url": "Do not add something",
    "cm_description": "This computation aims to compute the PhotoVoltaic – PV"
    "energy potential, the Solar Thermal – ST energy potential"
    "and the financial feasibility of massive interventions"
    "The code is on the Hotmaps Github group and has"
    " been developed by EURAC",
    "cm_id": CM_ID,
     "wiki_url": WIKIURL + "CM-Solar-thermal-and-PV-potential",
    "inputs_calculation_module": INPUTS_CALCULATION_MODULE,
}
