#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from enocean_async.consolelogger import init_logging
from enocean_async.communicators.serialcommunicator import SerialCommunicator


class USB300DB(SerialCommunicator):
    async def packet(self, packet):
        self.loop.create_task(self.send_to_tcp_socket('localhost', 9637, packet))
        return


def main():
    init_logging()
    Gateway = USB300DB()
    Gateway.start()

    EXIT = False
    while EXIT is not True:
        e =input("PRESS E TO EXIT\n")
        if e == 'E' or e == 'e':
            EXIT = True

    Gateway.stop()

if __name__ == "__main__" :
    main()