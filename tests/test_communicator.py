# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from enocean.communicators.communicator import Communicator
from enocean.protocol.packet import Packet, RadioPacket
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
    communicator = Communicator()
    communicator._buffer.extend(data[0:5])
    communicator.parse()
    assert communicator.receive.qsize() == 0
    communicator._buffer.extend(data[5:])
    communicator.parse()
    assert communicator.receive.qsize() == 1
    assert isinstance(communicator.get_packet(), RadioPacket)


@timing(1000)
def test_send():
    ''' Test sending packets to Communicator '''
    communicator = Communicator()
    assert communicator.send('AJSNDJASNDJANSD') is False
    assert communicator.transmit.qsize() == 0
    assert communicator._get_from_send_queue() is None
    assert communicator.send(Packet(PACKET.COMMON_COMMAND, [0x08])) is True
    assert communicator.transmit.qsize() == 1
    assert isinstance(communicator._get_from_send_queue(), Packet)


def test_send_priority():
    ''' Test priorities when sending packages. '''
    communicator = Communicator()
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x04]), priority=4)
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x05]), priority=5)
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x02]), priority=2)
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x00]), priority=0)
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x01]), priority=1)
    communicator.send(Packet(PACKET.COMMON_COMMAND, [0x03]), priority=3)

    for i in range(6):
        priority, packet = communicator.transmit.get()
        assert priority == i
        assert packet.data == [i]
