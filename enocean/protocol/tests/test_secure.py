# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from nose.tools import assert_raises

from enocean.protocol.secure import SecureStore, SecureDevice
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PARSE_RESULT, PACKET, RORG
from enocean.decorators import timing


@timing(1000)
def test_secure_teach_in():
    ''' Tests Secure Teach-In, verify and decrypt '''
    # Secure Teach-In telegrams (part 1)
    msg1 = bytearray([
        0x55,
        0x00, 0x0F, 0x07, 0x01,
        0x2B,
        0x35, 0x24, 0x4b,  0xC0, 0xFF, 0x45, 0x6E, 0x4F, 0x63, 0x65,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
        0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
        0x71
    ])

    # Secure Teach-In telegrams (part 2)
    msg2 = bytearray([
        0x55,
        0x00, 0x12, 0x07, 0x01,
        0x18,
        0x35, 0x40, 0x61, 0x6E, 0x20, 0x47, 0x6D, 0x62, 0x48, 0x2E, 0x31, 0x33, 0x00,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
        0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
        0xF0
    ])

    # Secure telegram (PTM215 A0 pressed)
    msg3 = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0x30, 0xD0, 0xB5, 0x18, 0xFB,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
        0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
        0x4D
    ])

    # Secure telegram (PTM215 A0 released)
    msg4 = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0x30, 0x7B, 0xAE, 0xC8, 0x28,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
        0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
        0x94
    ])

    secure_devices = SecureStore()
    assert secure_devices.is_teach_in_allowed() == False

    # Teach in not allowed
    _status, _buf, packet1 = Packet.parse_msg(msg1)
    assert secure_devices.teach_in(packet1) == None
    _status, _buf, packet2 = Packet.parse_msg(msg2)
    assert secure_devices.teach_in(packet2) == None

    # Not paired
    _status, _buf, packet3 = Packet.parse_msg(msg3)
    with assert_raises(ValueError):
        secure_devices.decrypt(packet3)

    with assert_raises(ValueError):
        SecureDevice([packet1])
    with assert_raises(ValueError):
        SecureDevice([packet2, packet1])
    with assert_raises(ValueError):
        SecureDevice([packet1, packet3])

    secure_devices.allow_teach_in(min_dBm=-80)
    assert secure_devices.is_teach_in_allowed() == True

    # Teach in allowed
    _status, _buf, packet = Packet.parse_msg(msg1)
    assert packet.rorg == RORG.SEC_TI
    assert secure_devices.teach_in(packet) == None

    with assert_raises(ValueError):
        secure_devices.decrypt(packet1)

    _status, _buf, packet = Packet.parse_msg(msg2)
    assert packet.rorg == RORG.SEC_TI
    dev = secure_devices.teach_in(packet)
    assert dev.sender == [0x01, 0x9E, 0xB6, 0x3B]
    assert dev.psk == 0
    assert dev.ptm == 1
    assert dev.rlc_algo == 2
    assert dev.rlc_tx == 0
    assert dev.mac_algo == 1
    assert dev.data_enc == 3
    assert dev.rlc == 0xC0FF
    assert dev.key == bytearray([0x45, 0x6E, 0x4F, 0x63, 0x65, 0x61, 0x6E, 0x20,
                                 0x47, 0x6D, 0x62, 0x48, 0x2E, 0x31, 0x33, 0x00])
    assert dev.rlc_len == 2
    assert dev.explicit_rlc_len == 0
    assert dev.mac_len == 3

    # AO pressed
    _status, _buf, packet = Packet.parse_msg(msg3)
    assert packet.rorg == RORG.SEC
    dev = secure_devices.decrypt(packet)
    assert packet.rorg == RORG.SECD
    # translate RORG.SECD of PTM215 to VLD (D2-03-00)
    dev.translate_application(packet)
    assert packet.rorg == RORG.VLD
    assert packet.data[1] == 0x0E  # AO pressed
    # translate profile D2-03-00 (payload 4 bits) to RPS (F6-02-01)
    dev.translate_profile(packet)
    assert packet.rorg == RORG.RPS

    # replay protection
    _status, _buf, packet = Packet.parse_msg(msg3)
    with assert_raises(ValueError):
        secure_devices.decrypt(packet)

    # Remove and re-add in store
    secure_devices.remove_device(dev)
    _status, _buf, packet = Packet.parse_msg(msg4)
    with assert_raises(ValueError):
        secure_devices.decrypt(packet)
    with assert_raises(KeyError):
        secure_devices.remove_device(dev)
    secure_devices.add_device(dev)

    # AO released
    _status, _buf, packet = Packet.parse_msg(msg4)
    assert packet.rorg == RORG.SEC
    dev = secure_devices.decrypt(packet)
    assert packet.rorg == RORG.SECD
    # translate RORG.SECD of PTM215 to VLD (D2-03-00)
    dev.translate_application(packet)
    assert packet.rorg == RORG.VLD
    assert packet.data[1] == 0x0F  # released
    # translate profile D2-03-00 (payload 4 bits) to RPS (F6-02-01)
    dev.translate_profile(packet)
    assert packet.rorg == RORG.RPS
