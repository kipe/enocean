#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
import enocean.utils
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import PACKET, RORG
from enocean.protocol.eep import EEP
import sys
import traceback
import glob
try:
    import queue
except ImportError:
    import Queue as queue


init_logging()
communicator = SerialCommunicator(port=(glob.glob('/dev/serial/by-id/*EnOcean*')+glob.glob('/dev/ttyAMA*')+glob.glob('/dev/ttyUSB*'))[0])
communicator.start()

print(f'The Base ID of your module is {enocean.utils.to_hex_string(communicator.base_id)}')
print(f'Remaining resets of base id: {communicator.remaining_base_id_writes}')
for info, value in communicator.version_info.items():
    print(f'{info}: {value}')

communicator.stop()
