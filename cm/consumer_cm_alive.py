#!/usr/bin/env python
import pika
import logging
from app import constant
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

queue_name =  constant.RPC_CM_ALIVE + str(constant.CM_ID)
parameters = pika.URLParameters(str(constant.CELERY_BROKER_URL))
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.queue_declare(queue=queue_name)



def on_request(ch, method, props, body):
    #body.status = 'up'
    LOGGER.info("CM requested with body",body)

    response = body

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)

print(" [x] Awaiting RPC requests")
LOGGER.info(" [x] Awaiting RPC requests")
channel.start_consuming()

