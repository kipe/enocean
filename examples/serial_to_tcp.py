#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.communicators.utils import send_to_tcp_socket
import sys
import traceback

import Queue

init_logging()
c = SerialCommunicator()
c.start()
while c.is_alive():
    try:
        # Loop to empty the queue...
        p = c.receive.get(block=True, timeout=1)
        send_to_tcp_socket('localhost', 9637, p)
    except Queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if c.is_alive():
    c.stop()
