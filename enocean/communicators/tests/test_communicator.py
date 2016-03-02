# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from enocean.communicators.communicator import Communicator
from enocean.protocol.packet import Packet, RadioPacket
from enocean.protocol.constants import PACKET, RORG
from enocean.tests.decorators import timing


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
    com = Communicator()
    assert com.send('AJSNDJASNDJANSD') is False
    assert com.transmit.qsize() == 0
    assert com._get_from_send_queue() is None
    assert com.send(Packet(PACKET.COMMON_COMMAND, [0x08])) is True
    assert com.transmit.qsize() == 1
    assert isinstance(com._get_from_send_queue(), Packet)


def test_stop():
    com = Communicator()
    com.stop()
    assert com._stop_flag.is_set()


def test_callback():
    def callback(packet):
        assert isinstance(packet, RadioPacket)

    data = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ])

    com = Communicator(callback=callback)
    com._buffer.extend(data)
    com.parse()
    assert com.receive.qsize() == 0


def test_base_id():
    com = Communicator()
    assert com.base_id is None

    other_data = bytearray([
        0x55,
        0x00, 0x0A, 0x07, 0x01,
        0xEB,
        0xA5, 0x00, 0x00, 0x55, 0x08, 0x01, 0x81, 0xB7, 0x44, 0x00,
        0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x2D, 0x00,
        0x75
    ])

    response_data = bytearray([
        0x55,
        0x00, 0x05, 0x00, 0x02,
        0xCE,
        0x00, 0xFF, 0x87, 0xCA, 0x00,
        0xA3
    ])

    com._buffer.extend(other_data)
    com._buffer.extend(response_data)
    com.parse()
    assert com.base_id == [0xFF, 0x87, 0xCA, 0x00]
    assert com.receive.qsize() == 2


def test_fails():
    com = Communicator()
    try:
        com._receive()
        assert False
    except NotImplementedError:
        assert True

    try:
        com._transmit(RadioPacket.create(rorg=RORG.BS1, rorg_func=0x00, rorg_type=0x01, sender=[0x01, 0x82, 0x5D, 0xAB], CO='closed'))
        assert False
    except NotImplementedError:
        assert True


def test_thread():
    com = Communicator()
    assert com.get_packet() is None
    # Stupid mock to get around Communicator._receive and Communicator._transmit raising an error.
    com._receive = lambda: ''
    com._transmit = lambda packet: ''

    com.start()
    com.base_id
    com.stop()
