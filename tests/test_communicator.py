# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division

from enocean.communicators.communicator import Communicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET
from .decorators import timing


@timing(1000)
def test_buffer():
    ''' Test buffer parsing for Communicator '''
    data = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ])
    com = Communicator()
    com._buffer.extend(data[0:5])
    com.parse()
    assert com.receive.qsize() == 0
    com._buffer.extend(data[5:])
    com.parse()
    assert com.receive.qsize() == 1


@timing(1000)
def test_send():
    ''' Test sending packets to Communicator '''
    com = Communicator()
    assert com.send('AJSNDJASNDJANSD') is False
    assert com.transmit.qsize() == 0
    assert com._get_from_send_queue() is None
    assert com.send(Packet(PACKET.COMMON_COMMAND, [0x08])) is True
    assert com.transmit.qsize() == 1
    assert isinstance(com._get_from_send_queue(), Packet)
