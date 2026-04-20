###############################################
# RabbitMQ in Action
# Chapter 9 - RMQ Queue Statistics
###############################################
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################
import sys, json, http.client, urllib.parse, base64

#/(qs.0) Validate argument count
if len(sys.argv) < 6:
    print("USAGE: queue_stats.py server_name:port auth_user auth_pass VHOST QUEUE_NAME")
    sys.exit(1)

#/(qs.1) Assign arguments to memorable variables
server, port = sys.argv[1].split(":")
username = sys.argv[2]
password = sys.argv[3]
vhost = sys.argv[4]
queue_name = sys.argv[5]

#/(qs.2) Build API path
vhost = urllib.parse.quote(vhost, safe='')
queue_name = urllib.parse.quote(queue_name, safe='')
path = "/api/queues/%s/%s" % (vhost, queue_name)
#/(qs.3) Set the request method
method = "GET"

#/(qs.4) Connect to the API server
conn = http.client.HTTPConnection(server, int(port))
#/(qs.5) Base64 the username/password
credentials = base64.b64encode(("%s:%s" % (username, password)).encode('utf-8')).decode('utf-8')
#/(qs.6) Set the content-type and credentials
headers = {"Content-Type" : "application/json",
           "Authorization" : "Basic " + credentials}
#/(qs.7) Send the request
conn.request(method, path, "", headers)
#/(qs.8) Receive the response.
response = conn.getresponse()
if response.status > 299:
    print("Error executing API call (%d): %s" % (response.status,
                                                 response.read().decode('utf-8')))
    sys.exit(2)

#/(qs.9) Decode response
resp_payload = json.loads(response.read().decode('utf-8'))

#/(qs.10) Display queue statistics
print("'%s' Queue Stats" % urllib.parse.unquote(queue_name))
