# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division

from enocean.protocol.packet import Packet, RadioPacket
from enocean.protocol.constants import PACKET, RORG


def test_packet_assembly():
    PACKET_CONTENT_1 = bytearray([
        0x55,
        0x00, 0x0A, 0x00, 0x01,
        0x80,
        0xA5, 0x00, 0x00, 0x00, 0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x00,
        0x18
    ])
    PACKET_CONTENT_2 = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x00, 0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0xE4
    ])
    PACKET_CONTENT_3 = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x32, 0x20, 0x89, 0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x43
    ])

    # manually assemble packet
    p = Packet(PACKET.RADIO)
    p.rorg = RORG.BS4
    sender_bytes = [(0xdeadbeef >> i & 0xff) for i in (24, 16, 8, 0)]
    data = [0, 0, 0, 0]
    p.data = [p.rorg] + data + sender_bytes + [0]

    # test content
    packet_serialized = p.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_1)
    assert list(packet_serialized) == list(PACKET_CONTENT_1)

    # set optional data
    sub_tel_num = 3
    destination = [255, 255, 255, 255]    # broadcast
    dbm = 0xff
    security = 0
    p.optional = [sub_tel_num] + destination + [dbm] + [security]

    # test content
    packet_serialized = p.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_2)
    assert list(packet_serialized) == list(PACKET_CONTENT_2)

    # update data based on EEP
    p.select_eep(0x20, 0x01)
    prop = {
        'CV': 50,
        'TMP': 21.5,
        'ES': 'true',
    }
    p.set_eep(prop)

    # test content
    packet_serialized = p.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_3)
    assert list(packet_serialized) == list(PACKET_CONTENT_3)
    assert p.rorg_func == 0x20
    assert p.rorg_type == 0x01
