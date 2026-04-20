###############################################
# RabbitMQ in Action
# Chapter 1 - Hello World Consumer
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, os, sys
from configparser import ConfigParser

# Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'chapter-4', 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{env}' not found in config.ini")
    sys.exit(1)

# Use guest credentials for chapter-2 examples
credentials = pika.PlainCredentials("guest", "guest")
conn_params = pika.ConnectionParameters(
    host=config.get(env, 'host'),
    port=config.getint(env, 'port'),
    credentials=credentials
)
conn_broker = pika.BlockingConnection(conn_params) #/(hwc.1) Establish connection to broker


channel = conn_broker.channel() #/(hwc.2) Obtain channel

channel.exchange_declare(exchange="hello-exchange", #/(hwc.3) Declare the exchange
                         exchange_exchange_type="direct",
                         passive=False,
                         durable=True,
                         auto_delete=False)

channel.queue_declare(queue="hello-queue") #/(hwc.4) Declare the queue

channel.queue_bind(queue="hello-queue",     #/(hwc.5) Bind the queue and exchange together on the key "hola"
                   exchange="hello-exchange",
                   routing_key="hola")


def msg_consumer(ch, method, properties, body): #/(hwc.6) Make function to process incoming messages
    
    ch.basic_ack(delivery_tag=method.delivery_tag)  #/(hwc.7) Message acknowledgement
    
    body_str = body.decode('utf-8')
    if body_str == "quit":
        ch.basic_cancel(consumer_tag="hello-consumer") #/(hwc.8) Stop consuming more messages and quit
        ch.stop_consuming()
    else:
        print(body_str)
    
    return



channel.basic_consume(queue="hello-queue",    #/(hwc.9) Subscribe our consumer
                       on_message_callback=msg_consumer,
                       consumer_tag="hello-consumer")

channel.start_consuming() #/(hwc.10) Start consuming
