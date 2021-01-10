#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from enocean.consolelogger import init_logging
from enocean.protocol.secure import SecureStore
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PARSE_RESULT, PACKET, RORG

# note that importing enocean.protocol.secure needs pycryptodome
# $ pip3 install pycryptodome

# Secure Teach-In telegrams (PTM215 part 1)
msg1 = bytearray([
    0x55,
    0x00, 0x0F, 0x07, 0x01,
    0x2B,
    0x35, 0x24, 0x4b,  0xC0, 0xFF, 0x45, 0x6E, 0x4F, 0x63, 0x65,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
    0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
    0x71
])

# Secure Teach-In telegrams (PTM215 part 2)
msg2 = bytearray([
    0x55,
    0x00, 0x12, 0x07, 0x01,
    0x18,
    0x35, 0x40, 0x61, 0x6E, 0x20, 0x47, 0x6D, 0x62, 0x48, 0x2E, 0x31, 0x33, 0x00,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
    0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
    0xF0
])

# Secure telegram (PTM215 A0 pressed)
msg3 = bytearray([
    0x55,
    0x00, 0x0A, 0x07, 0x01,
    0xEB,
    0x30, 0xD0, 0xB5, 0x18, 0xFB,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
    0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
    0x4D
])

# Secure telegram (PTM215 A0 released)
msg4 = bytearray([
    0x55,
    0x00, 0x0A, 0x07, 0x01,
    0xEB,
    0x30, 0x7B, 0xAE, 0xC8, 0x28,  0x01, 0x9E, 0xB6, 0x3B, 0x00,
    0x00, 0xff, 0xff, 0xff, 0xff, 0x37, 0x00,
    0x94
])

init_logging()

# setup the secure store for paired devices
secure_devices = SecureStore()
# add a file name for simple pickle store
# or sub class and override load() and store() for a custom implementation
# secure_devices = SecureStore('foo.pickle')

# allow secure teach in for a maximum number of devices (max_devices=1),
# a limited time (max_time=300 i.e. 5 minutes),
# and a required minimum dBm (min_dBm=-56 i.e. about a meter distance).
secure_devices.allow_teach_in()

for msg in [msg1, msg2, msg3, msg4]:
    status, buf, packet = Packet.parse_msg(msg)
    assert status == PARSE_RESULT.OK
    assert buf == []
    print('INPUT', packet)

    if packet.packet_type == PACKET.RADIO_ERP1:
        if packet.rorg == RORG.SEC:
            print('Secure telegram')
            # lookup the paired device, verify and decrypt
            dev = secure_devices.decrypt(packet)
            # the packet is now decrypted to SECD
            assert packet.rorg == RORG.SECD
            print('Decrypted telegram:', packet)

            # translate RORG.SECD of PTM215 to VLD (D2-03-00)
            dev.translate_application(packet)
            # the packet is now VLD (D2-03-00)
            assert packet.rorg == RORG.VLD
            print('Translated telegram:', packet)

            # translate profile D2-03-00 (payload 4 bits) to RPS (F6-02-01)
            dev.translate_profile(packet)
            # the packet is now RPS (F6-02-01)
            assert packet.rorg == RORG.RPS
            print('Converted telegram:', packet)

        elif packet.rorg == RORG.SEC_ENCAPS:
            print('Secure telegram with RORG encapsulation')
            print('RORG not handeld.')

        elif packet.rorg == RORG.SECD:
            print('Non-secure message type that results from the decryption of a secure message with R-ORG 0x30.')
            print('RORG not handeld.')

        elif packet.rorg == RORG.SEC_CDM:
            print('Secure chained Messages')
            print('RORG not handeld.')

        elif packet.rorg == RORG.SEC_MAN:
            print('Maintenance Security message')
            print('RORG not handeld.')

        elif packet.rorg == RORG.SEC_TI:
            print('Secure Teach-In telegrams transmit private key and rolling to the communication partner')
            dev = secure_devices.teach_in(packet)
            # dev is None for the first teach-in packet
            # dev is the paired SecureDevice for the second teach-in packet
            print('Teach-in result:', dev)

    else:
        print('Packet type not handeld.')
