#!/usr/bin/env python
import logging
import os
from app import create_app, log
from app.constant import PORT
from app.constant import URL_CM_DOCKER
import requests
import threading
import time
from flask import request
import socket




application = create_app(os.environ.get('FLASK_CONFIG', 'development'))
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                #get the external ip
                ip = socket.gethostbyname(socket.gethostname())
                # the cm will run his register request
                base_url = 'http://'+ str(ip) +':'+ str(PORT) +'/'
                headers = {'Content-Type':  'application/json'}
                r = requests.post(base_url +'computation-module/register/', headers=headers)
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()



log.info(application)
if __name__ == '__main__':
    #start_runner()

    application.run(host='0.0.0.0', port=5001)
    #thread = threading.Thread(target=os.system('python consumer.py &'))

    #thread.start()


    #init_queue()




