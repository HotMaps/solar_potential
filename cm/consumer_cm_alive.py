#!/usr/bin/env python
import pika
import logging


from app.constant import RPC_CM_ALIVE,CM_ID,CELERY_BROKER_URL
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

queue_name =  RPC_CM_ALIVE + str(CM_ID)
parameters = pika.URLParameters(str(CELERY_BROKER_URL))
connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.queue_declare(queue=queue_name)



def on_request(ch, method, props, body):
    #body.status = 'up'


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

