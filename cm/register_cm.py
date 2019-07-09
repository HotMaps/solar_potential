#!/usr/bin/env python
import logging

import json

import time

from app.api_v1.transactions import register

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

import psutil

for proc in psutil.process_iter():
    print(proc.name())

def kill_by_process_name(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            print("Killing process: " + name)
            if(check_process_exist_by_name(name)):
                print("Killing process: " + name + " sucess")
            else:
                print("Killing process: " + name + " failed")
            return

    print("Not found process: " + name)

def check_process_exist_by_name(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            return True

    return False



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
                kill_by_process_name("python3 register_cm.py")
                break
            except :

                LOGGER.info('Server not yet started')
                time.sleep(2)

    print('Started runner')
    start_loop()



if __name__ == '__main__':
    start_runner()






