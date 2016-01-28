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


def assemble_radio_packet(transmitter_id):
    return RadioPacket.create(rorg=RORG.BS4, func=0x20, type=0x01,
                              sender=transmitter_id,
                              CV=50,
                              TMP=21.5,
                              ES='true')


init_logging()
c = SerialCommunicator()
c.start()

# Request transmitter ID
p = Packet(PACKET.COMMON_COMMAND, [0x08])
c.send(p)

# Fetch the transmitter ID for sending packages.
# NOT TESTED!!!
# Needs testing, and if functional, a similar loop should be implemented to the communicator initialization.
# This ID would then be used to send all future messages.
transmitter_id = None
while transmitter_id is None:
    try:
        p = c.receive.get(block=True, timeout=1)
        if p.type == PACKET.RESPONSE:
            transmitter_id = p.response_data
            # send custom radio packet
            c.send(assemble_radio_packet(transmitter_id))
        break
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

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
