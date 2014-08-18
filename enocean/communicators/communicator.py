# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging

import threading
try:
    import queue
except ImportError:
    import Queue as queue
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PARSE_RESULT

logger = logging.getLogger('enocean.communicators.Communicator')


class Communicator(threading.Thread):
    '''
    Communicator base-class for EnOcean.
    Not to be used directly, only serves as base class for SerialCommunicator etc.
    '''
    def __init__(self):
        super(Communicator, self).__init__()
        # Create an event to stop the thread
        self._stop = threading.Event()
        # Input buffer
        self._buffer = []
        # Setup packet queues
        self.transmit = queue.Queue()
        self.receive = queue.Queue()

    def _get_from_send_queue(self):
        ''' Get message from send queue, if one exists '''
        try:
            p = self.transmit.get(block=False)
            logger.info('Sending packet')
            logger.debug(p)
            return p
        except queue.Empty:
            pass
        return None

    def send(self, packet):
        if not isinstance(packet, Packet):
            logger.error('Object to send must be an instance of Packet')
            return False
        self.transmit.put(packet)
        return True

    def stop(self):
        self._stop.set()

    def parse(self):
        ''' Parses messages and puts them to receive queue '''
        # Loop while we get new messages
        while True:
            status, self._buffer, p = Packet.parse_msg(self._buffer)
            # If message is incomplete -> break the loop
            if status == PARSE_RESULT.INCOMPLETE:
                return status

            # If message is OK, add it to receive queue
            if status == PARSE_RESULT.OK and p:
                self.receive.put(p)
                logger.debug(p)
