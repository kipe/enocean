# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import socket
# import array


def send_to_tcp_socket(host, port, packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(str(bytearray(packet.build())))
    s.close()
