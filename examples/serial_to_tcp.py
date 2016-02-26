#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.communicators.utils import send_to_tcp_socket
import sys
import traceback

init_logging()
communicator = SerialCommunicator()
communicator.start()
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.get_packet()
        if packet is None:
            continue
        send_to_tcp_socket('localhost', 9637, packet)
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
