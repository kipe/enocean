#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Example to show automatic UTE Teach-in responses using
http://www.g-media.fr/prise-gigogne-enocean.html

Waits for UTE Teach-ins, sends the response automatically and prints the ID of new device.
'''

import time
from enocean_async.communicators.serialcommunicator import SerialCommunicator
from enocean_async.protocol.packet import Packet, RadioPacket, UTETeachInPacket
from enocean_async.protocol.constants import RORG
import enocean_async.utils

def set_position(destination, percentage, base_id):
    return RadioPacket.create(rorg=RORG.VLD, rorg_func=0x05, rorg_type=0x00, destination=destination, sender=base_id, command=1, POS=percentage)


devices_learned = []

class USB330DB(SerialCommunicator):
    async def packet(self, packet):
        print(packet)
        return
    async def teachin_packet(self, packet):
        print('New device learned! The ID is %s.' % (packet.sender_hex))
        devices_learned.append(packet.sender)
        return


def main():
    communicator = USB330DB()
    communicator.start()
    time.sleep(0.1)
    print('The Base ID of your module is', enocean_async.utils.to_hex_string(communicator.base_id))


    # set_position([0x05, 0x0F, 0x0B, 0xEA], 100)
    # time.sleep(10)
    packet = set_position([0x05, 0x0F, 0x0B, 0xEA], 50, communicator.base_id)
    communicator.send(packet)


    print('Press and hold the teach-in button on the plug now, till it starts turning itself off and on (about 10 seconds or so...)')
    EXIT = False
    while EXIT is not True:
        e =input("PRESS E TO EXIT\n")
        if e == 'E' or e == 'e':
            EXIT = True
   
    communicator.stop()
    print('Devices learned during this session: %s' % (', '.join([enocean_async.utils.to_hex_string(x) for x in devices_learned])))


if __name__ == "__main__":
    main()
