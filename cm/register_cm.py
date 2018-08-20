#!/usr/bin/env python
import logging
import os
from app import create_app, log
from app import constant
import json
import requests
import threading
import time
from flask import request
from app.api_v1.transactions import register
import socket
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)



def start_runner():
    def start_loop():
        not_started = True
        i = 0
        while not_started:
            LOGGER.info('In start loop')
            response = register()
            LOGGER.info("[HTAPI]  register response: %s ", response)
            LOGGER.info('Server not yet started')
            i=i+1
            LOGGER.info('count = %s',str(i))
            try:
                json.loads(response)
                LOGGER.info('Server started, quiting start_loop')
                not_started = False
            except Exception, e:
                print ("something wrong happernd",e)
                LOGGER.info('Server not yet started')
                time.sleep(2)

    print('Started runner')
    start_loop()



if __name__ == '__main__':
    start_runner()






