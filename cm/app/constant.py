# -*- coding: utf-8 -*-

CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'

CELERY_BROKER_URL = CELERY_BROKER_URL_LOCAL
#CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'
CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'solar_potential'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 313
PORT = 5001
TRANFER_PROTOCOLE ='http://'

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
    {'input_name': 'Effective building roof utilization factor',
     'input_type': 'range',
     'input_parameter_name': 'roof_use_factor',
     'input_value': 0.15,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 1,
     'cm_id': 313
     },
    {'input_name': 'Fraction of buildings with solar panels',
     'input_type': 'input',
     'input_parameter_name': 'reduction_factor',
     'input_value': 0.3,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 1,
     'cm_id': 313
     },
    {'input_name': 'Installed peak power [kW_p]',
     'input_type': 'input',
     'input_parameter_name': 'peak_power_pv',
     'input_value': 3,
     'input_unit': 'kW',
     'input_min': 0,
     'input_max': 20,
     'cm_id': 313
     },
    {'input_name': 'Efficiency of the solar system',
     'input_type': 'input',
     'input_parameter_name': 'efficiency_pv',
     'input_value': 0.75,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 1,
     'cm_id': 313
     },
    {'input_name': 'Module efficiency at Standard Test Conditions [kW m^{-2}]',
     'input_type': 'input',
     'input_parameter_name': 'k_pv',
     'input_value': 0.15,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 0.6,
     'cm_id': 313
     },
    {'input_name': 'Setup costs (all inclusive) price [currency/kWp]',
     'input_type': 'input',
     'input_parameter_name': 'setup_costs',
     'input_value': 5000,
     'input_unit': 'currency/kWp',
     'input_min': 0.0,
     'input_max': 10000,
     'cm_id': 313
     },
    {'input_name': 'Maintenance and operation costs [%] of the setup cost',
     'input_type': 'input',
     'input_parameter_name': 'maintenance_percentage',
     'input_value': 2,
     'input_unit': '%',
     'input_min': 0.0,
     'input_max': 100,
     'cm_id': 313
     },
    {'input_name': 'Financing years [year]',
     'input_type': 'input',
     'input_parameter_name': 'financing_years',
     'input_value': 20,
     'input_unit': 'year',
     'input_min': 0.0,
     'input_max': 40,
     'cm_id': 313
     },
    {'input_name': 'Discount rate [%]',
     'input_type': 'input',
     'input_parameter_name': 'discount_rate',
     'input_value': 4.0,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 100,
     'cm_id': 313
     }
]



SIGNATURE = {
    "category": "Solar potential",
    "cm_name": CM_NAME,
    "layers_needed": [
        # TODO: add new default dataset with the total energy of the roof
        "solar_optimal_total",  # kWh/m²/year
    ],
    "cm_url": "Do not add something",
    "cm_description": "This computation aims to compute the photovoltaic"
                      "energy potential and the financial feasibility of"
                      "a selected area ",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
