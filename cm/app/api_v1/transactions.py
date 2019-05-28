
from flask import request, abort, jsonify ,url_for, g,flash
from . import api
from .. import SIGNATURE,CM_NAME
import json
import requests
import logging
import os
from flask import send_from_directory
from  app import helper
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
    #   results: {"response": {"category": "Buildings", "cm_name": "calculation_module_1", "layers_needed": ["heat_density_tot"], "cm_description": "this computation module allows to ....", "cm_url": "http://127.0.0.1:5002/", "cm_id": 1, "inputs_calculation_module": [{"input_min": 1, "input_value": 1, "input_unit": "none", "input_name": "Reduction factor", "cm_id": 1, "input_type": "input", "input_parameter_name": "multiplication_factor", "input_max": 10}, {"input_min": 10, "input_value": 50, "input_unit": "", "input_name": "Blablabla", "cm_id": 1, "input_type": "range", "input_parameter_name": "bla", "input_max": 1000}]}}
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


    return response



def savefile(filename,url):
    print ('CM is Computing and will dowload files with url: ',url)
    r = None
    path = None
    try:
        r = requests.get(url, stream=True)
    except:
        LOGGER.error('API unable to download tif files')


    print ('image saved',r.status_code)
    if r.status_code == 200:
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        LOGGER.error('API unable to download tif files')

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
            default:  {'heat_tot_curr_density': '/var/hotmaps/cm_files_uploaded/raster_for_test.tif'}
          - name: inputs_parameter_selection
            in: path
            type: dict
            required: true
            default: {'multiplication_factor': 2}
          - name: multiplication_factor
            in: path
            type: integer
            required: true
            default: 1

       definitions:
         Color:
           type: string
       responses:
         200:
           description: MWS is aware of the CM
           examples:
            results: {"response": {"category": "Buildings", "cm_name": "calculation_module_1", "layers_needed": ["heat_density_tot"], "cm_description": "this computation module allows to ....", "cm_url": "http://127.0.0.1:5002/", "cm_id": 1, "inputs_calculation_module": [{"input_min": 1, "input_value": 1, "input_unit": "none", "input_name": "Reduction factor", "cm_id": 1, "input_type": "input", "input_parameter_name": "multiplication_factor", "input_max": 10}, {"input_min": 10, "input_value": 50, "input_unit": "", "input_name": "Blablabla", "cm_id": 1, "input_type": "range", "input_parameter_name": "bla", "input_max": 1000}]}}
             """

    print ('CM will Compute ')
    #import ipdb; ipdb.set_trace()
    data = request.get_json()

    #TODO CM Developper do not need to change anything here
    # here is the inputs layers and parameters
    inputs_raster_selection = helper.validateJSON(data["inputs_raster_selection"])


    inputs_parameter_selection = helper.validateJSON(data["inputs_parameter_selection"])



    inputs_vector_selection = helper.validateJSON(data["inputs_vector_selection"])
    print ('inputs_vector_selection', inputs_vector_selection)
    LOGGER.info('inputs_vector_selection', inputs_vector_selection)

    output_directory = UPLOAD_DIRECTORY
    # call the calculation module function
    result = calculation_module.calculation(output_directory, inputs_raster_selection,inputs_vector_selection,inputs_parameter_selection)

    response = {
        'result': result


    }

 #   LOGGER.info('response', response)

#    LOGGER.info("type response ",type(response))
    # convert response dict to json
    response = json.dumps(response)
    return response


