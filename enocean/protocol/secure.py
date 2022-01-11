# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
from enum import IntEnum
import struct
import time
import pickle
import os.path

from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
from Crypto.Cipher import AES
from Crypto.Hash import CMAC


def split_bytes_be(num, byte_count):
    '''Split number to byte_count big-endian bytes.'''
    return struct.pack('>I', num)[-byte_count:]


class RLC_ALGO(IntEnum):
    NO_RLC = 0
    RLC_16_IMPLICIT = 2
    RLC_24_IMPLICIT = 4
    RLC_24_EXPLICIT = 5
    RLC_32_24_EXPLICIT = 6
    RLC_32_32_EXPLICIT = 7


class MAC_ALGO(IntEnum):
    NO_MAC = 0
    MAC_24_AES128 = 1
    MAC_32_AES128 = 2


class DATA_ENC(IntEnum):
    NO_ENC = 0
    ENC_HSE = 1
    ENC_NA = 2
    ENC_VAES128 = 3
    ENC_AESCBC = 4


class SecureDevice(object):
    '''
    Secure device parameters.
    '''
    logger = logging.getLogger('enocean.protocol.secure')
    sender = []
    sender_int = 0
    psk = 0
    ptm = 0
    rlc_algo = 0
    rlc_tx = 0
    mac_algo = 0
    data_enc = 0
    rlc = 0
    key = ''

    def __init__(self, packets=None):
        if packets:
            self.parse(packets)

    def parse(self, packets):
        '''
        Parse Secure Teach-In telegrams to enroll the communication partner.
        Requires two RORG.SEC_TI packets, in order.
        Raises ValueError otherwise.
        '''
        if len(packets) != 2:
            raise ValueError('Excatly two packets required to teach-in secure device.')
        if packets[0].rorg != RORG.SEC_TI or packets[1].rorg != RORG.SEC_TI:
            raise ValueError('Packets of RORG.SEC_TI required to teach-in secure device.')
        if packets[0].packet_type != packets[1].packet_type:
            raise ValueError('Packets need to be the same type to teach-in secure device.')
        if packets[0].sender != packets[1].sender:
            raise ValueError('Packets of RORG.SEC_TI required to teach-in secure device.')

        packets[0].parse_eep(0x00, 0x00)
        if packets[0].parsed['CNT']['raw_value'] != 2 or packets[0].parsed['IDX']['raw_value'] != 0:
            raise ValueError('Packets need to be in-order to teach-in secure device.')

        packets[1].parse_eep(0x00, 0x00, command='1')
        if packets[1].parsed['IDX']['raw_value'] != 1:
            raise ValueError('Packets need to be in-order to teach-in secure device.')

        self.sender = packets[0].sender
        self.sender_int = packets[0].sender_int
        self.psk = packets[0].parsed['PSK']['raw_value']
        self.ptm = packets[0].parsed['TYPE']['raw_value']
        self.rlc_algo = packets[0].parsed['RLC_ALGO']['raw_value']
        self.rlc_tx = packets[0].parsed['RLC_TX']['raw_value']
        self.mac_algo = packets[0].parsed['MAC_ALGO']['raw_value']
        self.data_enc = packets[0].parsed['DATA_ENC']['raw_value']
        self.rlc = packets[0].parsed['RLC']['raw_value']

        var_len0 = len(packets[0].data) - 5  # 5 bytes sender+status
        key0 = packets[0].data[5:var_len0]  # idx 0: key[0:5]

        var_len1 = len(packets[1].data) - 5  # 5 bytes sender+status
        key1 = packets[1].data[2:var_len1]  # idx 1: key[6:16]

        self.key = bytearray(key0 + key1)

    @property
    def rlc_len(self):
        return [0, 0, 2, 2, 3, 3, 4, 4][self.rlc_algo]

    @property
    def explicit_rlc_len(self):
        return [0, 0, 0, 0, 0, 3, 3, 4][self.rlc_algo]

    @property
    def mac_len(self):
        return [0, 3, 4, 0][self.mac_algo]

    def vaes_decrypt(self, data_enc, rlc):
        VAES_INIT = bytearray([0x34, 0x10, 0xde, 0x8f, 0x1a, 0xba, 0x3e, 0xff,
                               0x9f, 0x5a, 0x11, 0x71, 0x72, 0xea, 0xca, 0xbd])

        rlc = split_bytes_be(rlc, self.rlc_len)
        rlc += b'\x00' * (16 - len(rlc))  # pad to 16 bytes
        vaes_init = bytes(a ^ b for (a, b) in zip(VAES_INIT, rlc))

        cipher = AES.new(self.key, AES.MODE_ECB)
        enc = cipher.encrypt(vaes_init)

        data_dec = [a ^ b for (a, b) in zip(data_enc, enc)]
        return data_dec

    def verify_cmac(self, rorg, data, rlc, mac_tag=None):
        return bytearray(mac_tag) == bytearray(self.gen_cmac(rorg, data, rlc))

    def gen_cmac(self, rorg, data, rlc):
        rlc = split_bytes_be(rlc, self.rlc_len)

        msg = [rorg]
        msg.extend(data)
        msg.extend(rlc)

        mac = CMAC.new(self.key, ciphermod=AES, mac_len=4)
        mac.update(bytearray(msg))

        return mac.digest()[:self.mac_len]

    def decrypt_SEC(self, packet, rlc_window=100):
        '''
        Verify CMAC and decrypt RORG.SEC to RORG.SECD, packet unchanged otherwise.
        Raises ValueError if packet is not RORG.SEC.
        '''
        if packet.rorg != RORG.SEC:
            raise ValueError('Packet is not RORG.SEC.')

        rlc = self.rlc

        rorg = packet.rorg
        data = packet.data[1:len(packet.data) - 5]  # 1 byte rorg + 5 bytes sender+status

        mac_len = self.mac_len
        cmac = data[-mac_len:]
        data = data[:-mac_len]

        rlc_len = self.explicit_rlc_len
        if rlc_len:
            explicit_rlc = data[-rlc_len:]
            data = data[:-rlc_len]

        data_enc = data

        while rlc_window >= 0:
            # self.gen_cmac(rorg, data_enc, rlc)
            if self.verify_cmac(rorg, data_enc, rlc, cmac):
                self.rlc = rlc + 1
                data_dec = self.vaes_decrypt(data_enc, rlc)
                # transform RORG.SEC to RORG.SECD
                packet.rorg = RORG.SECD
                packet.data[0] = packet.rorg  # 0x30 -> 0x32
                packet.data[1:1 + len(data_enc)] = data_dec
                # splice the explicit rlc and mac out
                packet.data[1 + len(data_enc):1 + len(data_enc) + rlc_len + mac_len] = []
                packet.status = 0
                return True
            rlc += 1
            rlc_window -= 1

        return False

    def translate_application(self, packet):
        '''
        Transform RORG.SECD to matching RORG.VLD (D2-03-00) if application type is PTM.
        Raises ValueError if packet is not RORG.SECD.
        '''
        if packet.rorg != RORG.SECD:
            raise ValueError('Packet is not RORG.SECD.')
        if self.ptm:
            packet.rorg = RORG.VLD
            packet.data[0] = packet.rorg
            packet.data[1] &= 0xf
            packet.parse_eep(0x03, 0x00)

    def translate_profile(self, packet):
        '''
        Convert profile D2-03-00 (payload 4 bits) to RPS (F6-02-01).
        Raises if packet is not RORG.VLD or not profile D2-03-00.
        '''
        if packet.rorg != RORG.VLD:
            raise ValueError('Packet is not RORG.VLD.')
        if packet.rorg_func != 0x03 or packet.rorg_type != 0x00:
            raise ValueError('Packet is not profile D2-03-00.')

        # conversion between the profiles D2-03-00 (payload 4 bits) and F6-02-01:
        # D2-03-00 DATA to F6-02-01 DATA and F6-02-01 STATUS
        map_D2_03_00_to_F6_02_01 = {
            0: (0, 0),  # Reserved
            1: (0, 0),  # Reserved
            2: (0, 0),  # Reserved
            3: (0, 0),  # Reserved
            4: (0, 0),  # Reserved
            5: (0x17, 0x30),  # Button A1 + B0 pressed,energy bow pressed
            6: (0x70, 0x20),  # 3 or 4 buttons pressed,energy bow pressed
            7: (0x37, 0x30),  # Button A0 + B0 pressed,energy bow pressed
            8: (0x10, 0x20),  # No buttons pressed, energybow pressed
            9: (0x15, 0x30),  # Button A1 + B1 pressed,energy bow pressed
            10: (0x35, 0x30),  # Button A0 + B1 pressed,energy bow pressed
            11: (0x50, 0x30),  # Button B1 pressed, energybow pressed
            12: (0x70, 0x30),  # Button B0 pressed, energybow pressed
            13: (0x10, 0x30),  # Button A1 pressed, energybow pressed
            14: (0x30, 0x30),  # Button A0 pressed, energybow pressed
            15: (0, 0x20),  # Energy bow released
        }
        (data, status) = map_D2_03_00_to_F6_02_01[packet.data[1]]
        packet.rorg = RORG.RPS
        packet.data[0] = packet.rorg
        packet.data[1] = data
        packet.status = status
        packet.parse_eep(0x02, 0x01)


