# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from enocean.communicators import Communicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import RORG, DB6
from enocean.decorators import timing


@timing(rounds=100, limit=750)
def test_ute_in():
    communicator = Communicator()
    communicator.base_id = [0xDE, 0xAD, 0xBE, 0xEF]

    status, buf, packet = Packet.parse_msg(
        bytearray([
            0x55,
            0x00, 0x0D, 0x07, 0x01,
            0xFD,
            0xD4, 0xA0, 0xFF, 0x3E, 0x00, 0x01, 0x01, 0xD2, 0x01, 0x94, 0xE3, 0xB9, 0x00,
            0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x40, 0x00,
            0xAB
        ])
    )

    assert packet.sender_hex == '01:94:E3:B9'
    assert packet.unidirectional is False
    assert packet.bidirectional is True
    assert packet.response_expected is True
    assert packet.number_of_channels == 0xFF
    assert packet.rorg_manufacturer == 0x3E
    assert packet.rorg_of_eep == RORG.VLD
    assert packet.rorg_func == 0x01
    assert packet.rorg_type == 0x01
    assert packet.teach_in is True
    assert packet.delete is False
    assert packet.learn is True
    assert packet.contains_eep is True

    response_packet = packet.create_response_packet(communicator.base_id)
    assert response_packet.sender_hex == 'DE:AD:BE:EF'
    assert response_packet.destination_hex == '01:94:E3:B9'
    assert response_packet._bit_data[DB6.BIT_5:DB6.BIT_3] == [False, True]
    assert response_packet.data[2:7] == packet.data[2:7]
