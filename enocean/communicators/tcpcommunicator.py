# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging
import socket

from enocean.communicators.communicator import Communicator

logger = logging.getLogger('enocean.communicators.TCPCommunicator')


class TCPCommunicator(Communicator):
    ''' Socket communicator class for EnOcean radio '''
    def __init__(self, host='', port=9637):
        super(TCPCommunicator, self).__init__()
        self.host = host
        self.port = port

    def run(self):
        logger.info('TCPCommunicator started')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        sock.settimeout(0.5)

        while not self._stop.is_set():
            try:
                (client, addr) = sock.accept()
            except socket.timeout:
                continue
            logger.debug('Client connected')
            client.settimeout(0.5)
            while True and not self._stop.is_set():
                try:
                    d = client.recv(2048)
                except socket.timeout:
                    break
                if not d:
                    break
                self._buffer.extend([ord(c) for c in d])
            self.parse()
            client.close()
            logger.debug('Client disconnected')
        sock.close()
        logger.info('TCPCommunicator stopped')
