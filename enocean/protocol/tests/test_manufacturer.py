# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from enocean.protocol.packet import Packet
from enocean.protocol.eep import EEP
from enocean.protocol.constants import RORG
from enocean.decorators import timing


@timing(1000)
def test_eltako_shutter_state():
    ''' Tests RADIO message for EEP -profile manufacturer '''
    status, buf, packet = Packet.parse_msg(EEP(), bytearray([
        0x55,
        0x00, 0x0a, 0x07, 0x01,
        0xeb,
        0xa5, 0x07, 0xc6, 0x02, 0x0a, 0x04, 0x21, 0x96, 0x60, 0x00,
        0x00, 0xff,0xff, 0xff, 0xff, 0x4f, 0x00,
        0x8e
    ]))

    assert packet.parse_eep(0x00, 0x02, manufacturer=0x00d) == ['TRA', 'DIR', 'LCK']
    assert round(packet.parsed['TRA']['value'], 1) == 199.0
    assert packet.parsed['TRA']['raw_value'] == 1990
    assert packet.parsed['DIR']['value'] == 'Down'
    assert packet.parsed['LCK']['value'] == 'Unlock'
    assert packet.learn is False
    assert packet.contains_eep is False
    assert packet.rorg == 0xA5
    assert packet.rorg == int(RORG.BS4)
    assert packet.rorg_func == 0x00
    assert packet.rorg_type == 0x02
    assert packet.status == 0x00
    assert packet.repeater_count == 0
    assert packet.sender == [0x04, 0x21, 0x96, 0x60]
    assert packet.sender_hex == '04:21:96:60'

@timing(1000)
def test_standard_environ():
    ''' Tests RADIO message for EEP -profile manufacturer '''
    status, buf, packet = Packet.parse_msg(EEP(), bytearray([

        0x55,
        0x00, 0x0a, 0x07, 0x01,
        0xeb,
        0xa5, 0xff, 0x8a, 0x0a, 0x18, 0x05, 0xa0, 0x8b, 0xd6, 0x00,
        0x00, 0xff,0xff, 0xff, 0xff, 0x47, 0x00,
        0x00                                               
    ]))

    assert packet.parse_eep(0x13, 0x01) == ['DWS', 'TMP', 'WND', 'D/N', 'RAN']
    assert round(packet.parsed['DWS']['value'], 1) == 999.0
    assert packet.parsed['DWS']['raw_value'] == 255
    assert packet.parsed['TMP']['raw_value'] == 138
    assert round(packet.parsed['TMP']['value'],1) == 24.9
    assert packet.parsed['WND']['raw_value'] == 10
    assert round(packet.parsed['WND']['value'],1) == 2.7
    assert packet.parsed['D/N']['raw_value'] == 0
    assert packet.parsed['RAN']['raw_value'] == 0
    assert packet.learn is False
    assert packet.contains_eep is False
    assert packet.rorg == 0xA5
    assert packet.rorg == int(RORG.BS4)
    assert packet.rorg_func == 0x13
    assert packet.rorg_type == 0x01
    assert packet.status == 0x00
    assert packet.repeater_count == 0
    assert packet.sender == [0x05, 0xa0, 0x8b, 0xd6]
    assert packet.sender_hex == '05:A0:8B:D6'


@timing(1000)
def test_eltako_environ():
    ''' Tests RADIO message for EEP -profile manufacturer '''
    status, buf, packet = Packet.parse_msg(EEP(), bytearray([

        0x55,
        0x00, 0x0a, 0x07, 0x01,
        0xeb,
        0xa5, 0xff, 0x8a, 0x0a, 0x18, 0x05, 0xa0, 0x8b, 0xd6, 0x00,
        0x00, 0xff,0xff, 0xff, 0xff, 0x47, 0x00,
        0x00                                               
    ]))

    assert packet.parse_eep(0x13, 0x01, manufacturer=0x00d) == ['DWS', 'TMP', 'WND', 'RAN']
    assert round(packet.parsed['DWS']['value'], 1) == 999.0
    assert packet.parsed['DWS']['raw_value'] == 255
    assert packet.parsed['TMP']['raw_value'] == 138
    assert round(packet.parsed['TMP']['value'],1) == 24.9
    assert packet.parsed['WND']['raw_value'] == 10
    assert round(packet.parsed['WND']['value'],1) == 2.7
    assert packet.parsed['RAN']['raw_value'] == 0
    assert packet.learn is False
    assert packet.contains_eep is False
    assert packet.rorg == 0xA5
    assert packet.rorg == int(RORG.BS4)
    assert packet.rorg_func == 0x13
    assert packet.rorg_type == 0x01
    assert packet.status == 0x00
    assert packet.repeater_count == 0
    assert packet.sender == [0x05, 0xa0, 0x8b, 0xd6]
    assert packet.sender_hex == '05:A0:8B:D6'
