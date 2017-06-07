#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.communicators.utils import send_to_tcp_socket
# from enocean.communicators.utils import send_to_udp_socket # When you want to use UDP
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue

init_logging()
communicator = SerialCommunicator()
communicator.start()
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.receive.get(block=True, timeout=1)
        send_to_tcp_socket('localhost', 9637, packet)
        # send_to_udp_socket('localhost', 9637, packet) # sending with UDP
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
