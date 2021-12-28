#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import datetime
import time
from influxdb import InfluxDBClient
import logging

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("my/home/automation/topic/#", qos=2)
    client.subscribe("my/home/automation/topic/#", qos=2)
    client.subscribe("my/home/automation/topic/#", qos=2)
    client.subscribe("my/home/automation/topic/hygro", qos=2)
    client.subscribe("my/home/automation/topic/#", qos=2)

def on_message(client, userdata, msg):
    # Use utc as timestamp
    receiveTime=datetime.datetime.utcnow()
   
    isfloatValue=False
    try:
        # Convert the string to a float so that it is stored as a number and not a string in the database
        message=msg.payload.decode("utf-8")
        val = float(message)
        isfloatValue=True
    except ValueError:
        isfloatValue=False
        mainlogger.info("got a non-float from " + str(msg.topic))

    if isfloatValue:
        mainlogger.info(str(msg.topic) + ": " + str(msg.payload))

        json_body = [
            {
                "measurement": msg.topic,
                "time": receiveTime,
                "fields": {
                    "value": val
                }
            }
        ]

        try:
            dbclient.write_points(json_body)
        except:
            mainlogger.info("ERROR WHILE SENDING TO INFLUX!!")

    # else:
    #     print(str(receiveTime) + ": " + msg.topic + " " + message)
    #
    #     json_body = [
    #         {
    #             "measurement": msg.topic,
    #             "time": receiveTime,
    #             "fields": {
    #                 "value": message
    #             }
    #         }
    #     ]
    #
    # dbclient.write_points(json_body)

# Set up a client for InfluxDB


mainlogger = logging.getLogger('eno_influx_logger')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
mainlogger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
mainlogger.addHandler(stream_handler)

mainlogger.info("Starting...")
dbclient = InfluxDBClient(host='', port=0000, database='')

mainlogger.info("InfluxConn OK...")

# Initialize the MQTT client that should connect to the Mosquitto broker
client = mqtt.Client(client_id="")
client.username_pw_set(username="", password="")
client.on_connect = on_connect
client.on_message = on_message
connOK=False
while(connOK == False):
    try:
        client.connect("", port=0000, keepalive=60, )
        connOK = True
        mainlogger.info("MQTTConn OK...")
    except:
        connOK = False
    time.sleep(2)

# Blocking loop to the Mosquitto broker
client.loop_forever()