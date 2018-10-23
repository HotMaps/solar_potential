
from flask import request, abort, jsonify ,url_for, g,flash
from . import api
from .. import SIGNATURE,CM_NAME
import json
import requests
import logging
import os
from flask import send_from_directory
from app import helper
from app import constant

from app.api_v1 import errors
import socket
from . import calculation_module
from app import CalculationModuleRpcClient

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


UPLOAD_DIRECTORY = '/var/tmp'
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)

@api.route('/files/<string:filename>', methods=['GET'])
def get(filename):
    # get file stored in the api directory
    return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)

@api.route('/register/', methods=['POST'])
def register():

    #""" register the Calculation module (CM)to the main web services (MWS)-
    #the CM will send its SIGNATURE to the main web service, CM SIGNATURE contains elements to identity the CM and
    #how to handle it and the list of input it needs on the user interface. CM SIGNATURE can be find on app/constants.py file, this file must be change manually
    #Also constants.py must contains a CM_ID that is a unique number that as to be defined by the CREM (Centre de Recherches Energetiques et Municipales de Martigny)

    #  ---
    #  definitions:
    #     Color:
    #     type: string
    #  #responses:
    #  200:
    #   description: MWS is aware of the CM
    #  examples:
    #   results: {"response": {"category": "Buildings", "cm_name": "calculation_module_1", "layers_needed": ["heat_density_tot"], "cm_description": "this computation module allows to ....", "cm_url": "http://127.0.0.1:5002/", "cm_id": 1, "inputs_calculation_module": [{"input_min": 1, "input_value": 1, "input_unit": "none", "input_name": "Reduction factor", "cm_id": 1, "input_type": "input", "input_parameter_name": "reduction_factor", "input_max": 10}, {"input_min": 10, "input_value": 50, "input_unit": "", "input_name": "Blablabla", "cm_id": 1, "input_type": "range", "input_parameter_name": "bla", "input_max": 1000}]}}
    #    """

    # about to send the external IP
    print ('CM will begin register ')
    ip = socket.gethostbyname(socket.gethostname())
    # retrive dynamic url
    base_url = 'http://'+ str(ip) +':'+ str(constant.PORT) +'/'
    signature_final = SIGNATURE


    calculation_module_rpc = CalculationModuleRpcClient()

    signature_final["cm_url"] = base_url
    payload = json.dumps(signature_final)
    response = calculation_module_rpc.call(payload)
    print ('CM will finish register ')

    return response



def savefile(filename,url):
    print ('CM is Computing and will dowload files with url: ',url)
    r = None
    path = None
    try:
        r = requests.get(url, stream=True)
    except:
        LOGGER.error('API unable to download tif files')
        print ('API unable to download tif files saved')

    print ('image saved',r.status_code)
    if r.status_code == 200:
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        LOGGER.error('API unable to download tif files')
        print ('unsable to download tif')
    return path


@api.route('/compute/', methods=['POST'])
def compute():
    #TODO: CM provider must "change the documentation with the information of his CM

    """ compute the Calculation module (CM)from the main web services (MWS)-
    the main web service is sending
        ---
       parameters:
          - name: inputs_raster_selection
            in: path
            type: dict
            required: true
            default:  {'solar_optimal_total': '/var/hotmaps/cm_files_uploaded/raster_for_test.tif'}
          - name: inputs_parameter_selection
            in: path
            type: dict
            required: true
            default: {'roof_use_factor': 0.15,
                      'reduction_factor': 0.3,
                      'peak_power_pv': 3,
                      'efficiency_pv': 0.75,
                      'k_pv': 0.15,
                      'setup_costs': 5000,
                      'maintenance_percentage': 2,
                      'financing_years': 20,
                      'discount_rate': 4
                      }

       definitions:
         Color:
           type: string
       responses:
         200:
           description: MWS is aware of the CM
           examples:
            results: {"response":
                      {"category": "Energy Potential",
                       "cm_name": "calculation_module_1",
                       "layers_needed": ["heat_density_tot"],
                       "cm_description": "this computation module aims to
                                          compute the photovoltaic energy
                                          potential and the financial
                                          feasibility of a selected area
                                          by considering:
                                           - the installation of new PV systems
                                             on a percentage of building
                                             footprint
                                           - the financial feasibility of
                                             new plants
                                          The output of the module are:
                                           - the total cost of covering the
                                             selected area with PV panels
                                             [currency]
                                           - the total yearly energy production
                                             [MWh/year]
                                           - the Levelized Cost of Energy
                                             [currency/kWh]
                                           - the most suitable roofs for
                                             PV energy production",
                       "cm_url": "http://127.0.0.1:5002/",
                       "cm_id": 313, "inputs_calculation_module":
                           [
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
]}}
             """

    print ('CM will Compute ')
    #import ipdb; ipdb.set_trace()
    data = request.get_json()

    #TODO CM Developper do not need to change anything here
    # here is the inputs layers and parameters
    inputs_raster_selection = helper.validateJSON(data["inputs_raster_selection"])
    print ('inputs_raster_selection', inputs_raster_selection)
    LOGGER.info('inputs_raster_selection', inputs_raster_selection)

    inputs_parameter_selection = helper.validateJSON(data["inputs_parameter_selection"])
    print ('inputs_parameter_selection', inputs_parameter_selection)
    LOGGER.info('inputs_parameter_selection', inputs_parameter_selection)

    output_directory = UPLOAD_DIRECTORY
    # call the calculation module function
    result = calculation_module.calculation(output_directory,
                                            inputs_raster_selection,
                                            inputs_parameter_selection)

    response = {
        'result': result


    }
    print("response ",response)

    # convert response dict to json
    response = json.dumps(response)
    return response


