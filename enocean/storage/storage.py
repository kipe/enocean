# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
import json
import errno
import logging
import enocean.utils


class Storage(object):
    ''' Implements storage of devices '''
    __version__ = 1
    logger = logging.getLogger('enocean.storage.storage')

    def __init__(self, location=None):
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
        ''' Sets a list of used transmitter offsets '''
        if isinstance(value, list):
            self.data['used_transmitter_offsets'] = value
        raise ValueError('Storage.used_offsets value must be a list.')

    def add_to_used_offsets(self, value):
        ''' Adds value to used offsets. '''
        if not isinstance(value, int) or value < 0 or value > 127:
            raise ValueError('offset value must be an integer in the range 0 - 127.')

        if 'used_transmitter_offsets' not in self.data:
            self.data['used_transmitter_offsets'] = []

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
        if not os.path.exists(self.location):
            self.data = {
                'storage_version': self.__version__,
                'used_transmitter_offsets': [],
                'devices': {},
            }
            return {}

        with open(self.location, 'r') as f:
            self.data = json.loads(f.read())
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
                os.makedirs(os.path.dirname(self.location), mode=0755)
            except OSError as exception:
                # If the directories already exist, it's OK
                if exception.errno == errno.EEXIST:
                    pass
                # Otherwise, re-raise the exception.
                else:
                    raise

        with open(self.location, 'w') as f:
            f.write(json.dumps(self.data))

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
        If found, returns an dictionary containing (at least):
            - id (as a list of integers)
            - eep_rorg (integer)
            - eep_func (integer or None)
            - eep_type (integer or None)
            - transmitter_offset (integer or None)
        If not found, returns None.
        '''
        if isinstance(device_id, list):
            device_id = enocean.utils.to_hex_string(device_id)

        device = self.data.get('devices', {}).get(device_id, None)
        if device is None:
            self.logger.warning('No device found with ID "%s"' % (device_id))
            return None

        device['device_id'] = enocean.utils.from_hex_string(device_id)
        device['eep_rorg'] = enocean.utils.from_hex_string(device.get('eep_rorg', '0x00'))
        device['eep_func'] = None if device.get('eep_func', None) is None else enocean.utils.from_hex_string(device['eep_func'])
        device['eep_type'] = None if device.get('eep_type', None) is None else enocean.utils.from_hex_string(device['eep_type'])
        device['transmitter_offset'] = None if device.get('transmitter_offset', None) is None else device['transmitter_offset']

        return device

    def save_device(self, device_id, eep_rorg, eep_func=None, eep_type=None, transmitter_offset=None):
        '''
        Saves device to Storage.
        Required arguments are:
            - device_id (as an list of integers or hex-string)
            - eep_rorg (as an integer or hex-string)
        Optional arguments are:
            - eep_func (as an integer or hex-string)
            - eep_type (as an integer or hex-string)
            - transmitter_offset (as an integer)
        '''
        # TODO: Possibly add additional storage as **kwargs?
        if isinstance(device_id, list):
            device_id = enocean.utils.to_hex_string(device_id)
        if isinstance(eep_rorg, int):
            eep_rorg = enocean.utils.to_hex_string(eep_rorg)
        if isinstance(eep_func, int):
            eep_func = enocean.utils.to_hex_string(eep_func)
        if isinstance(eep_type, int):
            eep_type = enocean.utils.to_hex_string(eep_type)

        if 'devices' not in self.data:
            self.data['devices'] = {}
        if device_id not in self.data['devices']:
            self.data['devices'][device_id] = {}

        self.data['devices'][device_id] = {
            'eep_rorg': eep_rorg,
            'eep_func': eep_func,
            'eep_type': eep_type,
            'transmitter_offset': None if not isinstance(transmitter_offset, int) else transmitter_offset,
        }
        if isinstance(transmitter_offset, int):
            self.add_to_used_offsets(transmitter_offset)
        self.logger.info('Device with ID "%s" saved' % (device_id))
        self.save()

    def remove_device(self, device_id):
        '''
        Removes device from Storage by device id.
        Input:
            - device id (as an list of integers or hex-string)
        '''
        if isinstance(device_id, list):
            device_id = enocean.utils.to_hex_string(device_id)
        try:
            del self.data['devices'][device_id]
            self.save()
        except KeyError:
            self.logger.warning('No device found with ID "%s"' % (device_id))
