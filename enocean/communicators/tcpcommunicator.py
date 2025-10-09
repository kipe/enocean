# -*- encoding: utf-8 -*-

import logging
import socket

from .communicator import Communicator

LOGGER = logging.getLogger('enocean.communicators.TCPCommunicator')


class TCPCommunicator(Communicator):
    """ Socket communicator class for EnOcean radio """

    def __init__(self, host: str = '', port: int = 9637, loglevel=logging.NOTSET) -> None:
        super().__init__(loglevel=loglevel)
        LOGGER.setLevel(loglevel)
        self.host = host
        self.port = port

    def run(self) -> None:
        LOGGER.info('TCPCommunicator started')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        sock.settimeout(0.5)

        while not self._stop_flag.is_set():
            try:
                (client, addr) = sock.accept()
            except socket.timeout:
                continue
            LOGGER.debug(f'Client "{addr}" connected')
            client.settimeout(0.5)
            while True and not self._stop_flag.is_set():
                try:
                    data = client.recv(2048)
                except socket.timeout:
                    break
                if not data:
                    break
                self._buffer.extend(bytearray(data))
            self.parse()
            client.close()
            LOGGER.debug('Client disconnected')
        sock.close()
        LOGGER.info('TCPCommunicator stopped')
