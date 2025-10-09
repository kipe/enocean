#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Example to show automatic UTE Teach-in responses using
http://www.g-media.fr/prise-gigogne-enocean.html

Waits for UTE Teach-ins, sends the response automatically and prints the ID of new device.
'''

import queue
import sys
import time
import traceback

import enocean.utils
from enocean.communicators import SerialCommunicator
from enocean.protocol.constants import RORG
from enocean.protocol.packet import RadioPacket, UTETeachInPacket


def send_command(destination, output_value):
    global communicator
    communicator.send(
        RadioPacket.create(rorg=RORG.VLD, rorg_func=0x01, rorg_type=0x01, destination=destination, sender=communicator.base_id, command=1, IO=0x1E, OV=output_value)
    )


def turn_on(destination):
    send_command(destination, 100)


def turn_off(destination):
    send_command(destination, 0)


communicator = SerialCommunicator()
communicator.start()
print('The Base ID of your module is %s.' % enocean.utils.to_hex_string(communicator.base_id))

# Example of turning switches on and off
turn_on([0x01, 0x94, 0xB9, 0x46])
# Needs a bit of sleep in between, working too fast :S
time.sleep(0.1)
turn_on([0x01, 0x94, 0xE3, 0xB9])
time.sleep(1)

turn_off([0x01, 0x94, 0xB9, 0x46])
time.sleep(0.1)
turn_off([0x01, 0x94, 0xE3, 0xB9])


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
