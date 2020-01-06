# -*- encoding: utf-8 -*-
import asyncio
import datetime
import logging
from enocean_async.protocol.packet import Packet, UTETeachInPacket, RadioPacket
from enocean_async.protocol.constants import PACKET, PARSE_RESULT, RETURN_CODE, RORG


class Communicator(asyncio.Protocol):
    '''Communicator class that implements the enocean protocol, 
    do not touch it directly, use insted SerialCommunicator 
    '''
    def __init__(self, packet_function, teachin_function, transport, send_function, base_id_function, loop, logger):
        '''packet_function: is the function that will be called everytime ther is a new packet of type Radio Recived\n
        teachin_function : is the function that will be callled everytime there is a new UTETeachInPacket\n
        transport : this function will store the type of transport\n
        base_id_function : this function will store the base_id of the communicator\n
        loop : this is the asynchronous EventLoop that will handle the enocean protocol\n
        communicator: this is the type of communicator, in our case it will be serial or tcp
        '''
        super().__init__()
        self.transport = None
        self._buffer = None
        self.packet = packet_function
        self.teachin = teachin_function
        self.set_transport = transport
        self.send = send_function
        self.set_base = base_id_function
        self.base_id = None
        self.loop = loop
        self.logger = logger



    def connection_made(self, transport):
        self.logger.info('Connected')
        self.set_transport(transport)
        self._buffer = bytes()
        self.send(Packet(PACKET.COMMON_COMMAND, data=[0x08]))
        return
        



    def data_received(self, data):
        self._buffer+= data
        status, self._buffer, packet = Packet.parse_msg(self._buffer)
        if status == PARSE_RESULT.OK and packet:
            self.loop.create_task(self.analize_data(packet))
            return
        return


    def connection_lost(self, exc):
        self.logger.warning('Connection lost')
        return


    async def send_response(self, packet):
        self.logger.info('Sending response to UTE teach-in.')
        response_packet = packet.create_response_packet(self.base_id)
        self.send(response_packet)
        return     
    

    async def analize_data(self, packet):
        packet.received = datetime.datetime.now()
        
        if packet.packet_type == PACKET.RESPONSE and packet.response == RETURN_CODE.OK and len(packet.response_data) == 4:
            self.set_base(packet.response_data)
            self.base_id = packet.response_data
            return
        
        if isinstance(packet, UTETeachInPacket):
            self.loop.create_task(self.send_response(packet))
            self.loop.create_task(self.teachin(packet))
            return

        if packet.packet_type == PACKET.RADIO:
            self.loop.create_task(self.packet(packet))
        return

    
class Server(asyncio.Protocol):
    '''Communicator class that implements the enocean protocol, 
    do not touch it directly, use insted SerialCommunicator 
    '''
    def __init__(self, packet_function, loop, logger):
        '''packet_function: is the function that will be called everytime ther is a new packet of type Radio Recived\n
        loop : this is the asynchronous EventLoop that will handle the enocean protocol\n
        communicator: this is the type of communicator, in our case it will be serial or tcp
        '''
        super().__init__()
        self.transport = None
        self.packet = packet_function
        self.loop = loop
        self.logger = logger
        self.transport = None



    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        self.logger.info('Connection from {}'.format(peername))
        self.transport = transport
        return
        



    def data_received(self, data):
        self._buffer = data
        status, self._buffer, packet = Packet.parse_msg(self._buffer)
        if status == PARSE_RESULT.OK and packet:
            self.logger.info('Close client socket')
            self.loop.create_task(self.packet(packet))
        return
    
    def connection_lost(self, exc):
        self.logger.warning('The server closed the connection')
        self.loop.stop()
