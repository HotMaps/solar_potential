#!/usr/bin/env python
import logging

import json
import os
import time

from app.api_v1.transactions import register

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

def start_loop():
    not_started = True
    i = 0

    LOGGER.info('In start loop')
    response = register()
    LOGGER.info("[HTAPI]  register response: %s ", response)
    LOGGER.info('Server not yet started')
    i=i+1
    LOGGER.info('count = %s',str(i))

    json.loads(response)
    LOGGER.info('Server started, quiting start_loop')
    not_started = False
    os.system('kill $PPID')


    LOGGER.info('Server not yet started')
    #time.sleep(2)



def start_runner():

    print('Started runner')
    start_loop()



if __name__ == '__main__':
    start_runner()






