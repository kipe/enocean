# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
from collections import OrderedDict

import enocean.utils
from enocean.protocol import crc8
from enocean.protocol.eep import EEP
from enocean.protocol.constants import PACKET, RORG, PARSE_RESULT, DB0, DB2, DB3, DB4, DB6


class Packet(object):
    '''
    Base class for Packet.
    Mainly used for for packet generation and
    Packet.parse_msg(buf) for parsing message.
    parse_msg() returns subclass, if one is defined for the data type.
    '''
    eep = EEP()
    logger = logging.getLogger('enocean.protocol.packet')

    def __init__(self, packet_type, data=None, optional=None):
        self.packet_type = packet_type
        self.rorg = RORG.UNDEFINED
        self.rorg_func = None
        self.rorg_type = None
        self.rorg_manufacturer = None

        if not isinstance(data, list) or data is None:
            self.logger.warning('Replacing Packet.data with default value.')
            self.data = []
        else:
            self.data = data

        if not isinstance(optional, list) or optional is None:
            self.logger.warning('Replacing Packet.optional with default value.')
            self.optional = []
        else:
            self.optional = optional

        self.status = 0
        self.parsed = OrderedDict({})
        self.repeater_count = 0
        self._profile = None

        self.parse()

    def __str__(self):
        return '0x%02X %s %s %s' % (self.packet_type, [hex(o) for o in self.data], [hex(o) for o in self.optional], self.parsed)

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.packet_type == other.packet_type and self.rorg == other.rorg and self.data == other.data and self.optional == other.optional

    @property
    def _bit_data(self):
        # First and last 5 bits are always defined, so the data we're modifying is between them...
        # TODO: This is valid for the packets we're currently manipulating.
        # Needs the redefinition of Packet.data -> Packet.message.
        # Packet.data would then only have the actual, documented data-bytes. Packet.message would contain the whole message.
        # See discussion in issue #14
        return enocean.utils.to_bitarray(self.data[1:len(self.data) - 5], (len(self.data) - 6) * 8)

    @_bit_data.setter
    def _bit_data(self, value):
        # The same as getting the data, first and last 5 bits are ommitted, as they are defined...
        for byte in range(len(self.data) - 6):
            self.data[byte+1] = enocean.utils.from_bitarray(value[byte*8:(byte+1)*8])

    # # COMMENTED OUT, AS NOTHING TOUCHES _bit_optional FOR NOW.
    # # Thus, this is also untested.
    # @property
    # def _bit_optional(self):
    #     return enocean.utils.to_bitarray(self.optional, 8 * len(self.optional))

    # @_bit_optional.setter
    # def _bit_optional(self, value):
    #     if self.rorg in [RORG.RPS, RORG.BS1]:
    #         self.data[1] = enocean.utils.from_bitarray(value)
    #     if self.rorg == RORG.BS4:
    #         for byte in range(4):
    #             self.data[byte+1] = enocean.utils.from_bitarray(value[byte*8:(byte+1)*8])

    @property
    def _bit_status(self):
        return enocean.utils.to_bitarray(self.status)

    @_bit_status.setter
    def _bit_status(self, value):
        self.status = enocean.utils.from_bitarray(value)

    @staticmethod
    def parse_msg(buf, communicator=None):
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
        buf = [ord(x) if not isinstance(x, int) else x for x in buf[list(buf).index(0x55):]]
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
            Packet.logger.error('Header CRC error!')
            # Return CRC_MISMATCH
            return PARSE_RESULT.CRC_MISMATCH, buf, None
        if msg[6 + data_len + opt_len] != crc8.calc(msg[6:6 + data_len + opt_len]):
            # Fail if doesn't match message
            Packet.logger.error('Data CRC error!')
            # Return CRC_MISMATCH
            return PARSE_RESULT.CRC_MISMATCH, buf, None

        # If we got this far, everything went ok (?)
        if packet_type == PACKET.RADIO:
            # Need to handle UTE Teach-in here, as it's a separate packet type...
            if data[0] == RORG.UTE:
                packet = UTETeachIn(packet_type, data, opt_data, communicator=communicator)
                # Send a response automatically, works only if
                # - communicator is set
                # - communicator.teach_in == True
                packet.send_response()
            else:
                packet = RadioPacket(packet_type, data, opt_data)
        elif packet_type == PACKET.RESPONSE:
            packet = ResponsePacket(packet_type, data, opt_data)
        elif packet_type == PACKET.EVENT:
            packet = EventPacket(packet_type, data, opt_data)
        else:
            packet = Packet(packet_type, data, opt_data)

        return PARSE_RESULT.OK, buf, packet

    @staticmethod
    def create(packet_type, rorg, rorg_func, rorg_type, direction=None, command=None,
               destination=None,
               sender=None,
               learn=False, **kwargs):
        '''
        Creates an packet ready for sending.
        Uses rorg, rorg_func and rorg_type to determine the values set based on EEP.
        Additional arguments (**kwargs) are used for setting the values.

        Currently only supports:
            - PACKET.RADIO
            - RORGs RPS, BS1, BS4, VLD.

        TODO:
            - Require sender to be set? Would force the "correct" sender to be set.
            - Do we need to set telegram control bits?
              Might be useful for acting as a repeater?
        '''

        if packet_type != PACKET.RADIO:
            # At least for now, only support PACKET.RADIO.
            raise ValueError('Packet type not supported by this function.')

        if rorg not in [RORG.RPS, RORG.BS1, RORG.BS4, RORG.VLD]:
            # At least for now, only support these RORGS.
            raise ValueError('RORG not supported by this function.')

        if destination is None:
            Packet.logger.warning('Replacing destination with broadcast address.')
            destination = [0xFF, 0xFF, 0xFF, 0xFF]

        # TODO: Should use the correct Base ID as default.
        #       Might want to change the sender to be an offset from the actual address?
        if sender is None:
            Packet.logger.warning('Replacing sender with default address.')
            sender = [0xDE, 0xAD, 0xBE, 0xEF]

        if not isinstance(destination, list) or len(destination) != 4:
            raise ValueError('Destination must a list containing 4 (numeric) values.')

        if not isinstance(sender, list) or len(sender) != 4:
            raise ValueError('Sender must a list containing 4 (numeric) values.')

        packet = Packet(packet_type, data=[], optional=[])
        packet.rorg = rorg
        packet.data = [packet.rorg]
        # Select EEP at this point, so we know how many bits we're dealing with (for VLD).
        packet.select_eep(rorg_func, rorg_type, direction, command)

        # Initialize data depending on the profile.
        if rorg in [RORG.RPS, RORG.BS1]:
            packet.data.extend([0])
        elif rorg == RORG.BS4:
            packet.data.extend([0, 0, 0, 0])
        else:
            packet.data.extend([0] * int(packet._profile.get('bits', '1')))
        packet.data.extend(sender)
        packet.data.extend([0])
        # Always use sub-telegram 3, maximum dbm (as per spec, when sending),
        # and no security (security not supported as per EnOcean Serial Protocol).
        packet.optional = [3] + destination + [0xFF] + [0]

        if command:
            # Set CMD to command, if applicable.. Helps with VLD.
            kwargs['CMD'] = command

        packet.set_eep(kwargs)
        if rorg in [RORG.BS1, RORG.BS4] and not learn:
            if rorg == RORG.BS1:
                packet.data[1] |= (1 << 3)
            if rorg == RORG.BS4:
                packet.data[4] |= (1 << 3)
        packet.data[-1] = packet.status

        # Parse the built packet, so it corresponds to the received packages
        # For example, stuff like RadioPacket.learn should be set.
        packet = Packet.parse_msg(packet.build())[2]
        packet.rorg = rorg
        packet.parse_eep(rorg_func, rorg_type, direction, command)
        return packet

    def parse(self):
        ''' Parse data from Packet '''
        # Parse status from messages
        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            self.status = self.data[-1]
        if self.rorg == RORG.VLD:
            self.status = self.optional[-1]

        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            # These message types should have repeater count in the last for bits of status.
            self.repeater_count = enocean.utils.from_bitarray(self._bit_status[4:])
        return self.parsed

    def select_eep(self, rorg_func, rorg_type, direction=None, command=None):
        ''' Set EEP based on FUNC and TYPE '''
        # set EEP profile
        self.rorg_func = rorg_func
        self.rorg_type = rorg_type
        self._profile = self.eep.find_profile(self._bit_data, self.rorg, rorg_func, rorg_type, direction, command)
        return self._profile is not None

    def parse_eep(self, rorg_func=None, rorg_type=None, direction=None, command=None):
        ''' Parse EEP based on FUNC and TYPE '''
        # set EEP profile, if demanded
        if rorg_func is not None and rorg_type is not None:
            self.select_eep(rorg_func, rorg_type, direction, command)
        # parse data
        provides, values = self.eep.get_values(self._profile, self._bit_data, self._bit_status)
        self.parsed.update(values)
        return list(provides)

    def set_eep(self, data):
        ''' Update packet data based on EEP. Input data is a dictionary with keys corresponding to the EEP. '''
        self._bit_data, self._bit_status = self.eep.set_values(self._profile, self._bit_data, self._bit_status, data)

    def build(self):
        ''' Build Packet for sending to EnOcean controller '''
        data_length = len(self.data)
        ords = [0x55, (data_length >> 8) & 0xFF, data_length & 0xFF, len(self.optional), int(self.packet_type)]
        ords.append(crc8.calc(ords[1:5]))
        ords.extend(self.data)
        ords.extend(self.optional)
        ords.append(crc8.calc(ords[6:]))
        return ords


