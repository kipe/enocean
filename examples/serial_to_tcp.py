#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import queue
import sys
import traceback

from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.communicators.utils import send_to_tcp_socket
from enocean.consolelogger import init_logging

init_logging()
communicator = SerialCommunicator()
communicator.start()
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.receive.get(block=True, timeout=1)
        send_to_tcp_socket('localhost', 9637, packet)
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
