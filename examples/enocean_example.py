#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet, RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue


def assemble_radio_packet():
    return RadioPacket.create(rorg=RORG.BS4, func=0x20, type=0x01,
                              sender=[0xDE, 0xAD, 0xBE, 0xFF],
                              CV=50,
                              TMP=21.5,
                              ES='true')


init_logging()
c = SerialCommunicator()
c.start()

# send common command
p = Packet(PACKET.COMMON_COMMAND, [0x08])
c.send(p)

# send custom radio packet
c.send(assemble_radio_packet())

# endless loop receiving radio packets
while c.is_alive():
    try:
        # Loop to empty the queue...
        p = c.receive.get(block=True, timeout=1)

        if p.type == PACKET.RADIO and p.rorg == RORG.BS4:
            # parse packet with given FUNC and TYPE
            for k in p.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.BS1:
            # alternatively you can select FUNC and TYPE explicitely
            p.select_eep(0x00, 0x01)
            # parse it
            for k in p.parse_eep():
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.RPS:
            for k in p.parse_eep(0x02, 0x02):
                print('%s: %s' % (k, p.parsed[k]))
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if c.is_alive():
    c.stop()
