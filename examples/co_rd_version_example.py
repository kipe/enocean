#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#For working with the lib without 
import sys
sys.path.append("/home/alan/Workspace/python-enocean/rename-enocean-lib/")

from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet, RadioPacket
from enocean.protocol.constants import PACKET, RORG
import traceback

try:
    import queue
except ImportError:
    import Queue as queue


init_logging()

serCom = SerialCommunicator(port=u'/dev/ttyUSB0', callback=None)
pack = Packet(PACKET.COMMON_COMMAND, [0x03])

serCom.daemon = True
serCom.start()
serCom.send(pack)

# endless loop receiving radio packets
while serCom.is_alive():
    try:
        # Loop to empty the queue...
        packRec = serCom.receive.get(block=True, timeout=1)
        if packRec.type == PACKET.RESPONSE:
            print "Packet is RESPONSE"   
            print "Return Code: " + str(packRec.data[0])    
            print "APP version: " + str(bytearray(packRec.data[1:5])).encode('hex')
            print "API version: " + str(bytearray(packRec.data[5:9])).encode('hex')
            print "Chip ID: " + str(bytearray(packRec.data[9:13])).encode('hex')
            print "Chip Version: " + str(bytearray(packRec.data[13:17])).encode('hex')
            print "App Description Version: " + str(bytearray(packRec.data[17:])) 

    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if serCom.is_alive():
    serCom.stop()
