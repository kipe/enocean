# -*- encoding: utf-8 -*-
import asyncio
from enocean_async.protocol.packet import Packet, RadioPacket, UTETeachInPacket

class Serial_to_Tcp(asyncio.Protocol):
    def __init__(self, packet):
        self.packet = packet

    def connection_made(self, transport):
        transport.write(bytes(self.packet.build()))