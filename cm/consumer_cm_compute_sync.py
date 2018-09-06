#!/usr/bin/env python
import pika



import socket
import requests
import logging
from app.constant import PORT,CM_ID,CELERY_BROKER_URL,RPC_Q,TRANFER_PROTOCOLE
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
queue_name =  RPC_Q + str(CM_ID)
parameters = pika.URLParameters(CELERY_BROKER_URL)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.queue_declare(queue=queue_name)



def on_request(ch, method, props, body):
    #body.status = 'up'

    print ('body',body)

    headers = {'Content-Type':  'application/json'}
    ip = socket.gethostbyname(socket.gethostname())

    base_url = TRANFER_PROTOCOLE+ str(ip) +':'+str(PORT)+'/computation-module/compute/'
    print ('base_url ', base_url)
    res = requests.post(base_url, data = body, headers = headers)
    response = res.text
    print ('onRequest response', response)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)

print(" [x] Awaiting RPC requests")
channel.start_consuming()

