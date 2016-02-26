# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
import socket

from enocean.communicators.communicator import Communicator


class TCPCommunicator(Communicator):
    ''' Socket communicator class for EnOcean radio '''
    logger = logging.getLogger('enocean.communicators.TCPCommunicator')

    def __init__(self, host='', port=9637):
        super(TCPCommunicator, self).__init__()
        self.host = host
        self.port = port

        self.logger.info('TCPCommunicator started')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(0.5)

    def _receive(self):
        try:
            (client, addr) = self.sock.accept()
        except socket.timeout:
            return

        self.logger.debug('Client "%s" connected' % (addr))
        client.settimeout(0.5)

        try:
            data = client.recv(2048)
        except socket.timeout:
            return
        if not data:
            return
        self._buffer.extend(bytearray(data))

        client.close()
        self.logger.debug('Client disconnected')

    def _transmit(self, packet):
        pass

    def stop(self):
        self.sock.close()
        self.logger.info('TCPCommunicator stopped')
        super(TCPCommunicator, self).stop()
