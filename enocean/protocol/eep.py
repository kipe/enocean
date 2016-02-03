# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from bs4 import BeautifulSoup
import logging
from enocean.protocol.constants import RORG

logger = logging.getLogger('enocean.protocol.eep')

path = os.path.dirname(os.path.realpath(__file__))


class EEP(object):
    _data_description = None

    def __init__(self):
        self.ok = False
        try:
            with open(os.path.join(path, 'EEP.xml'), 'r') as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
            self.ok = True
        except IOError:
            logger.warn('Cannot load protocol file!')
            pass

    def _get_hex(self, nmb):
        ''' Get hex-representation of number '''
        return '0x%02X' % (nmb)

    def _get_raw(self, source, bitarray):
        ''' Get raw data as integer, based on offset and size '''
        offset = int(source['offset'])
        size = int(source['size'])
        return int(''.join(['1' if digit else '0' for digit in bitarray[offset:offset + size]]), 2)

    def _get_value(self, source, bitarray):
        ''' Get value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)

        rng = source.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)

        scl = source.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)

        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source['unit'],
                'value': (scl_max - scl_min) / (rng_max - rng_min) * (raw_value - rng_min) + scl_min,
                'raw_value': raw_value,
            }
        }

    def _get_enum(self, source, bitarray):
        ''' Get enum value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)
        value_desc = source.find('item', {'value': str(raw_value)})
        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source.get('unit', ''),
                'value': value_desc['description'],
                'raw_value': raw_value,
            }
        }

    def _get_boolean(self, source, bitarray):
        ''' Get boolean value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)
        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source.get('unit', ''),
                'value': True if raw_value else False,
                'raw_value': raw_value,
            }
        }

    def _set_raw(self, target, raw_value, bitarray):
        ''' put value into bit array '''
        offset = int(target['offset'])
        size = int(target['size'])
        for digit in range(size):
            bitarray[offset+digit] = (raw_value >> (size-digit-1)) & 0x01 != 0
        return bitarray

    def _set_value(self, target, value, bitarray):
        # derive raw value
        rng = target.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)
        scl = target.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)
        raw_value = (value - scl_min) * (rng_max - rng_min) / (scl_max - scl_min) + rng_min
        # store value in bitfield
        return self._set_raw(target, int(raw_value), bitarray)

    def _set_enum(self, target, value, bitarray):
        if isinstance(value, int):
            raise ValueError('No integers here, use the description string provided in EEP.')

        # derive raw value
        value_item = target.find('item', {'description': value})
        if value_item is None:
            raise ValueError('Enum description for value "%s" not found in EEP.' % (value))
        raw_value = int(value_item['value'])
        return self._set_raw(target, raw_value, bitarray)

    def _set_boolean(self, target, data, bitarray):
        bitarray[int(target['offset'])] = data
        return bitarray

    def find_profile(self, rorg, func, type, direction=None):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.ok:
            logging.warning("Not ready.")
            return False

        rorg = self.soup.find('telegram', {'rorg': self._get_hex(rorg)})
        if not rorg:
            logger.warn('Cannot find rorg in EEP!')
            return False

        func = rorg.find('profiles', {'func': self._get_hex(func)})
        if not func:
            logger.warn('Cannot find func in EEP!')
            return False

        profile = func.find('profile', {'type': self._get_hex(type)})
        if not profile:
            logger.warn('Cannot find type in EEP!')
            return False

        # extract data description
        # the direction tag is optional
        if direction is None:
            self._data_description = profile.find('data')
        else:
            self._data_description = profile.find('data', {'direction': direction})

        if not self._data_description:
            logger.warn('Cannot find data description in EEP!')
            self._data_description = []

        return True

    def get_values(self, bitarray, status):
        ''' Get keys and values from bitarray '''
        if not self.ok:
            return [], {}

        if not self._data_description:
            return [], {}

        output = {}
        for source in self._data_description.contents:
            if not source.name:
                continue
            if source.name == 'value':
                output.update(self._get_value(source, bitarray))
            if source.name == 'enum':
                output.update(self._get_enum(source, bitarray))
            if source.name == 'status':
                output.update(self._get_boolean(source, status))
        return output.keys(), output

    def set_values(self, rorg, data, status, properties):
        ''' Update data based on data contained in properties '''
        if not self.ok:
            return data, status

        if not self._data_description:
            return data, status

        for property, value in properties.items():
            # find the given property from EEP
            target = self._data_description.find(shortcut=property)
            if not target:
                logger.warning('Cannot find data description for shortcut %s', property)
                continue

            # update bit_data
            if target.name == 'value':
                data = self._set_value(target, value, data)
            if target.name == 'enum':
                data = self._set_enum(target, value, data)
            if target.name == 'status':
                if rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
                    status = self._set_boolean(target, value, status)
        return data, status
