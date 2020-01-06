#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from enocean_async.consolelogger import init_logging
import time
import traceback
import enocean_async.utils
from enocean_async.communicators.serialcommunicator import SerialCommunicator
from enocean_async.protocol.packet import RadioPacket, UTETeachInPacket
from enocean_async.protocol.constants import RORG


class USB330DB(SerialCommunicator):
    async def packet(self, packet):
        if packet.rorg == RORG.VLD:
           # in this way i'll parse the correct command of the radio packet sent by the plug
            packet.select_eep(0x01, 0x09, command=packet.command)
           # parse it
            packet.parse_eep()
            for k in packet.parsed:
                print('%s: %s\n' % (k, packet.parsed[k]))
        return


    def Status_Query(self, destination_id):
        '''i'm sending as an example an Actuator Status Query to the plug'''
        self.send(RadioPacket.create(rorg=RORG.VLD, rorg_func=0x01, rorg_type=0x09, command=3,
         destination=destination_id, sender=self.base_id, IO=0x1E))
        return




def main():
    init_logging()
    communicator = USB330DB()
    communicator.start()
    time.sleep(0.1)
    print('The Base ID of your module is %s.' % enocean_async.utils.to_hex_string(communicator.base_id))
    communicator.Status_Query([0x01, 0x87, 0xBC, 0x25])  #This is my plug_id
    print('Press and hold the teach-in button on the plug now, till it starts turning itself off and on (about 10 seconds or so...)')
    EXIT = False
    while EXIT is not True:
        e =input("PRESS E TO EXIT\n")
        if e == 'E' or e == 'e':
            EXIT = True
   
    communicator.stop()




if __name__=='__main__':
    main()