from __future__ import print_function

import json
import os
import uuid

import requests
from flask import (abort, flash, g, jsonify, request, send_from_directory,
                   url_for)

from .calculation_module import calculation

from . import api
from .. import CM_NAME, SIGNATURE, URL_MAIN_WEBSERVICE


UPLOAD_DIRECTORY = '/var/hotmaps/cm_uploaded_files'

while True:
    mydir = UPLOAD_DIRECTORY
    try:
        os.makedirs(mydir)
        break
    except OSError, e:
        if e.errno != os.errno.EEXIST:
            raise
            # time.sleep might help here
        pass


@api.route('/files/<string:filename>', methods=['GET'])
def get(filename):
    return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)


@api.route('/register/', methods=['POST'])
def register():
    """ register the Calculation module (CM)to the main web services (MWS)-
    the CM will send its SIGNATURE to the main web service, CM SIGNATURE contains elements to identity the CM and
    how to handle it and the list of input it needs on the user interface. CM SIGNATURE can be find on app/constants.py file, this file must be change manually
    Also constants.py must contains a CM_ID that is a unique number that as to be defined by the CREM (Centre de Recherches Energetiques et Municipales de Martigny)

       ---
       definitions:
         Color:
           type: string
       responses:
         200:
           description: MWS is aware of the CM
           examples:
            results: {"response": {"category": "Buildings", "cm_name": "calculation_module_1", "layers_needed": ["heat_density_tot"], "cm_description": "this computation module allows to ....", "cm_url": "http://127.0.0.1:5002/", "cm_id": 1, "inputs_calculation_module": [{"input_min": 1, "input_value": 1, "input_unit": "none", "input_name": "Reduction factor", "cm_id": 1, "input_type": "input", "input_parameter_name": "reduction_factor", "input_max": 10}, {"input_min": 10, "input_value": 50, "input_unit": "", "input_name": "Blablabla", "cm_id": 1, "input_type": "range", "input_parameter_name": "bla", "input_max": 1000}]}}
             """

    print('CM will register ')

    # base_url = request.base_url.replace("computation-module/register/", "")
    print('CM base_url register ')
    signature_final = SIGNATURE
    ##push

    #signature_final["cm_url"] = base_url

    payload = json.dumps(signature_final)
    print(payload)
    registerCM(payload)
    return json.dumps({'response': payload})


def registerCM(data):
    headers = {'Content-Type': 'application/json'}
    res = requests.post(URL_MAIN_WEBSERVICE + 'api/cm/register/', data=data, headers=headers)
    reponse = res.text
    status_code = res.status_code
    print('res.json() ', res.json())
    print('status_code ', status_code)
    print('reponse ', reponse)
    return requests


def savefile(filename, url):
    print(url)
    r = requests.get(url, stream=True)
    print(r.status_code)
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

    print('CM will Compute ')
    #import ipdb; ipdb.set_trace()
    data = request.get_json()
    url_file = data["url_file"]
    filename = data["filename"]
    # part to modify from the CM rpovider
    # parameters needed from the CM
    reduction_factor = data["reduction_factor"]
    print('reduction_factor ', reduction_factor)
    file_path = savefile(filename, url_file)
    filename = str(uuid.uuid4()) + '.tif'
    path_final = UPLOAD_DIRECTORY + '/' + filename
    #file_path = '/media/lesly/Data/Repositories/Computation_module/cm/app/api_v1/Raster_clip_extend.tif'
    indicator = calculation(file_path, factor=reduction_factor, directory=path_final)
    base_url = request.base_url.replace("compute", "files")
    # 1.2.1  url for downloading raster
    url_download_raster = base_url + filename
    print('indicator {}'.format(indicator))
    response = {
        'indicators': [{
            'indicator_name': 'heat_density',
            'indicator_value': str(indicator),
            'indicator_unit': 'KW', }

        ],
        'tiff_url': url_download_raster,
        'filename': filename

    }
    response = json.dumps(response)
    return response


def call_calculation_module(file_name, factor=2, directory=UPLOAD_DIRECTORY):
    return calculation(file_name, factor=2, directory=UPLOAD_DIRECTORY)


# Delete CM from main API
@api.route('/unregister/' + CM_NAME, methods=['DELETE'])
def unregister_cm(cm_name):
    print('request for deleting CM')
