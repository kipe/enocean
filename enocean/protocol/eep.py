# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
from bs4 import BeautifulSoup
import logging

import enocean.utils

logger = logging.getLogger('enocean.protocol.eep')

path = os.path.dirname(os.path.realpath(__file__))


class EEP(object):
    def __init__(self):
        self.ok = False
        self.telegrams = {}

        try:
            with open(os.path.join(path, 'EEP.xml'), 'r') as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
            self.ok = True
        except IOError:
            logger.warn('Cannot load protocol file!')

        if not self.ok:
            return
        self.__load_xml()

    def __load_xml(self):
        self.telegrams = {
            enocean.utils.from_hex_string(telegram['rorg']): {
                enocean.utils.from_hex_string(function['func']): {
                    enocean.utils.from_hex_string(type['type'], ): type
                    for type in function.find_all('profile')
                }
                for function in telegram.find_all('profiles')
            }
            for telegram in self.soup.find_all('telegram')
        }

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

    def _get_rangeitem(self, source, raw_value):
        for rangeitem in source.find_all('rangeitem'):
            if raw_value in range(int(rangeitem.get('start', -1)), int(rangeitem.get('end', -1)) + 1):
                return rangeitem

    def _get_enum(self, source, bitarray):
        ''' Get enum value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)

        # Try, if there's any rangeitems.
        value_desc = self._get_rangeitem(source, raw_value)
        if not value_desc:
            # If a matching rangeitem wasn't found, find a traditional item.
            value_desc = source.find('item', {'value': str(raw_value)})

        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source.get('unit', ''),
                'value': value_desc['description'].format(value=raw_value),
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
        ''' set given numeric value to target field in bitarray '''
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
        ''' set given enum value (by string or integer value) to target field in bitarray '''
        # derive raw value
        if isinstance(value, int):
            # check whether this value exists
            if target.find('item', {'value': value}):
                # set integer values directly
                raw_value = value
            else:
                raise ValueError('Enum value "%s" not found in EEP.' % (value))
        else:
            value_item = target.find('item', {'description': value})
            if value_item is None:
                raise ValueError('Enum description for value "%s" not found in EEP.' % (value))
            raw_value = int(value_item['value'])
        return self._set_raw(target, raw_value, bitarray)

    def _set_boolean(self, target, data, bitarray):
        ''' set given value to target bit in bitarray '''
        bitarray[int(target['offset'])] = data
        return bitarray

    def find_profile(self, bitarray, rorg, func, type, direction=None):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.ok:
            logger.warn('EEP.xml not loaded!')
            return None

        if rorg not in self.telegrams.keys():
            logger.warn('Cannot find rorg in EEP!')
            return None

        if func not in self.telegrams[rorg].keys():
            logger.warn('Cannot find func in EEP!')
            return None

        if type not in self.telegrams[rorg][func].keys():
            logger.warn('Cannot find func in EEP!')
            return None

        profile = self.telegrams[rorg][func][type]

        # For VLD; multiple commands can be defined, with the command id always in same location (per RORG-FUNC-TYPE).
        # If this is the case, find data by the command id.
        command = profile.find('command', recursive=False)
        if command:
            command = self._get_enum(command, bitarray).values()
            # If command wasn't found, the message isn't supported...
            if not command:
                return None
            return profile.find('data', {'command': list(command)[0].get('raw_value')}, recursive=False)

        # extract data description
        # the direction tag is optional
        if direction is None:
            return profile.find('data', recursive=False)
        return profile.find('data', {'direction': direction}, recursive=False)

    def get_values(self, profile, bitarray, status):
        ''' Get keys and values from bitarray '''
        if not self.ok or profile is None:
            return [], {}

        output = {}
        for source in profile.contents:
            if not source.name:
                continue
            if source.name == 'value':
                output.update(self._get_value(source, bitarray))
            if source.name == 'enum':
                output.update(self._get_enum(source, bitarray))
            if source.name == 'status':
                output.update(self._get_boolean(source, status))
        return output.keys(), output

    def set_values(self, profile, data, status, properties):
        ''' Update data based on data contained in properties '''
        if not self.ok or profile is None:
            return data, status

        for property, value in properties.items():
            # find the given property from EEP
            target = profile.find(shortcut=property)
            if not target:
                logger.warning('Cannot find data description for shortcut %s', property)
                continue

            # update bit_data
            if target.name == 'value':
                data = self._set_value(target, value, data)
            if target.name == 'enum':
                data = self._set_enum(target, value, data)
            if target.name == 'status':
                status = self._set_boolean(target, value, status)
        return data, status
