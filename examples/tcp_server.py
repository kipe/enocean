#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.tcpcommunicator import TCPCommunicator
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

init_logging()
communicator = TCPCommunicator()
communicator.start()
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.get_packet()
        if packet is None:
            continue
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS4:
            for k in packet.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, packet.parsed[k]))
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS1:
            for k in packet.parse_eep(0x00, 0x01):
                print('%s: %s' % (k, packet.parsed[k]))
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.RPS:
            for k in packet.parse_eep(0x02, 0x04):
                print('%s: %s' % (k, packet.parsed[k]))
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
