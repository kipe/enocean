# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from bs4 import BeautifulSoup

path = os.path.dirname(os.path.realpath(__file__))


class EEP(object):
    def __init__(self):
        self.ok = False
        try:
            with open(os.path.join(path, 'EEP_2.6.1.xml'), 'r') as f:
                self.soup = BeautifulSoup(f.read())
            self.ok = True
        except IOError:
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

    def find_profile(self, rorg, func, type):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.ok:
            return None, None

        rorg = self.soup.find('telegram', {'rorg': self._get_hex(rorg)})
        if not rorg:
            return None, None

        func = rorg.find('profiles', {'func': self._get_hex(func)})
        if not func:
            return None, None

        profile = rorg.find('profile', {'type': self._get_hex(type)})
        data_description = profile.find('data')
        if not data_description:
            data_description = []

        return profile, data_description

    def get_values(self, rorg, func, type, data):
        ''' Get keys and values from data, matching RORG, FUNC and TYPE '''
        if not self.ok:
            return [], {}

        profile, data_description = self.find_profile(rorg, func, type)
        if not profile or not data_description:
            return [], {}

        output = {}
        for d in data_description.contents:
            if not d.name:
                continue
            if d.name == 'value':
                output.update(self._get_value(d, data))
            if d.name == 'enum':
                output.update(self._get_enum(d, data))
        return output.keys(), output
