#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Example on getting the information about the EnOcean controller.
The sending is happening between the application and the EnOcean controller,
no wireless communication is taking place here.

The command used here is specified as 1.10.5 Code 03: CO_RD_VERSION
in the ESP3 document.
"""

from enocean_async.consolelogger import init_logging
from enocean_async.communicators.serialcommunicator import SerialCommunicator
from enocean_async.protocol.constants import RORG
import asyncio
import time
from functools import partial
import serial_asyncio
from enocean_async import utils

"""
'/dev/ttyUSB0' might change depending on where your device is.
To prevent running the app as root, change the access permissions:
'sudo chmod 777 /dev/ttyUSB0'
"""
class USB300DB(SerialCommunicator):
    async def packet(self, packet):
        if packet.rorg == RORG.VLD:
            packet.select_eep(0x05, 0x00)
            packet.parse_eep()
            await asyncio.sleep(0)
            for k in packet.parsed:
                print('%s: %s' % (k, packet.parsed[k]))
                await asyncio.sleep(0)
            
            return
    
        if packet.rorg == RORG.BS4:
            # parse packet with given FUNC and TYPE
            for k in packet.parse_eep(0x02, 0x05):
                await asyncio.sleep(0)
                print('%s: %s' % (k, packet.parsed[k]))

        if packet.rorg == RORG.BS1:
            # alternatively you can select FUNC and TYPE explicitely
            packet.select_eep(0x00, 0x01)
            # parse it
            packet.parse_eep()
            await asyncio.sleep(0)
            for k in packet.parsed:
                print('%s: %s' % (k, packet.parsed[k]))
                await asyncio.sleep(0)


        if packet.rorg == RORG.RPS:
            for k in packet.parse_eep(0x02, 0x02):
                await asyncio.sleep(0)
                print('%s: %s' % (k, packet.parsed[k]))


def main():
    init_logging()
    Gateway = USB300DB()
    Gateway.start()
    input("PRESS A BUTTON TO EXIT\n")
    Gateway.stop()

if __name__ == "__main__" :
    main()
    