# -*- encoding: utf-8 -*-

import datetime
import logging
import queue
import threading
from typing import Union

from ..protocol.constants import COMMON_COMMAND, PACKET, PARSE_RESULT, RETURN_CODE
from ..protocol.packet import Packet, UTETeachInPacket
from ..protocol.version_info import VersionInfo

LOGGER = logging.getLogger('enocean.communicators.Communicator')


class Communicator(threading.Thread):
    """
    Communicator base-class for EnOcean.
    Not to be used directly, only serves as base class for SerialCommunicator etc.
    """

    def __init__(self, callback: callable = None, teach_in: bool = True, loglevel=logging.NOTSET) -> None:
        super().__init__()
        LOGGER.setLevel(loglevel)
        # Create an event to stop the thread
        self._stop_flag = threading.Event()
        # Input buffer
        self._buffer = []
        # Setup packet queues
        self.transmit = queue.Queue()
        self.receive = queue.Queue()
        # Set the callback method
        self.__callback = callback
        # Internal variable for the Base ID of the module.
        self._base_id = None
        # Internal variable for the version info of the module.
        self._version_info = None
        # Should new messages be learned automatically? Defaults to True.
        # TODO: Not sure if we should use CO_WR_LEARNMODE??
        self.teach_in = teach_in

    def _get_from_send_queue(self) -> Union[Packet, None]:
        """ Get message from send queue, if one exists """
        try:
            packet = self.transmit.get(block=False)
            return packet
        except queue.Empty:
            pass
        return None

    def send(self, packet: Packet) -> bool:
        LOGGER.debug(f'sending: {packet}')
        if not isinstance(packet, Packet):
            LOGGER.error('Object to send must be an instance of Packet')
            return False
        self.transmit.put(packet)
        return True

    def stop(self) -> None:
        self._stop_flag.set()

    def parse(self) -> Union[None, PARSE_RESULT]:
        """ Parses messages and puts them to receive queue """
        # Loop while we get new messages
        while True:
            status, self._buffer, packet = Packet.parse_msg(self._buffer)
            # If message is incomplete -> break the loop
            if status == PARSE_RESULT.INCOMPLETE:
                return status

            # If message is OK, add it to receive queue or send to the callback method
            if status == PARSE_RESULT.OK and packet:
                packet.received = datetime.datetime.now()

                if isinstance(packet, UTETeachInPacket) and self.teach_in:
                    response_packet = packet.create_response_packet(self.base_id)
                    LOGGER.info('Sending response to UTE teach-in.')
                    self.send(response_packet)

                LOGGER.debug(f"received: {packet}")
                if self.__callback is None:
                    self.receive.put(packet)
                else:
                    self.__callback(packet)

    @property  # getter
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, callback):
        self.__callback = callback

    @property
    def base_id(self) -> Union[None, list[int, int, int, int]]:
        """ Fetches Base ID from the transmitter, if required. Otherwise, returns the currently set Base ID. """
        # If base id is already set, return it.
        if self._base_id is not None:
            return self._base_id

        start = datetime.datetime.now()

        # Send COMMON_COMMAND 0x08, CO_RD_IDBASE request to the module
        self.send(Packet(PACKET.COMMON_COMMAND, data=[COMMON_COMMAND.CO_RD_IDBASE.value], optional=[]))

        # wait at most 1 second for the response
        while True:
            seconds_elapsed = (datetime.datetime.now() - start).total_seconds()
            if seconds_elapsed > 1:
                self.logger.error("Could not obtain base id from module within 1 second (timeout).")
                break
            try:
                packet = self.receive.get(block=True, timeout=0.1)
                # We're only interested in responses to the request in question.
                if (
                    packet.packet_type == PACKET.RESPONSE
                    and packet.response == RETURN_CODE.OK
                    and len(packet.response_data) == 4
                ):
                    # Base ID is set in the response data.
                    self._base_id = packet.response_data
                    # Put packet back to the Queue, so the user can also react to it if required...
                    self.receive.put(packet)
                    break
                # Put other packets back to the Queue.
                self.receive.put(packet)
            except queue.Empty:
                continue
        # Return the current Base ID (might be None).
        return self._base_id

    @base_id.setter
    def base_id(self, base_id: list[int, int, int, int]):
        """ Sets the Base ID manually, only for testing purposes. """
        self._base_id = base_id

    @property 
    def chip_id(self):
        ''' Fetches Chip ID from the transmitter, if required. Otherwise returns the currently set Chip ID. '''
        if self.version_info is not None:
            return self.version_info.chip_id
        
        return None

    @property
    def version_info(self):
        ''' Fetches version info from the transmitter, if required. Otherwise returns the currently set version info. '''

        # If version info is already set, return it.
        if self._version_info is not None:
            return self._version_info

        start = datetime.datetime.now()

        # Send COMMON_COMMAND 0x03, CO_RD_VERSION request to the module
        self.send(Packet(PACKET.COMMON_COMMAND, data=[COMMON_COMMAND.CO_RD_VERSION.value], optional=[]))

        # wait at most 1 second for the response
        while True:
            seconds_elapsed = (datetime.datetime.now() - start).total_seconds()
            if seconds_elapsed > 1:
                LOGGER.warning("Could not obtain version info from module within 1 second (timeout).")
                break

            try:
                packet = self.receive.get(block=True, timeout=0.1)
                if packet.packet_type == PACKET.RESPONSE and packet.response == RETURN_CODE.OK and len(packet.response_data) == 32: 
                    # interpret the version info
                    self._version_info: VersionInfo = VersionInfo()
                    res = packet.response_data

                    self._version_info.app_version.main = res[0]
                    self._version_info.app_version.beta = res[1]
                    self._version_info.app_version.alpha = res[2]
                    self._version_info.app_version.build = res[3]

                    self._version_info.api_version.main = res[4]
                    self._version_info.api_version.beta = res[5]
                    self._version_info.api_version.alpha = res[6]
                    self._version_info.api_version.build = res[7]
                    
                    self._version_info.chip_id = [
                        res[8], res[9], res[10], res[11]
                    ]
                    self._version_info.chip_version = int.from_bytes(res[12:15], 'big')

                    self._version_info.app_description = bytearray(res[16:32]).decode('utf8').strip()

                    # Put packet back to the Queue, so the user can also react to it if required...
                    self.receive.put(packet)
                    break
                # Put other packets back to the Queue.
                self.receive.put(packet)
            except queue.Empty:
                continue
        # Return the current version info (might be None).        
        return self._version_info

