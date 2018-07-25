
CELERY_BROKER_URL = 'amqp://admin:mypass@rabbit:5672/'
#CELERY_BROKER_URL = 'amqp://localhost/'


#CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'


CM_NAME = 'calculation_module_test'

RPC_Q = 'rpc_queue_CM' # Do no change this value
CM_ID = 1
PORT = 5000 + CM_ID

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
    "cm_url": "",
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}