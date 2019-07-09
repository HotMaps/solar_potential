
CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'CM - Scale heat and cool density maps'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 1 # CM_ID is defined by the enegy research center of Martigny (CREM)
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80

#TODO ********************setup this URL depending on which version you are running***************************

CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER

#TODO ********************setup this URL depending on which version you are running***************************

TRANFER_PROTOCOLE ='http://'
INPUTS_CALCULATION_MODULE = [
    {'input_name': 'Multiplication factor',
     'input_type': 'input',
     'input_parameter_name': 'multiplication_factor',
     'input_value': '1',
     'input_priority': 0,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 10, 'cm_id': CM_ID  # Do no change this value
     },
]


SIGNATURE = {

    "category": "Buildings",
    "authorized_scale":["NUTS 2","NUTS 0","Hectare"],
    "cm_name": CM_NAME,
    "layers_needed": [
        "heat_tot_curr_density",
    ],
    "type_layer_needed": [
        "heat",
    ],
    "vectors_needed": [
        "heating_technologies_eu28",

    ],
    "cm_url": "Do not add something",
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
