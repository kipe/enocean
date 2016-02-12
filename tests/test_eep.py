# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division

from enocean.protocol.packet import Packet
from enocean.protocol.constants import RORG


def test_temperature():
    ''' Tests RADIO message for EEP -profile 0xA5 0x02 0x05 '''
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ]))
    assert pack.parse_eep(0x02, 0x05) == ['TMP']
    assert round(pack.parsed['TMP']['value'], 1) == 26.7
    assert pack.parsed['TMP']['raw_value'] == 85
    assert pack.learn is False
    assert pack.contains_eep is False
    assert pack.rorg is 0xA5
    assert pack.rorg is int(RORG.BS4)
    assert pack.rorg_func is 0x02
    assert pack.rorg_type is 0x05
    assert pack.status == 0x00
    assert pack.repeater_count == 0
    assert pack.sender == [0x01, 0x81, 0xB7, 0x44]
    assert pack.sender_hex == '01:81:B7:44'


def test_magnetic_switch():
    ''' Tests RADIO message for EEP -profile 0xD5 0x00 0x01 '''
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x08, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00,
        0x53
    ]))
    assert pack.parse_eep(0x00, 0x01) == ['CO']
    assert pack.parsed['CO']['value'] == 'open'
    assert pack.parsed['CO']['raw_value'] == 0
    assert pack.status == 0x00
    assert pack.repeater_count == 0

    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x09, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00,
        0xC7
    ]))
    assert pack.parse_eep(0x00, 0x01) == ['CO']
    assert pack.parsed['CO']['value'] == 'closed'
    assert pack.parsed['CO']['raw_value'] == 1
    assert pack.learn is False
    assert pack.status == 0x00
    assert pack.repeater_count == 0


def test_switch():
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x50, 0x00, 0x29, 0x89, 0x79, 0x30,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x37, 0x00,
        0x9D
    ]))
    assert sorted(pack.parse_eep(0x02, 0x02)) == ['EBO', 'NU', 'R1', 'R2', 'SA', 'T21']
    assert pack.parsed['SA']['value'] == 'No 2nd action'
    assert pack.parsed['EBO']['value'] == 'pressed'
    assert pack.parsed['R1']['value'] == 'Button BI'
    assert pack.parsed['T21']['value'] is True
    assert pack.parsed['NU']['value'] is True
    assert pack.learn is True
    assert pack.status == 0x30
    assert pack.repeater_count == 0

    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xF6, 0x00, 0x00, 0x29, 0x89, 0x79, 0x20,
        0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0x4A, 0x00,
        0x03
    ]))
    assert sorted(pack.parse_eep(0x02, 0x02)) == ['EBO', 'NU', 'R1', 'R2', 'SA', 'T21']
    assert pack.parsed['SA']['value'] == 'No 2nd action'
    assert pack.parsed['EBO']['value'] == 'released'
    assert pack.parsed['T21']['value'] is True
    assert pack.parsed['NU']['value'] is False
    assert pack.learn is True
    assert pack.status == 0x20
    assert pack.repeater_count == 0


def test_eep_parsing():
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x08, 0x28, 0x46, 0x80, 0x01, 0x8A, 0x7B, 0x30, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x49, 0x00,
        0x26
    ]))
    assert pack.learn is True
    assert pack.contains_eep is True
    assert pack.rorg_func == 0x02
    assert pack.rorg_type == 0x05
    assert pack.status == 0x00
    assert pack.repeater_count == 0


def test_eep_remaining():
    # Magnetic switch -example
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x07, 0x07, 0x01,
        0x7A,
        0xD5, 0x08, 0x01, 0x82, 0x5D, 0xAB, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x36, 0x00,
        0x53
    ]))
    assert pack.parse_eep(0x00, 0x01) == ['CO']

    # Temperature-example
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ]))
    # If this fails, the data is retained from the last Packet parsing!
    assert pack.parse_eep(0x00, 0x01) == []
    # Once we have parse with the correct func and type, this should pass.
    assert pack.parse_eep(0x02, 0x05) == ['TMP']


def test_eep_direction():
    status, buf, pack = Packet.parse_msg(bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x32, 0x20, 0x89, 0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x00,
        0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
        0x43
    ]))
    assert sorted(pack.parse_eep(0x20, 0x01, 1)) == ['ACO', 'BCAP', 'CCO', 'CV', 'DWO', 'ENIE', 'ES', 'FTS', 'SO', 'TMP']
    assert pack.parsed['CV']['value'] == 50
    assert sorted(pack.parse_eep(0x20, 0x01, 2)) == ['LFS', 'RCU', 'RIN', 'SB', 'SP', 'SPI', 'SPS', 'TMP', 'VC', 'VO']
    assert pack.parsed['SP']['value'] == 50
