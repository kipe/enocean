#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#For working with the lib without 
import sys
sys.path.append("/home/alan/Workspace/python-enocean/rename-enocean-lib/")

from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet, RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback
import ipdb

try:
    import queue
except ImportError:
    import Queue as queue


#init_logging()

serCom = SerialCommunicator(port=u'/dev/ttyUSB0', callback=None)
pack = Packet(PACKET.COMMON_COMMAND, [0x03])
serCom.daemon = True
serCom.start()

# The SerialCommunicator is running in a separate thread. It will print on recieved messages
# even if you stop this thread

#ipdb.set_trace()
# Request transmitter ID
#SserCom.send(pack)

# endless loop receiving radio packets

while serCom.is_alive():
    try:
        ipdb.set_trace()
        # Loop to empty the queue...
        packRec = serCom.receive.get(block=True, timeout=1)
        if packRec.type == PACKET.COMMON_COMMAND:
            print "Packet is COMMON_COMMAND"
            print pack.data
        if packRec.type == PACKET.RESPONSE:

            print "Packet is RESPONSE"            
            for i in packRec.data :
                print str(hex(i))


    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if serCom.is_alive():
    serCom.stop()
