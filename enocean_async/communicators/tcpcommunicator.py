# -*- encoding: utf-8 -*-
import asyncio
import serial_asyncio
import logging
from enocean_async.communicators.communicator import Server
from enocean_async.protocol.packet import Packet, RadioPacket
from enocean_async.communicators.utils import Serial_to_Tcp
from functools import partial
from aioconsole import ainput

class TCPCommunicator():
    logger = logging.getLogger('enocean.communicators.TCPCommunicator')
    def __init__(self, host='', port=9637):
        self.host = host
        self.port = port
        self.loop = None
        self.server = None
    


    async def packet(self, recived):
        '''Override this async method to decide what to do with the packet recived by the TCPCommunicator'''
        self.logger.debug(recived)
        return 


    async def close(self):
        await ainput("Press a button to close the Server\n")
        self.server.close()
        self.loop.stop()
        

    def start(self):
        '''This method will start the Enocean gateway in another asynchronous thread.\n
        Call it to start the TCPCommunication'''
        self.loop = asyncio.get_event_loop()
        self.logger.info('TCPCommunicator started')
        Gateway = partial (Server, self.packet, self.loop, self.logger)
        self.server = self.loop.create_server(Gateway,host=self.host, port= self.port)
        self.loop.create_task(self.server)
        self.loop.create_task(self.close())
        self.loop.run_forever()
        self.loop.close()
   
        

