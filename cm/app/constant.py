
CELERY_BROKER_URL = 'amqp://admin:mypass@rabbit:5672/'
#CELERY_BROKER_URL = 'amqp://localhost/'

URL_MWS_DEV = 'http://api.hotmapsdev.hevs.ch/'
URL_MWS_DEV_DOCKER = 'http://172.24.0.2/'
URL_MWS_LOCAL_DOCKER= 'http://172.25.0.6:5000/'
URL_MWS_LOCAL= 'http://127.0.0.1:5000/'
#CELERY_BROKER_URL = 'amqp://admin:mypass@rabbit:5672/'
#CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'


URL_MAIN_WEBSERVICE = URL_MWS_LOCAL_DOCKER
PORT_DOCKER = '5001'
URL_CM_DOCKER = '172.17.0.2'
PORT = '5001'
URL_CM = '0.0.0.0'
DOCKER_URL = '172.17.0.2:5001/'
CM_NAME = 'calculation_module_test'

RPC_Q = 'rpc_queue_CM'
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
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}