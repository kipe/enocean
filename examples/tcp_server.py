#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.tcpcommunicator import TCPCommunicator
# from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

import Queue

# p = Packet(PACKET.COMMON_COMMAND, [0x08])

init_logging()
tcp = TCPCommunicator()
tcp.start()
# c.send(p)
while tcp.is_alive():
    try:
        # Loop to empty the queue...
        p = tcp.receive.get(block=True, timeout=1)
        if p.type == PACKET.RADIO and p.rorg == RORG.BS4:
            for k in p.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.BS1:
            for k in p.parse_eep(0x00, 0x01):
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.RPS:
            for k in p.parse_eep(0x02, 0x04):
                print('%s: %s' % (k, p.parsed[k]))
    except Queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if tcp.is_alive():
    tcp.stop()
