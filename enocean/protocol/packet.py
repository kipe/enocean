# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging

from enocean.protocol import crc8
from enocean.protocol.eep import EEP
from enocean.protocol.constants import PACKET, RORG, PARSE_RESULT

logger = logging.getLogger('enocean.protocol.packet')
eep = EEP()


class Packet(object):
    '''
    Base class for Packet.
    Mainly used for for packet generation and
    Packet.parse_msg(buf) for parsing message.
    parse_msg() returns subclass, if one is defined for the data type.
    '''
    def __init__(self, type, data=[], optional=[]):
        self.type = type
        self.rorg = RORG.UNDEFINED
        self.data = data
        self.optional = optional
        self.bit_data = []
        self.bit_optional = []
        self.parsed = {}

        self.parse()

    def __str__(self):
        return '0x%02X %s %s %s' % (self.type, [hex(o) for o in self.data], [hex(o) for o in self.optional], self.parsed)

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.type == other.type and self.rorg == other.rorg and self.data == other.data and self.optional == other.optional

    def _get_bit(self, byte, bit):
        ''' Get bit value from byte '''
        return (byte >> bit) & 0x01

    def _combine_hex(self, data):
        ''' Combine list of integer values to one big integer '''
        output = 0x00
        for i, d in enumerate(reversed(data)):
            output |= (d << i * 8)
        return output

    def _to_bitarray(self, data, width=8):
        ''' Convert data (list of integers, bytearray or integer) to bitarray '''
        if isinstance(data, list) or isinstance(data, bytearray):
            data = self._combine_hex(data)
        return [True if digit == '1' else False for digit in bin(data)[2:].zfill(width)]

    @staticmethod
    def parse_msg(buf):
        '''
        Parses message from buffer.
        returns:
            - PARSE_RESULT
            - remaining buffer
            - Packet -object (if message was valid, else None)
        '''
        # If the buffer doesn't contain 0x55 (start char)
        # the message isn't needed -> ignore
        if 0x55 not in buf:
            return PARSE_RESULT.INCOMPLETE, [], None

        # Valid buffer starts from 0x55
        # Convert to list, as index -method isn't defined for bytearray
        buf = buf[list(buf).index(0x55):]
        try:
            data_len = (buf[1] << 8) | buf[2]
            opt_len = buf[3]
        except IndexError:
            # If the fields don't exist, message is incomplete
            return PARSE_RESULT.INCOMPLETE, buf, None

        # Header: 6 bytes, data, optional data and data checksum
        msg_len = 6 + data_len + opt_len + 1
        if len(buf) < msg_len:
            # If buffer isn't long enough, the message is incomplete
            return PARSE_RESULT.INCOMPLETE, buf, None

        msg = buf[0:msg_len]
        buf = buf[msg_len:]

        packet_type = msg[4]
        data = msg[6:6 + data_len]
        opt_data = msg[6 + data_len:6 + data_len + opt_len]

        # Check CRCs for header and data
        if msg[5] != crc8.calc(msg[1:5]):
            # Fail if doesn't match message
            logger.error('Header CRC error!')
            # Return CRC_MISMATCH
            return PARSE_RESULT.CRC_MISMATCH, buf, None
        if msg[6 + data_len + opt_len] != crc8.calc(msg[6:6 + data_len + opt_len]):
            # Fail if doesn't match message
            logger.error('Data CRC error!')
            # Return CRC_MISMATCH
            return PARSE_RESULT.CRC_MISMATCH, buf, None

        # If we got this far, everything went ok (?)
        if packet_type == PACKET.RADIO:
            p = RadioPacket(packet_type, data, opt_data)
        elif packet_type == PACKET.RESPONSE:
            p = ResponsePacket(packet_type, data, opt_data)
        else:
            p = Packet(packet_type, data, opt_data)

        return PARSE_RESULT.OK, buf, p

    def parse(self):
        ''' Parse data from Packet '''
        return self.parsed

    def parse_eep(self, func, type):
        ''' Parse EEP based on FUNC and TYPE '''
        provides, values = eep.get_values(self.rorg, func, type, self.bit_data)
        self.parsed.update(values)
        return list(provides)

    def build(self):
        ''' Build Packet for sending to EnOcean controller '''
        data_length = len(self.data)
        ords = [0x55, (data_length >> 8) & 0xFF, data_length & 0xFF, len(self.optional), int(self.type)]
        ords.append(crc8.calc(ords[1:5]))
        ords.extend(self.data)
        ords.extend(self.optional)
        ords.append(crc8.calc(ords[6:]))
        return ords


class RadioPacket(Packet):
    destination = 0
    destination_hex = ''
    dBm = 0
    status = 0
    sender = 0
    sender_hex = ''
    learn = True
    contains_eep = False

    def __str__(self):
        packet_str = super(RadioPacket, self).__str__()
        return '%s->%s (%d dBm): %s' % (self.sender_hex, self.destination_hex, self.dBm, packet_str)

    def parse(self):
        self.destination = self._combine_hex(self.optional[1:5])
        self.destination_hex = ':'.join([('%02X' % o) for o in self.optional[1:5]])
        self.dBm = -self.optional[5]
        self.status = self.data[-1]
        self.sender = self._combine_hex(self.data[-5:-1])
        self.sender_hex = ':'.join([('%02X' % o) for o in self.data[-5:-1]])
        # Default to learn == True, as some devices don't have a learn button
        self.learn = True

        self.rorg = self.data[0]
        if self.rorg == RORG.RPS:
            self.bit_data = self._to_bitarray(self.data[1], 8)
        if self.rorg == RORG.BS1:
            self.bit_data = self._to_bitarray(self.data[1], 8)
            self.learn = not self.bit_data[-4]
        if self.rorg == RORG.BS4:
            self.bit_data = self._to_bitarray(self.data[1:5], 32)
            self.learn = not self.bit_data[-4]
            if self.learn:
                self.contains_eep = self.bit_data[-7]
        return super(RadioPacket, self).parse()


class ResponsePacket(Packet):
    response = 0
    response_data = []

    def parse(self):
        self.response = self.data[0]
        self.response_data = self.data[1:]
        return super(ResponsePacket, self).parse()


class EventPacket(Packet):
    event = 0
    event_data = []

    def parse(self):
        self.event = self.data[0]
        self.event_data = self.data[1:]
        return super(EventPacket, self).parse()
