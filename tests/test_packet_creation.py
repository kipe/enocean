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

    # Test the easier method of sending packets.
    p = Packet.create(PACKET.RADIO, rorg=RORG.BS4, func=0x20, learn=True, type=0x01, **prop)
    packet_serialized = p.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_3)
    assert list(packet_serialized) == list(PACKET_CONTENT_3)
    assert p.rorg_func == 0x20
    assert p.rorg_type == 0x01

    # Test creating RadioPacket directly.
    p = RadioPacket.create(rorg=RORG.BS4, func=0x20, learn=True, type=0x01, **prop)
    packet_serialized = p.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_3)
    assert list(packet_serialized) == list(PACKET_CONTENT_3)
    assert p.rorg_func == 0x20
    assert p.rorg_type == 0x01


# Corresponds to the tests done in test_eep
def test_temperature():
    TEMPERATURE = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x5C
    ])
    p = RadioPacket.create(rorg=RORG.BS4, func=0x02, type=0x05, sender=[0x01, 0x81, 0xB7, 0x44], TMP=26.66666666666666666666666666666666666666666667)
    packet_serialized = p.build()
    assert len(packet_serialized) == len(TEMPERATURE)
    assert list(packet_serialized) == list(TEMPERATURE)


# Corresponds to the tests done in test_eep
def test_magnetic_switch():
    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x08, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0xBA
    ])
    p = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], CO='open')
    packet_serialized = p.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)

    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x09, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x2E
    ])

    p = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], CO='closed')
    packet_serialized = p.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)


# TODO!!
# Would require setting of status fields and adding them to EEP.xml also.
# Status fields are defined as constants in EEP 2.6.4, per profile.
#
# def test_switch():
#     SWITCH = bytearray([
#         0x55,
#         0x00, 0x07, 0x07, 0x01,
#         0x7A,
#         0xF6, 0x50, 0x00, 0x29, 0x89, 0x79, 0x30,
#         0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x37, 0x00,
#         0x9D
#     ]))

#     p = RadioPacket.create(rorg=RORG.RPS, func=0x02, type=0x02, sender=[0x00, 0x29, 0x89, 0x79], CO='closed')
#     packet_serialized = p.build()
#     assert len(packet_serialized) == len(MAGNETIC_SWITCH)
#     assert list(packet_serialized) == list(MAGNETIC_SWITCH)

#     # for i in range(len(packet_serialized)):
#     #     print(i, packet_serialized[i], MAGNETIC_SWITCH[i])