class RadioPacket(Packet):
    destination = [0xFF, 0xFF, 0xFF, 0xFF]
    dBm = 0
    sender = [0xFF, 0xFF, 0xFF, 0xFF]
    learn = True
    contains_eep = False

    def __str__(self):
        packet_str = super(RadioPacket, self).__str__()
        return '%s->%s (%d dBm): %s' % (self.sender_hex, self.destination_hex, self.dBm, packet_str)

    @staticmethod
    def create(rorg, rorg_func, rorg_type, direction=None, command=None,
               destination=None, sender=None, learn=False, **kwargs):
        return Packet.create(PACKET.RADIO, rorg, rorg_func, rorg_type, direction, command, destination, sender, learn, **kwargs)

    @property
    def sender_int(self):
        return enocean.utils.combine_hex(self.sender)

    @property
    def sender_hex(self):
        return enocean.utils.to_hex_string(self.sender)

    @property
    def destination_int(self):
        return enocean.utils.combine_hex(self.destination)

    @property
    def destination_hex(self):
        return enocean.utils.to_hex_string(self.destination)

    def parse(self):
        self.destination = self.optional[1:5]
        self.dBm = -self.optional[5]
        self.sender = self.data[-5:-1]
        # Default to learn == True, as some devices don't have a learn button
        self.learn = True

        self.rorg = self.data[0]

        # parse learn bit and FUNC/TYPE, if applicable
        if self.rorg == RORG.BS1:
            self.learn = not self._bit_data[DB0.BIT_3]
        if self.rorg == RORG.BS4:
            self.learn = not self._bit_data[DB0.BIT_3]
            if self.learn:
                self.contains_eep = self._bit_data[DB0.BIT_7]
                if self.contains_eep:
                    # Get rorg_func and rorg_type from an unidirectional learn packet
                    self.rorg_func = enocean.utils.from_bitarray(self._bit_data[DB3.BIT_7:DB3.BIT_1])
                    self.rorg_type = enocean.utils.from_bitarray(self._bit_data[DB3.BIT_1:DB2.BIT_2])
                    self.rorg_manufacturer = enocean.utils.from_bitarray(self._bit_data[DB2.BIT_2:DB0.BIT_7])
                    self.logger.debug('learn received, EEP detected, RORG: 0x%02X, FUNC: 0x%02X, TYPE: 0x%02X, Manufacturer: 0x%02X' % (self.rorg, self.rorg_func, self.rorg_type, self.rorg_manufacturer))

        return super(RadioPacket, self).parse()


