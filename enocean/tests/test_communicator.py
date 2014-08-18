# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from ..communicators.communicator import Communicator
from ..protocol.packet import Packet
from ..protocol.constants import PACKET


def test_buffer():
    ''' Test buffer parsing for Communicator '''
    data = [
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ]
    c = Communicator()
    c._buffer.extend(data[0:5])
    c.parse()
    assert c.receive.qsize() == 0
    c._buffer.extend(data[5:])
    c.parse()
    assert c.receive.qsize() == 1


def test_send():
    ''' Test sending packets to Communicator '''
    c = Communicator()
    assert c.send('AJSNDJASNDJANSD') is False
    assert c.transmit.qsize() == 0
    assert c._get_from_send_queue() is None
    assert c.send(Packet(PACKET.COMMON_COMMAND, [0x08])) is True
    assert c.transmit.qsize() == 1
    assert isinstance(c._get_from_send_queue(), Packet)
