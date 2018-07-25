from flask import request, abort, jsonify ,url_for, g,flash
from . import api
from .. import SIGNATURE,CM_NAME
import json
import requests
from calculation_module import calculation
import os
from flask import send_from_directory
import uuid
from app import constant
from app.constant import PORT,RPC_Q
from app.api_v1 import errors
import socket





UPLOAD_DIRECTORY = '/var/hotmaps/cm_files_uploaded'
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0777)

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
    ip = socket.gethostbyname(socket.gethostname())
    base_url = 'http://'+ str(ip) +':'+ str(PORT) +'/'
    signature_final = SIGNATURE
    signature_final["cm_url"] = base_url
    payload = json.dumps(signature_final)
    return registerCM(payload)

# TODO: WP4 Developer create q register queue
def registerCM(data):
    headers = {'Content-Type':  'application/json'}
    res = requests.post( ""+'api/cm/register/', data = data, headers = headers)


    reponse = res.text
    status_code = res.status_code
    return reponse



def savefile(filename,url):
    r = requests.get(url, stream=True)
    path = None
    if r.status_code == 200:
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    return path

@api.route('/compute/', methods=['POST'])
def compute():

    """ compute the Calculation module (CM)from the main web services (MWS)-
    the main web service is sending
        ---
       parameters:
          - name: filename
            in: path
            type: string
            required: true
            default: 6d998d5c-5139-4f77-b0b3-8ee078e4527c.tif
          - name: url_file
            in: path
            type: string
            required: true
            default: http://127.0.0.1:5000/api/cm/files/6d998d5c-5139-4f77-b0b3-8ee078e4527c.tif
          - name: reduction_factor
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
            results: {"response": {"category": "Buildings", "cm_name": "calculation_module_1", "layers_needed": ["heat_density_tot"], "cm_description": "this computation module allows to ....", "cm_url": "http://127.0.0.1:5002/", "cm_id": 1, "inputs_calculation_module": [{"input_min": 1, "input_value": 1, "input_unit": "none", "input_name": "Reduction factor", "cm_id": 1, "input_type": "input", "input_parameter_name": "reduction_factor", "input_max": 10}, {"input_min": 10, "input_value": 50, "input_unit": "", "input_name": "Blablabla", "cm_id": 1, "input_type": "range", "input_parameter_name": "bla", "input_max": 1000}]}}
             """

    # the line of code bellow allow o debug a request
    #import ipdb; ipdb.set_trace()
    data = request.get_json()

    url_file = data["url_file"]
    filename = data["filename"]
    # part to modify from the CM rpovider
        #parameters needed from the CM
    #TODO: CM provider name of the input for the calculation module from the front end
    reduction_factor = data["reduction_factor"]
    file_path = savefile(filename,url_file)
    filename = str(uuid.uuid4()) + '.tif'
    path_final = UPLOAD_DIRECTORY+'/'+filename
    indicator = calculation(file_path, factor=reduction_factor, directory=path_final)
    base_url =  request.base_url.replace("compute","files")
    url_download_raster = base_url + filename
# 1.2.1  generate the indicators
    response = {
        'values': [{
            'name': 'heat demand from Calculation Module',
            'value': str(indicator),
            'unit': 'MWh',}

        ],

        'tiff_url': url_download_raster,
        'filename': filename

    }
    response = json.dumps(response)
    return response




