###############################################
# RabbitMQ in Action
# Chapter 1 - Hello World Producer
#             w/ Publisher Confirms
# 
# Requires: pika >= 0.9.6
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, os, sys
from configparser import ConfigParser, sys
from pika import spec

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
conn_broker = pika.BlockingConnection(conn_params) 

channel = conn_broker.channel()

def confirm_handler(frame): #/(hwppc.1) Publisher confirm handler
    if type(frame.method) == spec.Confirm.SelectOk:
        print("Channel in 'confirm' mode.")
    elif type(frame.method) == spec.Basic.Nack:
        if frame.method.delivery_tag in msg_ids:
            print("Message lost!")
    elif type(frame.method) == spec.Basic.Ack:
        if frame.method.delivery_tag in msg_ids:
            print("Confirm received!")
            msg_ids.remove(frame.method.delivery_tag)

#/(hwppc.2) Put channel in "confirm" mode
channel.confirm_delivery(callback=confirm_handler)

msg = sys.argv[1]
msg_props = pika.BasicProperties()
msg_props.content_type = "text/plain"

msg_ids = [] #/(hwppc.3) Reset message ID tracker

channel.basic_publish(body=msg,
                      exchange="hello-exchange",
                      properties=msg_props,
                      routing_key="hola") #/(hwppc.4) Publish the message

msg_ids.append(len(msg_ids) + 1) #/(hwppc.5) Add ID to tracking list

channel.close()