class SecureStore(object):
    '''
    Secure paired devices store.
    '''
    logger = logging.getLogger('enocean.protocol.secure')
    file = None
    paired = {}
    teachin_max_devices = 0
    teachin_max_timeout = 0
    teachin_min_dBm = 0
    teachin_packets = []
    teachin_packet_time = 0

    def __init__(self, file=None):
        self.file = file
        self.load()

    def load(self):
        '''This should be overridden with a better suited implementation.'''
        if self.file and os.path.exists(self.file):
            self.logger.info('Reading secure store from file')
            self.paired = pickle.load(open(self.file, 'rb'))

    def save(self, changed_device=None):
        '''This should be overridden with a better suited implementation.'''
        if self.file:
            self.logger.debug('Writing secure store to file')
            pickle.dump(self.paired, open(self.file, 'wb'))

    def add_device(self, secure_device):
        ''' Add a paired device manually '''
        self.paired[secure_device.sender_int] = secure_device
        self.save(secure_device)

    def remove_device(self, secure_device):
        '''
        Remove a paired device.
        Raises KeyError if not found.
        '''
        del self.paired[secure_device.sender_int]
        self.save(secure_device)

    def get_device(self, packet):
        '''
        Return the paired device matching the packet sender, None otherwise.
        '''
        try:
            return self.paired[packet.sender_int]
        except KeyError:
            pass

    def is_teach_in_allowed(self):
        '''
        Returns wether teach in is currently allowed.
        '''
        return self.teachin_max_devices > 0 and self.teachin_max_timeout >= time.time()

    def allow_teach_in(self, max_devices=1, max_time=300, min_dBm=-56):
        '''
        Allow secure teach-in.
        Defaults are to allow 1 device within 300 seconds (5 minutes)
        at least -56 dBm (about a meter distance).
        '''
        self.teachin_max_devices = max_devices
        self.teachin_max_timeout = time.time() + max_time
        self.teachin_min_dBm = min_dBm

    def teach_in(self, packet):
        '''
        Process secure teach-in packets. Call for each packet.
        Return the new paired device, None otherwise.
        '''
        if self.teachin_max_devices < 1:
            self.logger.info('Max teach-in devices reached, ignoring secure teach-in')
        elif self.teachin_max_timeout < time.time():
            self.logger.info('Max timeout reached, ignoring secure teach-in')
        elif self.teachin_min_dBm > packet.dBm:
            self.logger.info('Min dBm not reached (%d of %d), ignoring secure teach-in',
                             packet.dBm, self.teachin_min_dBm)
        elif len(self.teachin_packets) == 0 or self.teachin_packet_time + 4 < time.time():
            self.logger.debug('First secure teach-in packet received')
            self.teachin_packets = [packet]
            self.teachin_packet_time = time.time()
        elif len(self.teachin_packets) == 1:
            self.logger.debug('Second secure teach-in packet received')
            self.teachin_packets.append(packet)
            try:
                dev = SecureDevice(self.teachin_packets)
                self.add_device(dev)
                self.teachin_max_devices -= 1
                return dev
            except ValueError as e:
                self.logger.debug('Secure teach-in failed: %s', e)
            finally:
                self.teachin_packets = []

    def decrypt(self, packet):
        '''
        Find the matching paired device, verify and decrypt the packet.
        Raises ValueError otherwise.
        '''
        dev = self.get_device(packet)
        if not dev:
            raise ValueError('Device "%s" not paired.' % (packet.sender_hex))

        if not dev.decrypt_SEC(packet):
            raise ValueError('Secure packet verify and decrypt failed.')

        self.save(dev)  # update RLC
        return dev
