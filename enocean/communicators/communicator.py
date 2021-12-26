# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
import datetime

import threading
try:
    import queue
except ImportError:
    import Queue as queue
from enocean.protocol.packet import Packet, UTETeachInPacket
from enocean.protocol.constants import PACKET, PARSE_RESULT, RETURN_CODE


class Communicator(threading.Thread):
    '''
    Communicator base-class for EnOcean.
    Not to be used directly, only serves as base class for SerialCommunicator etc.
    '''
    logger = logging.getLogger('enocean.communicators.Communicator')

    def __init__(self, callback=None, teach_in=True, get_base_id=True):
        super(Communicator, self).__init__()
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
        # Should new messages be learned automatically? Defaults to True.
        # TODO: Not sure if we should use CO_WR_LEARNMODE??
        self.teach_in = teach_in
        # Keep track if parsing started ok
        self.parse_started = threading.Event()
        # Should we try to get base id in init?
        self.get_base_id = get_base_id
        if get_base_id:
            # Ask for base_id, put as first packet in transmit buffer, wait for answer in parse loop
            self.send(Packet(PACKET.COMMON_COMMAND, data=[0x08]))
        else:
            # Starting without base_id, set parsing started flag now
            self.parse_started.set()

    def _get_from_send_queue(self):
        ''' Get message from send queue, if one exists '''
        try:
            packet = self.transmit.get(block=False)
            self.logger.info('Sending packet')
            self.logger.debug(packet)
            return packet
        except queue.Empty:
            pass
        return None

    def send(self, packet):
        if not isinstance(packet, Packet):
            self.logger.error('Object to send must be an instance of Packet')
            return False
        self.transmit.put(packet)
        return True

    def start(self):
        ''' Try to start parsing '''
        super(Communicator, self).start()
        # wait for parse to start
        started_ok = self.parse_started.wait(5)
        if not started_ok:
            # Failed, stop parsing
            self.logger.error('Communicator failed to start in time, stopping Communicator.')
            self.stop()
            return False
        return True

    def stop(self):
        self._stop_flag.set()

    def parse(self):
        ''' Parses messages and puts them to receive queue '''
        # Loop while we get new messages
        while True:
            status, self._buffer, packet = Packet.parse_msg(self._buffer)
            # If message is incomplete -> break the loop
            if status == PARSE_RESULT.INCOMPLETE:
                return status

            # If message is OK, add it to receive queue or send to the callback method
            if status == PARSE_RESULT.OK and packet:
                packet.received = datetime.datetime.now()

                if not self.parse_started.is_set():
                    # Put packet in receive buffer
                    self.receive.put(packet)
                    # look for response packet with base id
                    if packet.packet_type == PACKET.RESPONSE and packet.response == RETURN_CODE.OK and len(packet.response_data) == 4:  # noqa: E501
                        # Base ID is set with the response data, if not already set
                        if self._base_id is None:
                            self._base_id = packet.response_data
                            self.logger.info('Base ID: {}'.format(''.join('{:02X}'.format(x) for x in self._base_id)))
                    if self._base_id is not None:
                        self.parse_started.set()
                        self.logger.debug('Parsing started.')
                        if self.__callback is not None:
                            # Send receive queue to callback
                            while not self.receive.empty:
                                packet_from_queue = self.receive.get(block=False)
                                self.__callback(packet_from_queue)
                else:
                    if isinstance(packet, UTETeachInPacket) and self.teach_in:
                        if self.base_id is None:
                            self.logger.warning('Sending response to UTE teach-in failed, no base_id set.')
                        else:
                            response_packet = packet.create_response_packet(self.base_id)
                            self.logger.info('Sending response to UTE teach-in.')
                            self.send(response_packet)

                    if self.__callback is None:
                        self.receive.put(packet)
                    else:
                        self.__callback(packet)
                    self.logger.debug(packet)

    @property
    def base_id(self):
        return self._base_id

    @base_id.setter
    def base_id(self, base_id):
        ''' Sets the Base ID manually, only for testing purposes. '''
        self._base_id = base_id
        self.logger.info('Base ID (set manually): {}'.format(''.join('{:02X}'.format(x) for x in self._base_id)))

