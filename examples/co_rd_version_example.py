#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Example on getting the information about the EnOcean controller.
The sending is happening between the application and the EnOcean controller,
no wireless communication is taking place here.

The command used here is specified as 1.10.5 Code 03: CO_RD_VERSION
in the ESP3 document.
"""

from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET
import traceback

try:
    import queue
except ImportError:
    import Queue as queue

init_logging()
"""
'/dev/ttyUSB0' might change depending on where your device is.
To prevent running the app as root, change the access permissions:
'sudo chmod 777 /dev/ttyUSB0'
"""
communicator = SerialCommunicator(port=u'/dev/ttyUSB0', callback=None)
packet = Packet(PACKET.COMMON_COMMAND, [0x03])

communicator.daemon = True
communicator.start()
communicator.send(packet)

while communicator.is_alive():
    try:
        packRec = communicator.receive.get(block=True, timeout=1)
        if packRec.type == PACKET.RESPONSE:
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

if communicator.is_alive():
    communicator.stop()
