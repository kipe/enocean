# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging

from enocean.protocol import crc8
from enocean.protocol.eep import EEP
from enocean.protocol.constants import PACKET, RORG, PARSE_RESULT, DB0, DB2, DB3

logger = logging.getLogger('enocean.protocol.packet')


class Packet(object):
    '''
    Base class for Packet.
    Mainly used for for packet generation and
    Packet.parse_msg(buf) for parsing message.
    parse_msg() returns subclass, if one is defined for the data type.
    '''
    eep = EEP()

    def __init__(self, type, data=[], optional=[]):
        self.type = type
        self.rorg = RORG.UNDEFINED
        self.rorg_func = None
        self.rorg_type = None
        self.rorg_manufacturer = None
        self.data = data
        self.optional = optional
        self.status = 0
        self.bit_data = []
        self.bit_optional = []
        self.bit_status = []
        self.parsed = {}
        self.repeater_count = 0

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

    def _from_bitarray(self, data):
        ''' Convert bit array back to integer '''
        return int(''.join(['1' if x else '0' for x in data]), 2)

    def _to_hex_string(self, data):
        ''' Convert list of integers to a hex string, separated by ":" '''
        return ':'.join([('%02X' % o) for o in data])

    def _data_to_bitdata(self):
        ''' Updates the bit_data member based on data member.'''
        if self.rorg == RORG.RPS or self.rorg == RORG.BS1:
            self.bit_data = self._to_bitarray(self.data[1], 8)
        if self.rorg == RORG.BS4:
            self.bit_data = self._to_bitarray(self.data[1:5], 32)

    def _bitdata_to_data(self):
        ''' Updates the data member based on bit_data member.'''
        if self.rorg in [RORG.RPS, RORG.BS1]:
            self.data[1] = self._from_bitarray(self.bit_data)
        if self.rorg == RORG.BS4:
            for byte in range(4):
                self.data[byte+1] = self._from_bitarray(self.bit_data[byte*8:(byte+1)*8])

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

    @staticmethod
    def create(packet_type, rorg, func, type, direction=None,
               destination=[0xFF, 0xFF, 0xFF, 0xFF],
               sender=[0xDE, 0xAD, 0xBE, 0xEF],
               learn=False, **kwargs):
        '''
        Creates an packet ready for sending.
        Uses rorg, func and type to determine the values set based on EEP.
        Additional arguments (**kwargs) are used for setting the values.

        Currently only supports:
            - PACKET.RADIO
            - RORGs RPS, BS1, and BS4.

        TODO:
            - Require sender to be set? Would force the "correct" sender to be set.
            - Do we need to set telegram control bits?
              Might be useful for acting as a repeater?
        '''

        if packet_type != PACKET.RADIO:
            # At least for now, only support PACKET.RADIO.
            raise ValueError('Packet type not supported by this function.')

        if rorg not in [RORG.RPS, RORG.BS1, RORG.BS4]:
            # At least for now, only support these RORGS.
            raise ValueError('RORG not supported by this function.')

        if not isinstance(destination, list) or len(destination) != 4:
            raise ValueError('Destination must a list containing 4 (numeric) values.')

        if not isinstance(sender, list) or len(sender) != 4:
            raise ValueError('Sender must a list containing 4 (numeric) values.')

        p = Packet(packet_type)
        p.rorg = rorg
        p.data = [p.rorg]
        # Initialize data depending on the profile.
        p.data.extend([0] * 4 if rorg == RORG.BS4 else [0])
        p.data.extend(sender)
        # Always use sub-telegram 3, maximum dbm (as per spec, when sending),
        # and no security (security not supported as per EnOcean Serial Protocol).
        p.optional = [3] + destination + [0xFF] + [0]

        p.select_eep(func, type, direction)
        p.set_eep(kwargs)
        if rorg in [RORG.BS1, RORG.BS4] and not learn:
            if rorg == RORG.BS1:
                p.data[1] |= (1 << 3)
            if rorg == RORG.BS4:
                p.data[4] |= (1 << 3)
        p.data.append(p.status)

        # Parse the built package, so it corresponds to the received packages
        # For example, stuff like checking RadioPacket.learn should be set.
        p = Packet.parse_msg(p.build())[2]
        p.rorg = rorg
        p.parse_eep(func, type, direction)
        return p

    def parse(self):
        ''' Parse data from Packet '''
        # Parse status from messages
        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            self.status = self.data[-1]
        if self.rorg == RORG.VLD:
            self.status = self.optional[-1]
        self.bit_status = self._to_bitarray(self.status)

        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            # These message types should have repeater count in the last for bits of status.
            self.repeater_count = self._from_bitarray(self.bit_status[4:])
        return self.parsed

    def select_eep(self, func, type, direction=None):
        ''' Set EEP based on FUNC and TYPE '''
        # set EEP profile
        self.rorg_func = func
        self.rorg_type = type
        return self.eep.find_profile(self.rorg, func, type, direction)

    def parse_eep(self, func=None, type=None, direction=None):
        ''' Parse EEP based on FUNC and TYPE '''
        # set EEP profile, if demanded
        if func is not None and type is not None:
            self.select_eep(func, type, direction)
        # parse data
        provides, values = self.eep.get_values(self.bit_data, self.bit_status)
        self.parsed.update(values)
        return list(provides)

    def set_eep(self, data):
        ''' Update packet data based on EEP '''
        # update bit_data based on data
        self._data_to_bitdata()
        # data is a dict with EEP description keys
        self.bit_data, self.bit_status = self.eep.set_values(self.rorg, self.bit_data, self.bit_status, data)
        self.status = self._from_bitarray(self.bit_status)
        # update data based on bit_data
        self._bitdata_to_data()

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
    sender = 0
    sender_hex = ''
    learn = True
    contains_eep = False

    def __str__(self):
        packet_str = super(RadioPacket, self).__str__()
        return '%s->%s (%d dBm): %s' % (self.sender_hex, self.destination_hex, self.dBm, packet_str)

    @staticmethod
    def create(rorg, func, type, direction=None,
               destination=[0xFF, 0xFF, 0xFF, 0xFF],
               sender=[0xDE, 0xAD, 0xBE, 0xEF],
               learn=False, **kwargs):
        return Packet.create(PACKET.RADIO, rorg, func, type, direction, destination, sender, learn, **kwargs)

    def parse(self):
        self.destination = self._combine_hex(self.optional[1:5])
        self.destination_hex = self._to_hex_string(self.optional[1:5])
        self.dBm = -self.optional[5]
        self.sender = self._combine_hex(self.data[-5:-1])
        self.sender_hex = self._to_hex_string(self.data[-5:-1])
        # Default to learn == True, as some devices don't have a learn button
        self.learn = True

        self.rorg = self.data[0]
        self._data_to_bitdata()

        # parse learn bit and FUNC/TYPE, if applicable
        if self.rorg == RORG.BS1:
            self.learn = not self.bit_data[DB0.BIT_3]
        if self.rorg == RORG.BS4:
            self.learn = not self.bit_data[DB0.BIT_3]
            if self.learn:
                self.contains_eep = self.bit_data[DB0.BIT_7]
                if self.contains_eep:
                    # Get rorg_func and rorg_type from an unidirectional learn packet
                    self.rorg_func = self._from_bitarray(self.bit_data[DB3.BIT_7:DB3.BIT_1])
                    self.rorg_type = self._from_bitarray(self.bit_data[DB3.BIT_1:DB2.BIT_2])
                    self.rorg_manufacturer = self._from_bitarray(self.bit_data[DB2.BIT_2:DB0.BIT_7])
                    logger.debug('learn received, EEP detected, RORG: 0x%02X, FUNC: 0x%02X, TYPE: 0x%02X, Manufacturer: 0x%02X' % (self.rorg, self.rorg_func, self.rorg_type, self.rorg_manufacturer))

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
