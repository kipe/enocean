#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
import enocean.utils
from enocean.communicators.ESP2serialcommunicator import ESP2SerialCommunicator
from enocean.protocol.constants import PACKET, RORG
from enocean.manufacturer.eltako import *
import sys
import traceback
from time import sleep
import paho.mqtt.client as paho
from enocean.example.devicelist_example import *
import threading, logging

try:
    import queue
except ImportError:
    import Queue as queue

class BreakIt(Exception): pass

def eno_worker(wstop):
    # endless loop receiving radio packets
    mainlogger.info("Worker started...")
    while 1:
        try:
            if wstop.isSet():
                break

            # Loop to empty the queue...
            packet = esp2com.receive.get(block=True, timeout=1)

            if (packet.packet_type in [PACKET.RADIO, PACKET.EVENT]) and (packet.rorg in [RORG.RPS, RORG.BS4, RORG.BS1]):

                button = rockers.new_event(packet)
                if button is not None:
                    if button[1] is RockerEvent.Press:
                        cmqtt.publish("my/home/automation/topic/button/press", payload=button[0], qos=2, retain=False)
                    if button[1] is RockerEvent.Longpress_2s:
                        cmqtt.publish("my/home/automation/topic/button/longpress2", payload=button[0], qos=2, retain=False)
                    if button[1] is RockerEvent.Longpress_5s:
                        cmqtt.publish("my/home/automation/topic/button/longpress5", payload=button[0], qos=2, retain=False)

                for item in hygrometer:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode_humidity(packet)
                        cmqtt.publish(item.Name, payload=EnoValList, qos=2, retain=True)
                        raise BreakIt

                for item in roomsensors:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode(packet)
                        cmqtt.publish(item.Name + "/temperature", payload=EnoValList[0], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/setpoint", payload=EnoValList[1], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/state", payload=EnoValList[2], qos=2, retain=True)
                        raise BreakIt

                if packet.sender_hex == weatherstation.ID:
                    item = weatherstation
                    EnoValList = item.decode(packet)
                    if EnoValList[0] == 0:
                        cmqtt.publish(item.Name + "/lightsensor", payload=EnoValList[1], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/temperature", payload=EnoValList[2], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/windspeed", payload=EnoValList[3], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/rain", payload=EnoValList[4], qos=2, retain=True)
                    else:
                        cmqtt.publish(item.Name + "/sun/west", payload=EnoValList[1], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/sun/south", payload=EnoValList[2], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/sun/east", payload=EnoValList[3], qos=2, retain=True)

                    raise BreakIt

                for item in thermostate:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode(packet)
                        if len(EnoValList) == 3:
                            cmqtt.publish(item.Name + "/temperature", payload=EnoValList[0], qos=2, retain=True)
                            cmqtt.publish(item.Name + "/setpoint", payload=EnoValList[1], qos=2, retain=True)
                            cmqtt.publish(item.Name + "/state", payload=EnoValList[2], qos=2, retain=True)
                        else:
                            cmqtt.publish(item.Name + "/state", payload=EnoValList[0], qos=2, retain=True)

                        raise BreakIt

                for item in shutters:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode(packet)
                        cmqtt.publish(item.Name + "/position", payload=EnoValList[0], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/state", payload=EnoValList[1], qos=2, retain=True)
                        raise BreakIt

                for item in dimmer:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode(packet)
                        cmqtt.publish(item.Name + "/dimmvalue", payload=EnoValList[0], qos=2, retain=True)
                        cmqtt.publish(item.Name + "/state", payload=EnoValList[1], qos=2, retain=True)
                        raise BreakIt

                for item in switches:
                    if packet.sender_hex == item.ID:
                        EnoValList = item.decode(packet)
                        cmqtt.publish(item.Name + "/state", payload=EnoValList, qos=2, retain=True)
                        raise BreakIt

        except queue.Empty:
            continue
        except BreakIt:
            continue
        except KeyboardInterrupt:
            break
        except Exception:
            traceback.print_exc(file=sys.stdout)
            break


def SendSwToggle(communicator, messages):
    communicator.send(messages[0])
    sleep(0.1)
    communicator.send(messages[1])


def on_message_set_dimmerstate(client, userdata, message):
    for item in dimmer:
        if item.Name in message.topic and message.payload != None:
            try:
                newvalue = int(message.payload)
            except ValueError:
                mainlogger.info("Value Error happened with " + str(message.topic))
                return

            esp2com.send(item.send_DimMsg(newState=newvalue)[0])


def on_message_light_toggle(client, userdata, message):
    for item in schwitches:
        if item.Name in message.topic:
            eno_msg = item.send_toggle()
            SendSwToggle(esp2com, eno_msg)


def on_message_set_brightness(client, userdata, message):
    for item in dimmer:
        if item.Name in message.topic and message.payload != None:
            try:
                newvalue = float(message.payload)
            except ValueError:
                mainlogger.info("Value Error happened with " + str(message.topic))
                return

            esp2com.send(item.send_DimMsg(newVal=newvalue)[0])


def on_message_shutter_set_state(client, userdata, message):
    for item in shutters:
        if item.Name in message.topic and message.payload != None:
            try:
                newvalue = int(message.payload)
            except ValueError:
                mainlogger.info("Value Error happened with " + str(message.topic))
                return

            esp2com.send(item.send_Move(newState=newvalue)[0])


def on_message_shutter_set_pos(client, userdata, message):
    for item in schutters:
        if item.Name in message.topic and message.payload != None:
            if item.isMoving:
                #if shutter is moving, stop it first and wait for a position update...
                #tested ok, works perfectly
                runpos = item.pos
                esp2com.send(item.send_Move(newState="Stop")[0])
                timesslept = 0
                while runpos == item.pos:
                    sleep(0.05)
                    timesslept+=1
                    if timesslept*0.05 >= item.tFull_s:
                        #seems like we already were in an endstop, eltako behaviour...
                        break
            #print("Sleep loop delay " + str(timesslept*50.0) + "ms, ran " + str(timesslept) + " times...")
            try:
                newvalue = float(message.payload)
            except ValueError:
                mainlogger.info("Value Error happened with " + str(message.topic))
                return

            esp2com.send(item.send_Move(newpos=float(message.payload))[0])


def on_message_thermo_set_temp(client, userdata, message):
    for item in thermostate:
        if item.Name in message.topic and message.payload != None:
            try:
                newvalue = float(message.payload)
            except ValueError:
                mainlogger.info("Value Error happened with " + str(message.topic))
                return

            esp2com.send(item.send_SetPoint(SetPoint=newvalue, block=1)[0])


def on_message_thermo_set_release(client, userdata, message):
    for item in thermostate:
        if item.Name in message.topic and message.payload != None:
            esp2com.send(item.send_Release()[0])


def on_connect(client, userdata, flags, rc):
    cmqtt.subscribe("my/home/automation/topic/#", qos=2)
    mainlogger.info("Connected to MQTT-Broker with result code "+str(rc))


def on_disconnect(cmqtt, obj, rc):
    mainlogger.info("Disconnected from MQTT-Broker with result code "+str(rc))


def on_message(mosq, obj, msg):
    mainlogger.info("From mqtt-broker: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


init_logging()

mainlogger = logging.getLogger('eno_backend')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
mainlogger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
mainlogger.addHandler(stream_handler)

esp2com = ESP2SerialCommunicator()
cmqtt = paho.Client(client_id="", clean_session=True)
cmqtt.username_pw_set(username="", password="")
cmqtt.message_callback_add("my/home/automation/topic", on_message_set_brightness)
cmqtt.message_callback_add("my/home/automation/topic", on_message_set_dimmerstate)
cmqtt.message_callback_add("my/home/automation/topic", on_message_light_toggle)
cmqtt.message_callback_add("my/home/automation/topic", on_message_shutter_set_state)
cmqtt.message_callback_add("my/home/automation/topic", on_message_shutter_set_pos)
cmqtt.message_callback_add("my/home/automation/topic", on_message_thermo_set_temp)
cmqtt.message_callback_add("my/home/automation/topic", on_message_thermo_set_release)
cmqtt.on_message = on_message
cmqtt.on_connect = on_connect
cmqtt.on_disconnect = on_disconnect

cmqtt.connect("", port=0000)
esp2com.start()

wstop = threading.Event()
t = threading.Thread(name='eno-worker', target=eno_worker, args=(wstop,))
t.start()

mainlogger.info("Starting MQTT...")

cmqtt.loop_forever()

mainlogger.info('MQTT Exited, stopping other workers...')

if t.is_alive():
    wstop.set()
    t.join(timeout=10)

if esp2com.is_alive():
    esp2com.stop()
