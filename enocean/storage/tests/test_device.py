# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from enocean.storage import Device


def test_device_creation():
    device = Device(
        [0xDE, 0xAD, 0xBE, 0xEF],
        eep_rorg=0xA5,
        eep_func=0x01,
        eep_type=0x01
    )
    assert device.id == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.eep_rorg == 0xA5
    assert device.eep_func == 0x01
    assert device.eep_type == 0x01

    device = Device(
        id='DE:AD:BE:EF',
        eep_rorg=0xA5,
        eep_func=0x01,
        eep_type=0x01
    )
    assert device.id == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.eep_rorg == 0xA5
    assert device.eep_func == 0x01
    assert device.eep_type == 0x01
    assert device.__repr__() == device.__str__() == str(device) == device.__unicode__() == '<Device DE:AD:BE:EF A5-01-01>'


def test_device_modifying():
    device = Device([0xDE, 0xAD, 0xBE, 0xEF])
    assert device.id == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.eep_rorg is None
    assert device.eep_func is None
    assert device.eep_type is None
    assert device.as_dict() == {'eep_type': None, 'eep_rorg': None, 'eep_func': None, 'transmitter_offset': None, 'id': [222, 173, 190, 239], 'manufacturer_id': None}

    device.eep_rorg = 0xA5
    device.eep_func = 0x01
    device.eep_type = 0x01
    assert device.eep_rorg == 0xA5
    assert device.eep_func == 0x01
    assert device.eep_type == 0x01
    assert device.as_dict() == {'eep_type': 1, 'eep_rorg': 165, 'eep_func': 1, 'transmitter_offset': None, 'id': [222, 173, 190, 239], 'manufacturer_id': None}

    device.name = 'test'
    assert device.name == 'test'

    assert device.as_dict() == {'eep_type': 1, 'eep_rorg': 165, 'eep_func': 1, 'transmitter_offset': None, 'id': [222, 173, 190, 239], 'name': 'test', 'manufacturer_id': None}


def test_device___value_from_hex():
    device = Device([0xDE, 0xAD, 0xBE, 0xEF])
    assert device._Device__value_from_hex(None) is None
    assert device._Device__value_from_hex(255) == 255
    assert device._Device__value_from_hex('0xFF') == 255
    assert device._Device__value_from_hex('asd') == 'asd'
