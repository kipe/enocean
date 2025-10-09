# -*- encoding: utf-8 -*-

import logging
import time

import serial

from .communicator import Communicator

LOGGER = logging.getLogger('enocean.communicators.SerialCommunicator')


class SerialCommunicator(Communicator):
    """ Serial port communicator class for EnOcean radio """

    def __init__(self, port: str = '/dev/ttyAMA0', callback: callable = None, loglevel=logging.NOTSET) -> None:
        super().__init__(callback, loglevel=loglevel)
        LOGGER.setLevel(loglevel)
        # Initialize serial port
        self.__ser = serial.Serial(port, 57600, timeout=0.1)

    def run(self) -> None:
        LOGGER.info('SerialCommunicator started')
        while not self._stop_flag.is_set():
            # If there's messages in transmit queue
            # send them
            while True:
                packet = self._get_from_send_queue()
                if not packet:
                    break
                try:
                    self.__ser.write(bytearray(packet.build()))
                except serial.SerialException:
                    self.stop()

            # Read chars from serial port as hex numbers
            try:
                self._buffer.extend(bytearray(self.__ser.read(16)))
            except serial.SerialException:
                LOGGER.error('Serial port exception! (device disconnected or multiple access on port?)')
                self.stop()
                continue
            self.parse()
            time.sleep(0)

        self.__ser.close()
        LOGGER.info('SerialCommunicator stopped')
