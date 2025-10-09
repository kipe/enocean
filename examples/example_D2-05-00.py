#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Example to show automatic UTE Teach-in responses using
http://www.g-media.fr/prise-gigogne-enocean.html

Waits for UTE Teach-ins, sends the response automatically and prints the ID of new device.
'''

import queue
import sys
import traceback

import enocean.utils
from enocean.communicators import SerialCommunicator
from enocean.protocol.constants import RORG
from enocean.protocol.packet import RadioPacket, UTETeachInPacket


def set_position(destination, percentage):
    global communicator
    communicator.send(
        RadioPacket.create(rorg=RORG.VLD, rorg_func=0x05, rorg_type=0x00, destination=destination, sender=communicator.base_id, command=1, POS=percentage)
    )



communicator = SerialCommunicator()
communicator.start()
print('The Base ID of your module is %s.' % enocean.utils.to_hex_string(communicator.base_id))


# set_position([0x05, 0x0F, 0x0B, 0xEA], 100)
# time.sleep(10)
set_position([0x05, 0x0F, 0x0B, 0xEA], 50)


print('Press and hold the teach-in button on the plug now, till it starts turning itself off and on (about 10 seconds or so...)')
devices_learned = []

# endless loop receiving radio packets
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.receive.get(block=True, timeout=1)
        if isinstance(packet, UTETeachInPacket):
            print('New device learned! The ID is %s.' % (packet.sender_hex))
            devices_learned.append(packet.sender)
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

print('Devices learned during this session: %s' % (', '.join([enocean.utils.to_hex_string(x) for x in devices_learned])))

if communicator.is_alive():
    communicator.stop()
