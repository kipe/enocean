#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Example on getting the information about the EnOcean controller.
The sending is happening between the application and the EnOcean controller,
no wireless communication is taking place here.

The command used here is specified as 1.10.5 Code 03: CO_RD_VERSION
in the ESP3 document.
"""

import queue
import sys
import traceback

from enocean import utils
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.consolelogger import init_logging
from enocean.protocol.constants import PACKET
from enocean.protocol.packet import Packet

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
        receivedPacket = communicator.receive.get(block=True, timeout=1)
        if receivedPacket.packet_type == PACKET.RESPONSE:
            print('Return Code: %s' % utils.to_hex_string(receivedPacket.data[0]))
            print('APP version: %s' % utils.to_hex_string(receivedPacket.data[1:5]))
            print('API version: %s' % utils.to_hex_string(receivedPacket.data[5:9]))
            print('Chip ID: %s' % utils.to_hex_string(receivedPacket.data[9:13]))
            print('Chip Version: %s' % utils.to_hex_string(receivedPacket.data[13:17]))
            print('App Description Version: %s' % utils.to_hex_string(receivedPacket.data[17:]))
            print('App Description Version (ASCII): %s' % str(bytearray(receivedPacket.data[17:])))

    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
