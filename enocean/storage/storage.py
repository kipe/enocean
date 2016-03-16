# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
import json
import errno
import logging
import enocean.utils
from enocean.storage.device import Device
from enocean.storage.enoceanencoder import EnOceanEncoder


class Storage(object):
    ''' Implements storage of devices '''
    __version__ = 1
    logger = logging.getLogger('enocean.storage.storage')

    def __init__(self, location=None):
        ''' Loads storage from set location, defaulting to ~/.config/enocean/storage.json '''
        if location is None:
            location = '~/.config/enocean/storage.json'
        self.location = os.path.abspath(os.path.expanduser(location))
        self.load()

    @property
    def version(self):
        ''' Retrieves current storage version. '''
        return self.data.get('version', self.__version__)

    @property
    def used_offsets(self):
        ''' Gets the used offsets from Storage. '''
        return self.data.get('used_transmitter_offsets', [])

    @used_offsets.setter
    def used_offsets(self, value):
        '''
        Sets a list of used transmitter offsets.
        If value is not a list, raises ValueError.
        '''
        if not isinstance(value, list):
            raise ValueError('Storage.used_offsets value must be a list.')
        self.data['used_transmitter_offsets'] = value

    def add_to_used_offsets(self, value):
        '''
        Adds value to used offsets.
        If offset value is not in range 0-127, raises ValueError.
        '''
        if not isinstance(value, int) or value < 0 or value > 127:
            raise ValueError('offset value must be an integer in the range 0 - 127.')

        if value not in self.data['used_transmitter_offsets']:
            self.data['used_transmitter_offsets'].append(value)

    def remove_from_used_offsets(self, value):
        ''' Removes value from used offsets. '''
        try:
            self.data['used_transmitter_offsets'].remove(value)
        except (ValueError, KeyError):
            pass

    @property
    def next_offset(self):
        '''
        Points to next unused offset.
        If no offset is available, raises ValueError.
        '''
        used_offsets = self.used_offsets
        for i in range(0, 128):
            if i in used_offsets:
                continue
            return i
        raise ValueError('No offsets available.')

    def load(self):
        ''' Loads data from storage. '''
        self.logger.debug('Loading storage')
        self.data = {
            'storage_version': self.__version__,
            'used_transmitter_offsets': [],
            'devices': {},
        }

        if not os.path.exists(self.location):
            return self.data

        with open(self.location, 'r') as file_handle:
            self.data.update(**json.loads(file_handle.read()))
            self.data['devices'] = {
                device_id: Device(**device_data)
                for device_id, device_data in self.data.get('devices', {}).items()
            }
        # Convert storage versions here, if needed.
        # To be implemented if (and when) needed.
        # Something like:
        #
        #   import enocean.storage.convert_storage
        #   while self.version != self.__version__:
        #       self.data = getattr(enocean.storage.convert_storage, 'convert_%i_to_%i' % (self.version, self.version + 1))(self.data)
        #
        return self.data

    def save(self):
        ''' Saves data to storage. '''
        self.logger.debug('Saving storage')
        # If location doesn't exist
        if not os.path.exists(self.location):
            try:
                # Try to create the directories
                os.makedirs(os.path.dirname(self.location), mode=0o755)
            except OSError as exception:
                # If the directories already exist, it's OK
                # Otherwise, raise the exception.
                if exception.errno != errno.EEXIST:
                    raise

        with open(self.location, 'w') as file_handle:
            file_handle.write(json.dumps(self.data, cls=EnOceanEncoder))

    def wipe(self):
        ''' Wipes data from storage, removing everything. '''
        self.logger.warning('Wiping storage')
        try:
            os.unlink(self.location)
        except OSError as exception:
            # If file is not found, it's OK
            if exception.errno == errno.ENOENT:
                pass
            # Otherwise, re-raise the exception.
            else:
                raise
        self.load()

    @property
    def devices(self):
        ''' Returns a dictionary containing all devices. '''
        return self.data.get('devices', {})

    def load_device(self, device_id):
        '''
        Loads device from Storage by device id.
        Input:
            - device id (as an list of integers or hex-string)
        If found, returns Device
        If not found, raises KeyError.
        '''
        if isinstance(device_id, list):
            device_id = enocean.utils.to_hex_string(device_id)

        try:
            return self.data.get('devices', {})[device_id]
        except KeyError:
            raise KeyError('No device found with ID "%s"' % (device_id))

    def save_device(self, device):
        '''
        Saves device to Storage.
        If device is not a Device, raises ValueError.
        '''
        if not isinstance(device, Device):
            raise ValueError('device must be an instance of enocean.storage.Device')

        if 'devices' not in self.data:
            self.data['devices'] = {}

        if device.hex_id not in self.data['devices']:
            self.logger.info('New device with ID "%s" found.' % (device.hex_id))

        self.data['devices'][device.hex_id] = device
        if isinstance(device.transmitter_offset, int):
            self.add_to_used_offsets(device.transmitter_offset)
        self.save()

    def remove_device(self, device_id):
        '''
        Removes device from Storage by device id.
        Input:
            - device id (as an list of integers or hex-string)
        If not found, raises KeyError.
        '''
        if isinstance(device_id, list):
            device_id = enocean.utils.to_hex_string(device_id)

        try:
            del self.data['devices'][device_id]
            self.save()
        except KeyError:
            raise KeyError('No device found with ID "%s"' % (device_id))
