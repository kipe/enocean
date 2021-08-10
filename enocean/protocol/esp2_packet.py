# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from enocean.protocol.packet import EventPacket, Packet, RadioPacket, ResponsePacket, UTETeachInPacket
import logging
from collections import OrderedDict

import enocean.utils
from enocean.protocol import crc8
from enocean.protocol.eep import EEP
from enocean.protocol.constants import ORG, PACKET, RORG, PARSE_RESULT, DB0, DB2, DB3, DB4, DB6


class ESP2Packet(Packet):
    '''
    Base class for ESP2 Packet.
    Mainly used for for packet generation and
    Packet.parse_msg(buf) for parsing message.
    parse_msg() returns subclass, if one is defined for the data type.
    '''

    @staticmethod
    def parse_msg(buf):
        '''
        Parses message from buffer.
        returns:
            - PARSE_RESULT
            - remaining buffer
            - Packet -object (if message was valid, else None)
        '''
        # If the buffer doesn't contain 0xA5 (start char)
        # the message isn't needed -> ignore
        # if 0xA5 not in buf:
        #     return PARSE_RESULT.INCOMPLETE, [], None
        # else:
        #     if buf[list(buf).index(0xA5)+1] != 0x5A:
        #         return PARSE_RESULT.INCOMPLETE, [], None

        if not buf:
            return PARSE_RESULT.INCOMPLETE, [], None

        if 0xA5 not in buf:
            return PARSE_RESULT.INCOMPLETE, [], None

        msg_len = 0

        for index,value in enumerate(buf):
            try:
                if buf[index] == 0xA5 and buf[index+1] == 0x5A:
                    data_len = buf[index+2] & 0x1F
                    HSEQ = buf[index+2] >> 5
                    opt_len = 0
                    msg_len = data_len
                    if len(buf[index+2:]) < msg_len:
                        # If buffer isn't long enough, the message is incomplete
                        return PARSE_RESULT.INCOMPLETE, buf, None
                    crcval = crc8.calc_ESP2(buf[index+2:index+2+data_len])
                    if buf[index+2+data_len] == crcval:
                        buf = buf[index+2:]
                        break
                    else:
                        ESP2Packet.logger.error('Data CRC error!')
                        return PARSE_RESULT.CRC_MISMATCH, buf, None
            except IndexError:
                # If the fields don't exist, message is incomplete
                return PARSE_RESULT.INCOMPLETE, buf, None

        if msg_len == 0:
            ESP2Packet.logger.error('Data Length is Zero!')
            return PARSE_RESULT.INCOMPLETE, [], None

        msg = buf[0:msg_len]
        buf = buf[msg_len+1:]

        packet_type = HSEQ
        data = msg[1:data_len]
        opt_data = []

        #Adopt ORG to RORG for ESP2
        if data[0] == ORG.BS1:
            data[0] = RORG.BS1
        if data[0] == ORG.BS4:
            data[0] = RORG.BS4
        if data[0] == ORG.RPS:
            data[0] = RORG.RPS

        # If we got this far, everything went ok (?)
        if packet_type == PACKET.RADIO:
            # Need to handle UTE Teach-in here, as it's a separate packet type...
            if data[0] == RORG.UTE:
                packet = ESP2UTETeachInPacket(packet_type, data, opt_data)
                # Send a response automatically, works only if
                # - communicator is set
                # - communicator.teach_in == True
                packet.send_response()
            else:
                packet = ESP2RadioPacket(packet_type, data, opt_data)
        elif packet_type == PACKET.RESPONSE:
            packet = ESP2ResponsePacket(packet_type, data, opt_data)
        elif packet_type == PACKET.EVENT:
            #packet = EventPacket(packet_type, data, opt_data)
            packet = ESP2RadioPacket(packet_type, data, opt_data)
        else:
            packet = ESP2Packet(packet_type, data, opt_data)

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

        if rorg not in [RORG.RPS, RORG.BS1, RORG.BS4]:
            # At least for now, only support these RORGS.
            raise ValueError('RORG not supported by this function.')

        if destination is None:
            destination = [0xFF, 0xFF, 0xFF, 0xFF]

        # TODO: Should use the correct Base ID as default.
        #       Might want to change the sender to be an offset from the actual address?
        if sender is None:
            ESP2Packet.logger.warning('Replacing sender with default address.')
            sender = [0xDE, 0xAD, 0xBE, 0xEF]

        if not isinstance(destination, list) or len(destination) != 4:
            raise ValueError('Destination must a list containing 4 (numeric) values.')

        if not isinstance(sender, list) or len(sender) != 4:
            raise ValueError('Sender must a list containing 4 (numeric) values.')

        packet = ESP2Packet(packet_type, data=[], optional=[])
        packet.rorg = rorg

        if packet.rorg == RORG.BS1:
            packet.rorg = ORG.BS1
        if packet.rorg == RORG.BS4:
            packet.rorg = ORG.BS4
        if packet.rorg == RORG.RPS:
            packet.rorg = ORG.RPS

        packet.data = [packet.rorg]
        # Select EEP at this point, so we know how many bits we're dealing with (for VLD).
        #packet.select_eep(rorg_func, rorg_type, direction, command)

        # Initialize data depending on the profile.
       # if rorg in [RORG.RPS, RORG.BS1]:
       #     packet.data.extend([0])
        #elif rorg == RORG.BS4:
        packet.data.extend(command)
        #else:
          #  packet.data.extend([0] * int(packet._profile.get('bits', '1')))
        packet.data.extend(sender)
        packet.data.extend([0])
        # Always use sub-telegram 3, maximum dbm (as per spec, when sending),
        # and no security (security not supported as per EnOcean Serial Protocol).
        #packet.optional = [3] + destination + [0xFF] + [0]

        #if command:
            # Set CMD to command, if applicable.. Helps with VLD.
            #kwargs['CMD'] = command

        #packet.set_eep(kwargs)
        if rorg in [RORG.BS1, RORG.BS4] and not learn:
            if rorg == RORG.BS1:
                packet.data[1] |= (1 << 3)
            if rorg == RORG.BS4:
                packet.data[4] |= (1 << 3)
        packet.data[-1] = packet.status

        # Parse the built packet, so it corresponds to the received packages
        # For example, stuff like RadioPacket.learn should be set.
        packet = ESP2Packet.parse(packet.build_ESP2())[2]
        return packet

    def build(self):
        ''' Build Packet for sending to EnOcean controller '''
        data_length = len(self.data)+1
        ords = [0xA5, 0x5A, (data_length & 0x1F | ((int(self.packet_type)&0x07)<<5))]

        if self.data[0] in [RORG.RPS, RORG.BS4, RORG.BS1]:
            if self.data[0] == RORG.RPS:
                self.data[0] = ORG.RPS
            if self.data[0] == RORG.BS1:
                self.data[0] = ORG.BS1
            if self.data[0] == RORG.BS4:
                self.data[0] = ORG.BS4

        ords.extend(self.data)
        ords.append(crc8.calc_ESP2(ords[2:]))
        return ords

class ESP2RadioPacket(RadioPacket): 
    @staticmethod
    def create(rorg, rorg_func, rorg_type, direction=None, command=None,
               destination=None, sender=None, learn=False, **kwargs):
        return ESP2Packet.create(PACKET.RADIO_ERP1, rorg, rorg_func, rorg_type,
                             direction, command, destination, sender, learn, **kwargs)

class ESP2ResponsePacket(ResponsePacket, ESP2Packet):
    """ESP2 version of response package"""

class ESP2EventPacket(EventPacket, ESP2Packet):
    """ESP2 version of event package"""

class ESP2UTETeachInPacket(UTETeachInPacket, ESP2RadioPacket):
    """ESP2 version of UTE teachin package"""