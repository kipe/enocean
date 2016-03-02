# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import enocean.utils


def test_get_bit():
    assert enocean.utils.get_bit(1, 0) == 1
    assert enocean.utils.get_bit(8, 3) == 1
    assert enocean.utils.get_bit(6, 2) == 1
    assert enocean.utils.get_bit(6, 1) == 1


def test_to_hex_string():
    assert enocean.utils.to_hex_string(0) == '00'
    assert enocean.utils.to_hex_string(15) == '0F'
    assert enocean.utils.to_hex_string(16) == '10'
    assert enocean.utils.to_hex_string(22) == '16'

    assert enocean.utils.to_hex_string([0, 15, 16, 22]) == '00:0F:10:16'
    assert enocean.utils.to_hex_string([0x00, 0x0F, 0x10, 0x16]) == '00:0F:10:16'


def test_from_hex_string():
    assert enocean.utils.from_hex_string('00') == 0
    assert enocean.utils.from_hex_string('0F') == 15
    assert enocean.utils.from_hex_string('10') == 16
    assert enocean.utils.from_hex_string('16') == 22

    assert enocean.utils.from_hex_string('00:0F:10:16') == [0, 15, 16, 22]
    assert enocean.utils.from_hex_string('00:0F:10:16') == [0x00, 0x0F, 0x10, 0x16]
