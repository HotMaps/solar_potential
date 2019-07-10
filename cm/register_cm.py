#!/usr/bin/env python
import logging

import json

import time
from app.constant import CM_ID
from app.api_v1.transactions import register

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)



def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            LOGGER.info('In start loop')
            response = register()
            LOGGER.info('Server not yet started')

            if type(response) is bytes:
                # if the type is byte we tconvert the response to STR
                response = json.loads(response.decode('utf-8'))
            print (' response', response)
            # then we dcode this response
            cm = json.loads(response)
            cm_id = cm["cm_id"]
            if str(CM_ID) == str(cm_id) :
                LOGGER.info('Server started, quiting start_loop')
                not_started = False
            else:
                LOGGER.info('Server have not registerd for some reason')
            time.sleep(2)

    print('Started runner 1')
    start_loop()



if __name__ == '__main__':
    start_runner()








