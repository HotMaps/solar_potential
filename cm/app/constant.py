
URL_MWS_DEV = 'http://api.hotmapsdev.hevs.ch/'
URL_MAIN_WEBSERVICE = URL_MWS_DEV

PORT = '5001'
URL_CM = '0.0.0.0'
DOCKER_URL = '172.17.0.5:5001'
CM_NAME = 'calculation_module_1'
CM_ID = 1

INPUTS_CALCULATION_MODULE=  [
    { 'input_name': 'Reduction factor',
      'input_type': 'input',
      'input_parameter_name': 'reduction_factor',
      'input_value': 1,
      'input_unit': 'none',
      'input_min': 1,
      'input_max': 10
        , 'cm_id': CM_ID
      },
    { 'input_name': 'Blablabla',
      'input_type': 'range',
      'input_parameter_name': 'bla',
      'input_value': 50,
      'input_unit': '',
      'input_min': 10,
      'input_max': 1000,
      'cm_id': CM_ID
      }
]



SIGNATURE = {
    "category": "Buildings",
    "cm_name": CM_NAME,
    "layers_needed": [
        "heat_density_tot"
    ],
    "cm_url": DOCKER_URL,
    "cm_description": "this computation module allows to ....",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}