class UTETeachIn(RadioPacket):
    # Request types
    TEACH_IN = 0b00
    DELETE = 0b01
    NOT_SPECIFIC = 0b10

    # Response types
    NOT_ACCEPTED = [False, False]
    TEACHIN_ACCEPTED = [False, True]
    DELETE_ACCEPTED = [True, False]
    EEP_NOT_SUPPORTED = [True, True]

    unidirectional = False
    response_expected = False
    number_of_channels = 0xFF
    rorg_of_eep = RORG.UNDEFINED
    request_type = NOT_SPECIFIC
    channel = None

    contains_eep = True

    def __init__(self, packet_type, data=None, optional=None, communicator=None):
        self.__communicator = communicator
        super(UTETeachIn, self).__init__(packet_type=packet_type, data=data, optional=optional)

    @property
    def bidirectional(self):
        return not self.unidirectional

    @property
    def teach_in(self):
        return self.request_type != self.DELETE

    @property
    def delete(self):
        return self.request_type == self.DELETE

    def parse(self):
        super(UTETeachIn, self).parse()
        self.unidirectional = not self._bit_data[DB6.BIT_7]
        self.response_expected = not self._bit_data[DB6.BIT_6]
        self.request_type = enocean.utils.from_bitarray(self._bit_data[DB6.BIT_5:DB6.BIT_3])
        self.rorg_manufacturer = enocean.utils.from_bitarray(self._bit_data[DB3.BIT_2:DB2.BIT_7] + self._bit_data[DB4.BIT_7:DB3.BIT_7])
        self.channel = self.data[2]
        self.rorg_type = self.data[5]
        self.rorg_func = self.data[6]
        self.rorg_of_eep = self.data[7]
        if self.teach_in:
            self.learn = True
        return self.parsed

    def _create_response_packet(self, sender_id, response=TEACHIN_ACCEPTED):
        # Create data:
        # - Respond with same RORG (UTE Teach-in)
        # - Always use bidirectional communication, set response code, set command identifier.
        # - Databytes 5 to 0 are copied from the original message
        # - Set sender id and status
        data = [self.rorg] + \
               [enocean.utils.from_bitarray([True, False] + response + [False, False, False, True])] + \
               self.data[2:8] + \
               sender_id + [0]

        # Always use 0x03 to indicate sending, attach sender ID, dBm, and security level
        optional = [0x03] + self.sender + [0xFF, 0x00]

        return RadioPacket(PACKET.RADIO, data=data, optional=optional)

    def send_response(self, response=TEACHIN_ACCEPTED):
        if self.__communicator is None:
            self.logger.error('Communicator not set, cannot send UTE teach-in response.')
            return
        if not self.__communicator.teach_in:
            self.logger.info('Communicator not set to teach-in mode, not sending UTE teach-in response.')
            return
        self.logger.info('Sending response to UTE teach-in.')
        self.__communicator.send(
            self._create_response_packet(self.__communicator.base_id))


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
