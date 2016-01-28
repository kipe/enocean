#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue


def assemble_radio_packet():
    p = Packet(PACKET.RADIO)
    p.rorg = RORG.BS4
    sender_address = 0x00ffffff
    sender_bytes = [(sender_address >> i & 0xff) for i in (24, 16, 8, 0)]
    # setup default data
    data = [0]*4
    data[3] = 0x08  # clear learn bit
    status = 0  # not repeated
    p.data = [p.rorg] + data + sender_bytes + [status]

    # update data based on EEP
    p.select_eep(0x20, 0x01)
    prop = {
        'CV': 50,
        'TMP': 21.5,
        'ES': 'true',
    }
    p.set_eep(prop)

    # set optional data
    sub_tel_num = 3
    destination = [255, 255, 255, 255]    # broadcast
    dbm = 0xff
    security = 0
    p.optional = [sub_tel_num] + destination + [dbm] + [security]

    return p


init_logging()
c = SerialCommunicator()
c.start()

# send common command
p = Packet(PACKET.COMMON_COMMAND, [0x08])
c.send(p)

# send custom radio packet
# p = assemble_radio_packet()
# c.send(p)

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
