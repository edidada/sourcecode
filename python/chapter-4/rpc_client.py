###############################################
# RabbitMQ in Action
# Chapter 4.3.3 - RPC Client
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################
import time, json, pika, os, sys
from configparser import ConfigParser

#/(rpcc.0) Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{env}' not found in config.ini")
    print(f"Available environments: {', '.join(config.sections())}")
    sys.exit(1)

#/(rpcc.1) Establish connection to broker using config
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

#/(rpcc.2) Issue RPC call & wait for reply
msg = json.dumps({"client_name": "RPC Client 1.0", 
                  "time" : time.time()})

result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
msg_props = pika.BasicProperties()
msg_props.reply_to=result.method.queue

channel.basic_publish(body=msg,
                      exchange="rpc",
                      properties=msg_props,
                      routing_key="ping")

print("Sent 'ping' RPC call. Waiting for reply...")

def reply_callback(ch, method, properties, body):
    """Receives RPC server replies."""
    print("RPC Reply --- " + body.decode('utf-8'))
    ch.stop_consuming()



channel.basic_consume(queue=result.method.queue,
                      on_message_callback=reply_callback,
                      consumer_tag=result.method.queue)

channel.start_consuming()