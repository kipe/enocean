# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging
import serial

from communicator import Communicator

logger = logging.getLogger('enocean.communicators.SerialCommunicator')


class SerialCommunicator(Communicator):
    ''' Serial port communicator class for EnOcean radio '''
    def __init__(self, port='/dev/ttyAMA0'):
        super(SerialCommunicator, self).__init__()
        # Initialize serial port
        self.__ser = serial.Serial(port, 57600, timeout=0.1)

    def run(self):
        logger.info('SerialCommunicator started')
        while not self._stop.is_set():
            # If there's messages in transmit queue
            # send them
            while True:
                p = self._get_from_send_queue()
                if not p:
                    break
                self.__ser.write(str(bytearray(p.build())))

            # Read chars from serial port as hex numbers
            try:
                self._buffer.extend([ord(c) for c in self.__ser.read(16)])
            except serial.SerialException:
                logger.error('Serial port exception! (device disconnected or multiple access on port?)')
                break
            self.parse()

        self.__ser.close()
        logger.info('SerialCommunicator stopped')
