# -*- encoding: utf-8 -*-
from typing import Union


def get_bit(byte: int, bit: int) -> int:
    """ Get bit value from byte """
    return (byte >> bit) & 0x01


def combine_hex(data: Union[list, bytearray]) -> int:
    """ Combine list of integer values to one big integer """
    output = 0x00
    for i, value in enumerate(reversed(data)):
        output |= (value << i * 8)
    return output


def to_bitarray(data: Union[list, bytearray], width=8) -> list[bool]:
    """ Convert data (list of integers, bytearray or integer) to bitarray """
    if isinstance(data, list) or isinstance(data, bytearray):
        data = combine_hex(data)
    return [True if digit == '1' else False for digit in bin(data)[2:].zfill(width)]


def from_bitarray(data: list[bool]) -> int:
    """ Convert bit array back to integer """
    return int(''.join(['1' if x else '0' for x in data]), 2)


def to_hex_string(data: Union[list, int]) -> str:
    """ Convert list of integers to a hex string, separated by ":" """
    if isinstance(data, int):
        return f'{data:02X}'
    return ':'.join([f'{o:02X}' for o in data])


def from_hex_string(hex_string: str) -> Union[int, list]:
    reval = [int(x, 16) for x in hex_string.split(':')]
    if len(reval) == 1:
        return reval[0]
    return reval
