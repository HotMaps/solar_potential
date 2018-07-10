#!/usr/bin/env python
import os
from app import create_app
from app.constant import PORT
from app.constant import URL_CM
import requests
import threading
import time


application = create_app(os.environ.get('FLASK_CONFIG', 'development'))


def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                headers = {'Content-Type': 'application/json'}
                r = requests.post(
                    'http://' +
                    URL_CM +
                    ':' +
                    PORT +
                    '/computation-module/register/',
                    headers=headers)
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except BaseException:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__ == '__main__':
    start_runner()
    application.run(host=URL_CM, port=PORT)
