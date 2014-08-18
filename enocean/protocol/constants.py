# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from enum import IntEnum


# EnOceanSerialProtocol3.pdf / 12
class PACKET(IntEnum):
    RESERVED = 0x00
    RADIO = 0x01
    RESPONSE = 0x02
    RADIO_SUB_TEL = 0x03
    EVENT = 0x04
    COMMON_COMMAND = 0x05
    SMART_ACK_COMMAND = 0x06
    REMOTE_MAN_COMMAND = 0x07
    RADIO_MESSAGE = 0x09
    RADIO_ADVANCED = 0x0A


# EnOceanSerialProtocol3.pdf / 18
class RETURN_CODE(IntEnum):
    OK = 0x00
    ERROR = 0x01
    NOT_SUPPORTED = 0x02
    WRONG_PARAM = 0x04
    OPERATION_DENIED = 0x04


# EnOceanSerialProtocol3.pdf / 20
class EVENT_CODE(IntEnum):
    SA_RECLAIM_NOT_SUCCESFUL = 0x01
    SA_CONFIRM_LEARN = 0x02
    SA_LEARN_ACK = 0x03
    CO_READY = 0x04
    CO_EVENT_SECUREDEVICES = 0x05


# EnOcean_Equipment_Profiles_EEP_V2.61_public.pdf / 8
class RORG(IntEnum):
    UNDEFINED = 0x00
    RPS = 0xF6
    BS1 = 0xD5
    BS4 = 0xA5
    VLD = 0xD2
    MSC = 0xD1
    ADT = 0xA6
    SM_LRN_REQ = 0xC6
    SM_LRN_ANS = 0xC7
    SM_REC = 0xA7
    SYS_EX = 0xC5
    SEC = 0x30
    SEC_ENCAPS = 0x31


# Results for message parsing
class PARSE_RESULT(IntEnum):
    OK = 0x00
    INCOMPLETE = 0x01
    CRC_MISMATCH = 0x03
