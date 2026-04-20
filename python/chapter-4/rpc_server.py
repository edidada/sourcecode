###############################################
# RabbitMQ in Action
# Chapter 4.3.3 - RPC Server
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, json, os, sys
from configparser import ConfigParser

#/(apiserver.0) Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{env}' not found in config.ini")
    print(f"Available environments: {', '.join(config.sections())}")
    sys.exit(1)

#/(apiserver.1) Establish connection to broker using config
creds_broker = pika.PlainCredentials(
    config.get(env, 'username'),
    config.get(env, 'password')
)
conn_params = pika.ConnectionParameters(
    host=config.get(env, 'host'),
    port=config.getint(env, 'port'),
    virtual_host=config.get(env, 'virtual_host'),
    credentials=creds_broker
)
conn_broker = pika.BlockingConnection(conn_params)
channel = conn_broker.channel()

#/(apiserver.2) Declare Exchange & "ping" Call Queue
channel.exchange_declare(exchange="rpc",
                         exchange_type="direct",
                         auto_delete=False)
channel.queue_declare(queue="ping", auto_delete=False)
channel.queue_bind(queue="ping",
                   exchange="rpc",
                   routing_key="ping")

#/(apiserver.3) Wait for RPC calls and reply
def api_ping(ch, method, properties, body):
    """'ping' API call."""
    ch.basic_ack(delivery_tag=method.delivery_tag)
    msg_dict = json.loads(body.decode('utf-8'))
    print("Received API call...replying...")
    ch.basic_publish(body="Pong!" + str(msg_dict["time"]),
                          exchange="",
                          routing_key=properties.reply_to)

channel.basic_consume(queue="ping",
                      on_message_callback=api_ping,
                      consumer_tag="ping")

print("Waiting for RPC calls...")
channel.start_consuming()