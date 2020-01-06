# -*- encoding: utf-8 -*-
import asyncio
import serial_asyncio
import logging
from threading import Thread
from enocean_async.communicators.communicator import Communicator
from enocean_async.protocol.packet import Packet, RadioPacket, UTETeachInPacket
from enocean_async.communicators.utils import Serial_to_Tcp
from functools import partial



class SerialCommunicator():
    logger = logging.getLogger('enocean.communicators.SerialCommunicator')
    def __init__(self):
        self.baudrate = 57600
        self.port = '/dev/enocean'
        self.serial = None
        self.base_id = None
        self.thread = None
        self.loop = None
    


    async def packet(self, recived):
        '''Override this async method to decide what to do with the packet recived by the SerialCommunicator'''
        self.logger.debug(recived)
        return  



    async def teachin_packet(self, packet):
        '''Override this async method to decide what action do after reciving a teachin'''
        self.logger.debug(packet)
        return   



    def start(self):
        '''This method will start the Enocean gateway in another asynchronous thread.\n
        Call it to start the SerialCommunication'''
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.__start_loop, daemon=False)
        self.thread.start()
        return



    def __start_loop(self):
        '''Internal method.\n Do not call it directly'''
        self.logger.info('SerialCommunicator started')
        asyncio.set_event_loop(self.loop)
        Gateway = partial (Communicator, self.packet, self.teachin_packet, self.__serial, self.__write, self.__base_id, self.loop, self.logger)
        gateway = serial_asyncio.create_serial_connection(self.loop, Gateway, self.port, baudrate = self.baudrate)
        self.loop.create_task(gateway)
        self.loop.run_forever()
        tasks = asyncio.all_tasks(self.loop)
        for task in tasks:
            try:
                task.cancel()
            except:
                pass
        self.loop.close()
   
        
            
    async def __send_packet(self,packet):
        '''Internal method. Do not call it directly'''
        self.serial.write(packet)
        return



    def send(self, packet):
        '''This method will send asynchronously a packet throught the Enocean SerialCommunicator.\n
        This method can be called only outside the enocean eventloop.\n
        if the packet isn't an instance of Packet, it will create a log Error and return without sending the packet'''

        if not isinstance(packet, Packet):
            self.logger.error('Object to send must be an instance of Packet')
            return
        asyncio.run_coroutine_threadsafe(self.__send_packet(bytes(packet.build())), self.loop)
    
    

    def stop(self):
        '''This method will close the Serial connection of the Gatewa and close the eventloop that handles the enocean library
        after calling this method. If you want to start again the SerialCommunicator just call again SerialCommunicator.start() method'''
        self.loop.call_soon_threadsafe(self.serial.close)
        self.loop.call_soon_threadsafe( self.loop.stop)
        self.thread.join()
        self.logger.info('SerialCommunicator stopped')
        return 



    async def send_to_tcp_socket(self, Host, Port, packet):
        '''This is an asynchronous method used to send a packet to a tcp Socket. You can call it only inside another corutine of the asyncenocean library using
         self.loop.create_tasck(self.send_to_tcp_socket(Host, Port, packet)).\n If you want to call it outside a corutine , just call the method\n
         SerialCommunicator.send_to_tcp(Host, Port, packet).\n If the packet isn't an instance of Packet, it will create a log Error and return without sending the packet
         '''
        if not isinstance(packet, Packet):
            self.logger.error('Object to send must be an instance of Packet')
            return
        serial_to_tcp = partial(Serial_to_Tcp, packet)
        self.loop.create_task(self.loop.create_connection(serial_to_tcp, host=Host, port=Port))
        return
    


    def send_to_tcp(self, Host, Port, packet):
        '''This is an asynchronous method used to send a packet to a tcp Socket. This method can be called only outside the enocean eventloop.
         If the packet isn't an instance of Packet, it will create a log Error and return without sending the packet
        '''
        if not isinstance(packet, Packet):
            self.logger.error('Object to send must be an instance of Packet')
            return
        asyncio.run_coroutine_threadsafe(self.send_to_tcp_socket(Host, Port, packet), self.loop)



    def __serial(self, transport):
        '''Internal method. Do not call it directly'''
        self.serial = transport.serial
        return



    def __base_id(self, base_id):
        '''Internal method. Do not call it directly'''
        self.base_id = base_id
        return



    def __write(self, packet):
        '''Internal method. Do not call it directly'''
        self.serial.write(bytes(packet.build()))
        return

