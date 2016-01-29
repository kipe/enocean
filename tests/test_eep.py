# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division

from enocean.protocol.packet import Packet
from enocean.protocol.constants import RORG


def test_temperature():
    ''' Tests RADIO message for EEP -profile 0xA5 0x02 0x05 '''
    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ]))
    assert p.parse_eep(0x02, 0x05) == ['TMP']
    assert round(p.parsed['TMP']['value'], 1) == 26.7
    assert p.parsed['TMP']['raw_value'] == 85
    assert p.learn is False
    assert p.contains_eep is False
    assert p.rorg is 0xA5
    assert p.rorg is int(RORG.BS4)
    assert p.rorg_func is 0x02
    assert p.rorg_type is 0x05
    assert p.status == 0x00
    assert p.repeater_count == 0


def test_magnetic_switch():
    ''' Tests RADIO message for EEP -profile 0xD5 0x00 0x01 '''
    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x08, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00,
        0x53
    ]))
    assert p.parse_eep(0x00, 0x01) == ['CO']
    assert p.parsed['CO']['value'] == 'open'
    assert p.parsed['CO']['raw_value'] == 0
    assert p.status == 0x00
    assert p.repeater_count == 0

    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x09, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00,
        0xC7
    ]))
    assert p.parse_eep(0x00, 0x01) == ['CO']
    assert p.parsed['CO']['value'] == 'closed'
    assert p.parsed['CO']['raw_value'] == 1
    assert p.learn is False
    assert p.status == 0x00
    assert p.repeater_count == 0


def test_switch():
    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x50, 0x00, 0x29, 0x89, 0x79, 0x30,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x37, 0x00,
        0x9D
    ]))
    assert sorted(p.parse_eep(0x02, 0x02)) == ['EBO', 'NU', 'R1', 'R2', 'SA', 'T21']
    assert p.parsed['SA']['value'] == 'No 2nd action'
    assert p.parsed['EBO']['value'] == 'pressed'
    assert p.parsed['R1']['value'] == 'Button BI'
    assert p.parsed['T21']['value'] is True
    assert p.parsed['NU']['value'] is True
    assert p.learn is True
    assert p.status == 0x30
    assert p.repeater_count == 0

    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x00, 0x00, 0x29, 0x89, 0x79, 0x20,
        0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0x4A, 0x00,
        0x03
    ]))
    assert sorted(p.parse_eep(0x02, 0x02)) == ['EBO', 'NU', 'R1', 'R2', 'SA', 'T21']
    assert p.parsed['SA']['value'] == 'No 2nd action'
    assert p.parsed['EBO']['value'] == 'released'
    assert p.parsed['T21']['value'] is True
    assert p.parsed['NU']['value'] is False
    assert p.learn is True
    assert p.status == 0x20
    assert p.repeater_count == 0


def test_eep_parsing():
    status, buf, p = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x08, 0x28, 0x46, 0x80, 0x01, 0x8A, 0x7B, 0x30, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x49, 0x00,
        0x26
    ]))
    assert p.learn is True
    assert p.contains_eep is True
    assert p.rorg_func == 0x02
    assert p.rorg_type == 0x05
    assert p.status == 0x00
    assert p.repeater_count == 0
