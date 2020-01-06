#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from enocean_async.consolelogger import init_logging
from enocean_async.communicators.tcpcommunicator import TCPCommunicator
from enocean_async.protocol.constants import PACKET, RORG

class Server(TCPCommunicator):
    async def packet(self, packet):
        if packet.rorg == RORG.BS4:
            for k in packet.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, packet.parsed[k]))
            return
        if packet.rorg == RORG.BS1:
            for k in packet.parse_eep(0x00, 0x01):
                print('%s: %s' % (k, packet.parsed[k]))
            return
        if packet.rorg == RORG.RPS:
            for k in packet.parse_eep(0x02, 0x02):
                print('%s: %s' % (k, packet.parsed[k]))
            return


def main():
    init_logging()
    communicator = Server()
    communicator.start()


if __name__== "__main__":
    main()