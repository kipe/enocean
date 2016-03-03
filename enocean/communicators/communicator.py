# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
import os
import threading
try:
    import queue
except ImportError:
    import Queue as queue
from enocean.protocol.packet import Packet, RadioPacket, UTETeachIn
from enocean.protocol.constants import PACKET, PARSE_RESULT, RETURN_CODE
from enocean.storage import Storage, Device


class Communicator(threading.Thread):
    '''
    Communicator base-class for EnOcean.
    Not to be used directly, only serves as base class for SerialCommunicator etc.
    '''
    logger = logging.getLogger('enocean.communicators.Communicator')

    # TODO: Stupid, ugly hack to disable storage during testing.
    def __init__(self, callback=None, teach_in=True, use_storage=True if os.environ.get('ENOCEAN_TESTING', None) else False, storage_location=None):
        super(Communicator, self).__init__()
        # Create an event to stop the thread
        self._stop_flag = threading.Event()
        # Input buffer
        self._buffer = []
        # Setup packet queues
        self.transmit = queue.PriorityQueue()
        self.receive = queue.Queue()
        # Set the callback method
        self.__callback = callback
        # Internal variable for the Base ID of the module.
        self._base_id = None
        # Should new messages be learned automatically? Defaults to True.
        # TODO: Not sure if we should use CO_WR_LEARNMODE??
        self.teach_in = teach_in

        # Initialize Storage
        # TODO: Should really initialize with Storage-object, but not accept any new devices...
        self.storage = None
        if use_storage:
            self.storage = Storage(storage_location)

    def _get_from_send_queue(self):
        ''' Get message from send queue, if one exists '''
        try:
            priority, packet = self.transmit.get(block=False)
            self.logger.info('Sending packet')
            self.logger.debug(packet)
            return packet
        except queue.Empty:
            pass
        return None

    def _receive(self):
        ''' Receive messages from the device, to be implemented in the child class. '''
        raise NotImplementedError

    def _transmit(self, packet):
        ''' Transmit messages with the device, to be implemented in the child class. '''
        raise NotImplementedError

    def run(self):
        '''
        Main loop for communicator.
        Calls _receive() and _transmit() from the child class to receive and send messages.
        '''
        while not self._stop_flag.is_set():
            # If there's messages in transmit queue, send them
            while True:
                packet = self._get_from_send_queue()
                if not packet:
                    break
                self._transmit(packet)
            # Read new messages from the device.
            self._receive()
            self.parse()

    def get_packet(self, block=True, timeout=1):
        '''
        Fetches packet from receive queue.
        Optional arguments are the same as in Queue.get().
        https://docs.python.org/2/library/queue.html#Queue.Queue.get
        '''
        # TODO: change to PriorityQueue in v0.5.
        try:
            return self.receive.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def send(self, packet, priority=100):
        ''' Adds a packet to the transmit queue. '''
        if not isinstance(packet, Packet):
            self.logger.error('Object to send must be an instance of Packet')
            return False
        self.transmit.put((priority, packet))
        return True

    def stop(self):
        ''' Stops the communicator. '''
        self._stop_flag.set()

    def parse(self):
        ''' Parses messages and puts them to receive queue '''
        # Loop while we get new messages
        while True:
            status, self._buffer, packet = Packet.parse_msg(self._buffer)
            # If message is incomplete -> break the loop
            if status == PARSE_RESULT.INCOMPLETE:
                return status

            # If message is OK, add it to receive queue or send to the callback method
            if status == PARSE_RESULT.OK and packet:
                # Send automatic responses to UTETeachIn -packets.
                if isinstance(packet, UTETeachIn):
                    if not self.teach_in:
                        self.logger.info('Communicator not set to teach-in mode, not sending UTE teach-in response.')
                    else:
                        self.logger.info('Sending response to UTE teach-in.')
                        self.send(packet.create_response_packet(self.base_id), priority=0)
                        packet.response_sent = True

                self.store_device(packet)

                # TODO: Prioritize packages, once receive is changed to PriorityQueue
                if self.__callback is None:
                    self.receive.put(packet)
                else:
                    self.__callback(packet)
                self.logger.debug(packet)

    def store_device(self, packet):
        ''' Save device to storage, if all conditions are met. '''
        if self.storage is None:
            return
        if self.teach_in is False:
            return
        if not isinstance(packet, RadioPacket):
            return
        if not packet.learn:
            return

        try:
            device = self.storage.load_device(device_id=packet.sender)
            # If device is found, update the data we're likely to get from the teach_in.
            device.update({
                'eep_rorg': packet.rorg,
                'eep_func': packet.rorg_func,
                'eep_type': packet.rorg_type,
                'manufacturer_id': packet.rorg_manufacturer,
            })
            self.storage.save_device(device)
        except KeyError:
            # If device is not found, create a new device.
            self.storage.save_device(
                Device(
                    id=packet.sender,
                    eep_rorg=packet.rorg,
                    eep_func=packet.rorg_func,
                    eep_type=packet.rorg_type,
                    manufacturer_id=packet.rorg_manufacturer
                )
            )

    @property
    def base_id(self):
        ''' Fetches Base ID from the transmitter, if required. Otherwise returns the currently set Base ID. '''
        # If base id is already set, return it.
        if self._base_id is not None:
            return self._base_id

        # Send COMMON_COMMAND 0x08, CO_RD_IDBASE request to the module
        self.send(Packet(PACKET.COMMON_COMMAND, data=[0x08]))
        # Loop over 10 times, to make sure we catch the response.
        # Thanks to timeout, shouldn't take more than a second.
        # Unfortunately, all other messages received during this time are ignored.
        for i in range(0, 10):
            try:
                packet = self.receive.get(block=True, timeout=0.1)
                # We're only interested in responses to the request in question.
                if packet.packet_type == PACKET.RESPONSE and packet.response == RETURN_CODE.OK and len(packet.response_data) == 4:
                    # Base ID is set in the response data.
                    self._base_id = packet.response_data
                    # Put packet back to the Queue, so the user can also react to it if required...
                    self.receive.put(packet)
                    break
                # Put other packets back to the Queue.
                self.receive.put(packet)
            except queue.Empty:
                continue
        # Return the current Base ID (might be None).
        return self._base_id

    @base_id.setter
    def base_id(self, base_id):
        ''' Sets the Base ID manually, only for testing purposes. '''
        self._base_id = base_id
