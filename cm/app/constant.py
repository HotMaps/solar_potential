
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
    #
    # Spatial filter
    # =================
    {'input_name': 'Effective building roof utilization factor',
     'input_type': 'range',
     'input_parameter_name': 'roof_use_factor',
     'input_value': 0.15,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    #
    # General information of the solar system
    # ========================================
    {'input_name': 'Efficiency of the solar system',
     'input_type': 'range',
     'input_parameter_name': 'efficiency_solar_system',
     'input_value': 0.12,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    {'input_name': 'Useful system life [years]',
     # 'input_desc': 'Time after which the installation is considered worthless',
     'input_type': 'input',
     'input_parameter_name': 'solar_life',
     'input_value': 25,
     'input_unit': 'years',
     'input_min': 0,
     'input_max': 50,
     'cm_id': CM_ID
     },
    {'input_name': 'Performance system degradation [%/year]',
     # 'input_desc': '',
     'input_type': 'input',
     'input_parameter_name': 'solar_degradation',
     'input_value': 0.5,
     'input_unit': '%/year',
     'input_min': 0,
     'input_max': 100,
     'cm_id': CM_ID
     },
    #
    # Feed in tariffs
    #
    {'input_name': 'Feed in tariffs: number of years [years]',
     # 'input_desc': 'Duration of the feed-in-tariff',
     'input_type': 'input',
     'input_parameter_name': 'feed_years',
     'input_value': 20,
     'input_unit': 'years',
     'input_min': 0,
     'input_max': 50,
     'cm_id': CM_ID
     },
    {'input_name': 'Feed in tariffs: energy price [currency/kWh]',
     # 'input_desc': '',
     'input_type': 'input',
     'input_parameter_name': 'energy_price',
     'input_value': 0.18,
     'input_unit': 'currency/kWh',
     'input_min': 0.,
     'input_max': 0.80,
     'cm_id': CM_ID
     },
    {'input_name': 'Feed in tariffs: index linked',
     # 'input_desc': 'FiT linked to an inflation index?',
     'input_type': 'checkbox',
     'input_parameter_name': 'feed_in_price',
     'input_value': 'false',
     'input_unit': 'currency/kWh',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    #
    # Income after Guarantee
    # =======================
    {'input_name': 'Own consumption costs [currency/kWh]',
     # 'input_desc': 'Feed-in-tariff subsidy for own consumption'
     'input_type': 'input',
     'input_parameter_name': 'consumption_costs',
     'input_value': 0.25,
     'input_unit': 'currency/kWh',
     'input_min': 0.,
     'input_max': 0.50,
     'cm_id': CM_ID
     },
    {'input_name': 'Own consumption factor',
     # 'input_desc': 'Expected own consumption',
     'input_type': 'input',
     'input_parameter_name': 'consumption_factor',
     'input_value': 0.2,
     'input_unit': '',
     'input_min': 0.,
     'input_max': 1.,
     'cm_id': CM_ID
     },
    #
    # Electricity price consumption
    # ===============================
    {'input_name': 'Price now [currency/kWh]',
     # 'input_desc': 'Energy price now, used for estimating future energy prices',
     'input_type': 'input',
     'input_parameter_name': 'energy_price',
     'input_value': 0.2,
     'input_unit': 'currency/kWh',
     'input_min': 0.,
     'input_max': 1.,
     'cm_id': CM_ID
     },
    {'input_name': 'Energy price inflation [%/year]',
     # 'input_desc': 'Used for estimating future energy prices'
     'input_type': 'input',
     'input_parameter_name': 'energy_inflation',
     'input_value': 1,
     'input_unit': 'currency/kWh',
     'input_min': 0,
     'input_max': 100,
     'cm_id': CM_ID
     },
    #
    # Setup costs (all inclusive)
    # ============================
    {'input_name': 'Setup costs (all inclusive) price [currency/kWp]',
     # 'input_desc': 'Setup cost of the installation (fixed cost)'
     'input_type': 'input',
     'input_parameter_name': 'setup_costs',
     'input_value': 3000,
     'input_unit': 'currency/kWp',
     'input_min': 0.,
     'input_max': 10000,
     'cm_id': CM_ID
     },
    #
    # Running costs
    # ====================
    {'input_name': 'Lease [currency/year]',
     # 'input_desc': 'If a lease is to be paid enter this here, annual costs'
     'input_type': 'input',
     'input_parameter_name': 'running_costs_lease',
     'input_value': 0,
     'input_unit': 'currency/year',
     'input_min': 0.,
     'input_max': 10000000,
     'cm_id': CM_ID
     },
    {'input_name': 'Insurance premium [%]',
     # 'input_desc': 'Annual insurance premium as a percentage of the initial value of the installation'
     'input_type': 'input',
     'input_parameter_name': 'insurance_percentage',
     'input_value': 0.5,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Maintenance [%]',
     # 'input_desc': 'Annual maintenance cost as a percentage of the initial value of the installation'
     'input_type': 'input',
     'input_parameter_name': 'maintenance_percentage',
     'input_value': 0.5,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Inflation rate [%/year]',
     # 'input_desc': 'Inflation rate is used to predict future costs'
     'input_type': 'input',
     'input_parameter_name': 'inflation_rate',
     'input_value': 2.,
     'input_unit': '%/year',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    #
    # Financing
    # =================
    {'input_name': 'Own funds [%]',
     # 'input_desc': 'Own funds provided as a fraction (in %) of the setup cost'
     'input_type': 'input',
     'input_parameter_name': 'own_fund_percentage',
     'input_value': 100.,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'loan type',
     # 'input_desc': 'SELECT:: Simple: Simple loan, no redemption. Annuity: Works like a mortgage. Redeemable: Redemptions possible at specified times',
     'input_type': 'input',
     'input_parameter_name': 'loan_type',
     'input_value': 2.,
     'input_unit': '%]',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Redemption Sched.',
     # 'input_desc': 'SELECT::This option only applies to loan type "redeemable": Uniform:Redemptions are chosen such that a uniform dividend can be paid. Maximum: Redemptions are maximized so that the loan is paid back quickest. '
     'input_type': 'input',
     'input_parameter_name': 'redemption_sched',
     'input_value': 0.5,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Financing years [year]',
     # 'input_desc': 'Financing term'
     'input_type': 'input',
     'input_parameter_name': 'financing_years',
     'input_value': 20,
     'input_unit': 'year',
     'input_min': 0.,
     'input_max': 40.,
     'cm_id': CM_ID
     },
    {'input_name': 'Interest rate [%]',
     # 'input_desc': 'Interest rate applicable for the loan type',
     'input_type': 'input',
     'input_parameter_name': 'interest_rate',
     'input_value': 4.0.,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Disagio [%]',
     # 'input_desc': 'Disagio in percent, i.e. a 3% disagio means a 97% loan'
     'input_type': 'input',
     'input_parameter_name': 'disagio',
     'input_value': 3.,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    {'input_name': 'Investment yield [%]',
     # 'input_desc': 'Applicable for loan type "simple". Determines which return assumes to be achieved when building the reserve'
     'input_type': 'input',
     'input_parameter_name': 'inflation_rate',
     'input_value': 3.5,
     'input_unit': '%',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
     },
    #
    # Tax
    # =================
    {'input_name': 'Tax rate',
     # 'input_desc': 'Tax rate applicable to taxable income (equals income before redemption less depreciation)'
     'input_type': 'input',
     'input_parameter_name': 'inflation_rate',
     'input_value': 3.5,
     'input_unit': 'none',
     'input_min': 0.,
     'input_max': 100.,
     'cm_id': CM_ID
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
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
