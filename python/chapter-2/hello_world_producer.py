###############################################
# RabbitMQ in Action
# Chapter 1 - Hello World Producer
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, sys, os
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
conn_broker = pika.BlockingConnection(conn_params) #/(hwp.1) Establish connection to broker


channel = conn_broker.channel() #/(hwp.2) Obtain channel

channel.exchange_declare(exchange="hello-exchange", #/(hwp.3) Declare the exchange
                         exchange_exchange_type="direct",
                         passive=False,
                         durable=True,
                         auto_delete=False)

msg = sys.argv[1]
msg_props = pika.BasicProperties()
msg_props.content_type = "text/plain" #/(hwp.4) Create a plaintext message

channel.basic_publish(body=msg,
                      exchange="hello-exchange",
                      properties=msg_props,
                      routing_key="hola") #/(hwp.5) Publish the message
