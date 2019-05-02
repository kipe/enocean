#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
import enocean.utils
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue


def assemble_radio_packet(transmitter_id):  #i'm sending as an example an Actuator Status Query to the plug     
    return  RadioPacket.create(rorg=RORG.VLD, rorg_func=0x01, rorg_type=0x09, command=3, destination=[0x01, 0x87, 0xBC, 0x25], sender=communicator.base_id, IO=0x1E)
                                                                                                      #this is my plug_id
#init_logging()
communicator = SerialCommunicator(port=u'/dev/ttyUSB0', callback=None)
communicator.start()
print('The Base ID of your module is %s.' % enocean.utils.to_hex_string(communicator.base_id))

if communicator.base_id is not None:
    print('Sending example package.')
    communicator.send(assemble_radio_packet(communicator.base_id))

# endless loop receiving radio packets
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.receive.get(block=True, timeout=1)
       
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.VLD:
           # in this way i'll parse the correct command of the radio packet sent by the plug
            packet.select_eep(0x01, 0x09, command=packet.command)
           # parse it
            packet.parse_eep()
            for k in packet.parsed:
                print('%s: %s\n' % (k, packet.parsed[k]))

            
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
