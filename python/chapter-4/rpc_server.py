###############################################
# RabbitMQ in Action
# Chapter 4.3.3 - RPC Server
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, json

#/(apiserver.0) Establish connection to broker
creds_broker = pika.PlainCredentials("rpc_user", "rpcme")
conn_params = pika.ConnectionParameters("172.18.176.57",
                                        virtual_host = "/",
                                        credentials = creds_broker)
conn_broker = pika.BlockingConnection(conn_params)
channel = conn_broker.channel()

#/(apiserver.1) Declare Exchange & "ping" Call Queue
channel.exchange_declare(exchange="rpc",
                         exchange_type="direct",
                         auto_delete=False)
channel.queue_declare(queue="ping", auto_delete=False)
channel.queue_bind(queue="ping",
                   exchange="rpc",
                   routing_key="ping")

#/(apiserver.2) Wait for RPC calls and reply
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