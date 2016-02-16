# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from nose.tools import raises

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
    PACKET_CONTENT_4 = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x32, 0x00, 0x00, 0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x80
    ])

    # manually assemble packet
    pack = Packet(PACKET.RADIO)
    pack.rorg = RORG.BS4
    sender_bytes = [(0xdeadbeef >> i & 0xff) for i in (24, 16, 8, 0)]
    data = [0, 0, 0, 0]
    pack.data = [pack.rorg] + data + sender_bytes + [0]

    # test content
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_1)
    assert list(packet_serialized) == list(PACKET_CONTENT_1)

    # set optional data
    sub_tel_num = 3
    destination = [255, 255, 255, 255]    # broadcast
    dbm = 0xff
    security = 0
    pack.optional = [sub_tel_num] + destination + [dbm] + [security]

    # test content
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_2)
    assert list(packet_serialized) == list(PACKET_CONTENT_2)

    # update data based on EEP
    pack.select_eep(0x20, 0x01, 1)
    prop = {
        'CV': 50,
        'TMP': 21.5,
        'ES': 'true',
    }
    pack.set_eep(prop)

    # test content
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_3)
    assert list(packet_serialized) == list(PACKET_CONTENT_3)
    assert pack.rorg_func == 0x20
    assert pack.rorg_type == 0x01

    # Test the easier method of sending packets.
    pack = Packet.create(PACKET.RADIO, rorg=RORG.BS4, func=0x20, learn=True, type=0x01, direction=1, **prop)
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_3)
    assert list(packet_serialized) == list(PACKET_CONTENT_3)
    assert pack.rorg_func == 0x20
    assert pack.rorg_type == 0x01

    # Test creating RadioPacket directly.
    pack = RadioPacket.create(rorg=RORG.BS4, func=0x20, learn=True, type=0x01, direction=2, SP=50)
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(PACKET_CONTENT_4)
    assert list(packet_serialized) == list(PACKET_CONTENT_4)
    assert pack.rorg_func == 0x20
    assert pack.rorg_type == 0x01


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
    pack = RadioPacket.create(rorg=RORG.BS4, func=0x02, type=0x05, sender=[0x01, 0x81, 0xB7, 0x44], TMP=26.66666666666666666666666666666666666666666667)
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(TEMPERATURE)
    assert list(packet_serialized) == list(TEMPERATURE)
    assert pack.learn is False

    TEMPERATURE = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x00, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0xE0
    ])
    pack = RadioPacket.create(rorg=RORG.BS4, func=0x02, type=0x05, sender=[0x01, 0x81, 0xB7, 0x44], learn=True, TMP=26.66666666666666666666666666666666666666666667)
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(TEMPERATURE)
    assert pack.learn is True


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
    pack = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], CO='open')
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)
    assert pack.learn is False

    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x00, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x06
    ])
    pack = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], learn=True, CO='open')
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)
    assert pack.learn is True

    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x09, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x2E
    ])

    pack = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], CO='closed')
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)
    assert pack.learn is False

    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x01, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x92
    ])

    pack = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], learn=True, CO='closed')
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)
    assert pack.learn is True


def test_switch():
    SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x50, 0x00, 0x29, 0x89, 0x79, 0x30,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x61
    ])

    # test also enum setting by integer value with EB0
    pack = RadioPacket.create(rorg=RORG.RPS, func=0x02, type=0x02, sender=[0x00, 0x29, 0x89, 0x79],
                           SA='No 2nd action',
                           EBO=1,
                           R1='Button BI',
                           T21=True,
                           NU=True,
                           )
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(SWITCH)
    assert list(packet_serialized) == list(SWITCH)

    SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x00, 0x00, 0x29, 0x89, 0x79, 0x20,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0xD2
    ])

    pack = RadioPacket.create(rorg=RORG.RPS, func=0x02, type=0x02, sender=[0x00, 0x29, 0x89, 0x79],
                           SA='No 2nd action',
                           EBO='released',
                           T21=True,
                           NU=False,
                           )
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(SWITCH)
    assert list(packet_serialized) == list(SWITCH)


@raises(ValueError)
def test_illegal_eep_enum1():
    RadioPacket.create(rorg=RORG.RPS, func=0x02, type=0x02, sender=[0x00, 0x29, 0x89, 0x79], EBO='inexisting')


@raises(ValueError)
def test_illegal_eep_enum2():
    RadioPacket.create(rorg=RORG.RPS, func=0x02, type=0x02, sender=[0x00, 0x29, 0x89, 0x79], EBO=2)


# Corresponds to the tests done in test_eep
def test_packets_with_destination():
    TEMPERATURE = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x03, 0xDE, 0xAD, 0xBE, 0xEF, 0xFF, 0x00,
        0x5F
    ])
    pack = RadioPacket.create(rorg=RORG.BS4, func=0x02, type=0x05, sender=[0x01, 0x81, 0xB7, 0x44], destination=[0xDE, 0xAD, 0xBE, 0xEF], TMP=26.66666666666666666666666666666666666666666667)
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(TEMPERATURE)
    assert list(packet_serialized) == list(TEMPERATURE)
    assert pack.learn is False

    MAGNETIC_SWITCH = bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x08, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x03, 0xDE, 0xAD, 0xBE, 0xEF, 0xFF, 0x00,
        0xB9
    ])
    pack = RadioPacket.create(rorg=RORG.BS1, func=0x00, type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], destination=[0xDE, 0xAD, 0xBE, 0xEF], CO='open')
    packet_serialized = pack.build()
    assert len(packet_serialized) == len(MAGNETIC_SWITCH)
    assert list(packet_serialized) == list(MAGNETIC_SWITCH)
    assert pack.learn is False
