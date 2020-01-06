#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Example to show automatic UTE Teach-in responses using
http://www.g-media.fr/prise-gigogne-enocean.html

Waits for UTE Teach-ins, sends the response automatically and prints the ID of new device.
'''

import time
import traceback
import enocean_async.utils
from enocean_async.communicators.serialcommunicator import SerialCommunicator
from enocean_async.protocol.packet import RadioPacket, UTETeachInPacket
from enocean_async.protocol.constants import RORG

devices_learned = []

class USB330DB(SerialCommunicator):
    async def packet(self, packet):
        print(packet)
        return
    async def teachin_packet(self, packet):
        print('New device learned! The ID is %s.' % (packet.sender_hex))
        devices_learned.append(packet.sender)
        return

    def send_command(self, destination, output_value):
        self.send(RadioPacket.create(rorg=RORG.VLD, rorg_func=0x01, rorg_type=0x01,
         destination=destination, sender=self.base_id, command=1, IO=0x1E, OV=output_value))
        
    def turn_on(self, destination):
        self.send_command(destination, 100)

    def turn_off(self, destination):
        self.send_command(destination, 0)



def main():
    communicator = USB330DB()
    communicator.start()
    time.sleep(0.1)
    print('The Base ID of your module is %s.' % enocean_async.utils.to_hex_string(communicator.base_id))


    # Example of turning switches on and off
    communicator.turn_on([0x01, 0x94, 0xB9, 0x46])
    # Needs a bit of sleep in between, working too fast :S
    time.sleep(0.1)
    communicator.turn_on([0x01, 0x94, 0xE3, 0xB9])
    time.sleep(1)

    communicator.turn_off([0x01, 0x94, 0xB9, 0x46])
    time.sleep(0.1)
    communicator.turn_off([0x01, 0x94, 0xE3, 0xB9])


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

