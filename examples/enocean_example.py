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
serCom = SerialCommunicator()
serCom.start()

# Request transmitter ID
pack = Packet(PACKET.COMMON_COMMAND, [0x08])
serCom.send(pack)

# Fetch the transmitter ID for sending packages.
# NOT TESTED!!!
# Needs testing, and if functional, a similar loop should be implemented to the communicator initialization.
# This ID would then be used to send all future messages.
transmitter_id = None
while transmitter_id is None:
    try:
        pack = serCom.receive.get(block=True, timeout=1)
        if pack.type == PACKET.RESPONSE:
            transmitter_id = pack.response_data
            # send custom radio packet
            serCom.send(assemble_radio_packet(transmitter_id))
        break
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

# endless loop receiving radio packets
while serCom.is_alive():
    try:
        # Loop to empty the queue...
        pack = serCom.receive.get(block=True, timeout=1)

        if pack.type == PACKET.RADIO and pack.rorg == RORG.BS4:
            # parse packet with given FUNC and TYPE
            for k in pack.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, pack.parsed[k]))
        if pack.type == PACKET.RADIO and pack.rorg == RORG.BS1:
            # alternatively you can select FUNC and TYPE explicitely
            # pack.select_eep(0x00, 0x01)
            # parse it
            for k in pack.parse_eep(0x00, 0x01):
                print('%s: %s' % (k, pack.parsed[k]))
        if pack.type == PACKET.RADIO and pack.rorg == RORG.RPS:
            for k in pack.parse_eep(0x02, 0x02):
                print('%s: %s' % (k, pack.parsed[k]))
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if serCom.is_alive():
    serCom.stop()
