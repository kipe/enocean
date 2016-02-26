# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
import serial

from enocean.communicators.communicator import Communicator


class SerialCommunicator(Communicator):
    ''' Serial port communicator class for EnOcean radio '''
    logger = logging.getLogger('enocean.communicators.SerialCommunicator')

    def __init__(self, port='/dev/ttyAMA0', callback=None):
        super(SerialCommunicator, self).__init__(callback)
        # Initialize serial port
        self.__ser = serial.Serial(port, 57600, timeout=0.1)
        self.logger.info('SerialCommunicator started')

    def _receive(self):
        # Read chars from serial port as hex numbers
        try:
            self._buffer.extend(bytearray(self.__ser.read(16)))
        except serial.SerialException:
            self.logger.error('Serial port exception! (device disconnected or multiple access on port?)')
            pass

    def _transmit(self, packet):
        self.__ser.write(bytearray(packet.build()))

    def stop(self):
        self.__ser.close()
        self.logger.info('SerialCommunicator stopped')
        super(SerialCommunicator, self).stop()
