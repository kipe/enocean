# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('enocean.protocol.eep')

path = os.path.dirname(os.path.realpath(__file__))


class EEP(object):
    _profile = None
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

    def _get_raw(self, value, bitarray):
        ''' Get raw data as integer, based on offset and size '''
        offset = int(value['offset'])
        size = int(value['size'])
        return int(''.join(['1' if digit else '0' for digit in bitarray[offset:offset + size]]), 2)

    def _get_value(self, value, data):
        ''' Get value, based on the data in XML '''
        raw_value = self._get_raw(value, data)

        rng = value.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)

        scl = value.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)

        return {
            value['shortcut']: {
                'description': value['description'],
                'unit': value['unit'],
                'value': (scl_max - scl_min) / (rng_max - rng_min) * (raw_value - rng_min) + scl_min,
                'raw_value': raw_value,
            }
        }

    def _get_enum(self, value, data):
        ''' Get enum value, based on the data in XML '''
        raw_value = self._get_raw(value, data)
        value_desc = value.find('item', {'value': str(raw_value)})
        return {
            value['shortcut']: {
                'description': value['description'],
                'unit': value.get('unit', ''),
                'value': value_desc['description'],
                'raw_value': raw_value,
            }
        }

    def _set_raw(self, value, raw_value, bitarray):
        ''' put value into bit array '''
        offset = int(value['offset'])
        size = int(value['size'])
        for digit in range(size):
            bitarray[offset+digit] = (raw_value >> (size-digit-1)) & 0x01 != 0

    def _set_value(self, value, data, bitarray):
        # derive raw value
        rng = value.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)
        scl = value.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)
        raw_value = (data - scl_min) * (rng_max - rng_min) / (scl_max - scl_min) + rng_min
        # store value in bitfield
        self._set_raw(value, int(raw_value), bitarray)

    def _set_enum(self, value, data, bitarray):
        # derive raw value
        value_item = value.find('item', {'description': data})
        raw_value = int(value_item['value'])
        # store value in bitfield
        self._set_raw(value, raw_value, bitarray)

    def find_profile(self, rorg, func, type):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.ok:
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

        # store identified profile
        self._profile = profile

        # extract data description
        self._data_description = self._profile.find('data')
        if not self._data_description:
            logger.warn('Cannot find data description in EEP!')
            self._data_description = []

        return True

    def get_values(self, data):
        ''' Get keys and values from data '''
        if not self.ok:
            return [], {}

        if not self._profile or not self._data_description:
            return [], {}

        output = {}
        for d in self._data_description.contents:
            if not d.name:
                continue
            if d.name == 'value':
                output.update(self._get_value(d, data))
            if d.name == 'enum':
                output.update(self._get_enum(d, data))
        return output.keys(), output

    def set_values(self, data, properties):
        ''' Update data based on data contained in properties '''
        if not self.ok:
            return [], {}

        if not self._profile or not self._data_description:
            return [], {}

        for cur_prop in properties:
            # check if given property is contained in EEP
            d = self._data_description.find_all(shortcut=cur_prop)
            if d:
                value = d[0]
                # update bit_data
                if value.name == 'value':
                    self._set_value(value, properties[cur_prop], data)
                if value.name == 'enum':
                    self._set_enum(value, properties[cur_prop], data)
            else:
                logger.warning('Cannot find data description for shortcut %s', cur_prop)
