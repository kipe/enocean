# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import


def get_bit(byte, bit):
    ''' Get bit value from byte '''
    return (byte >> bit) & 0x01


def combine_hex(data):
    ''' Combine list of integer values to one big integer '''
    output = 0x00
    for i, value in enumerate(reversed(data)):
        output |= (value << i * 8)
    return output


def to_bitarray(data, width=8):
    ''' Convert data (list of integers, bytearray or integer) to bitarray '''
    if isinstance(data, list) or isinstance(data, bytearray):
        data = combine_hex(data)
    return [True if digit == '1' else False for digit in bin(data)[2:].zfill(width)]


def from_bitarray(data):
    ''' Convert bit array back to integer '''
    return int(''.join(['1' if x else '0' for x in data]), 2)


def to_hex_string(data):
    ''' Convert list of integers to a hex string, separated by ":" '''
    if isinstance(data, int):
        return '%02X' % data
    return ':'.join([('%02X' % o) for o in data])


def from_hex_string(hex_string):
    reval = [int(x, 16) for x in hex_string.split(':')]
    if len(reval) == 1:
        return reval[0]
    return reval
