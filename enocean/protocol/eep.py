# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
import logging
from sys import version_info
from collections import OrderedDict
from bs4 import BeautifulSoup

import enocean.utils
from enocean.protocol.constants import RORG


class EEP(object):
    logger = logging.getLogger('enocean.protocol.eep')

    def __init__(self):
        self.init_ok = False
        self.telegrams = {}

        try:
            if version_info[0] > 2:
                with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'EEP.xml'), 'r', encoding='UTF-8') as xml_file:
                    self.soup = BeautifulSoup(xml_file.read(), "html.parser")
            else:
                with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'EEP.xml'), 'r') as xml_file:
                    self.soup = BeautifulSoup(xml_file.read(), "html.parser")
            self.init_ok = True
            self.__load_xml()
        except IOError:
            # Impossible to test with the current structure?
            # To be honest, as the XML is included with the library,
            # there should be no possibility of ever reaching this...
            self.logger.warn('Cannot load protocol file!')
            self.init_ok = False

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

    @staticmethod
    def _get_raw(source, bitarray):
        ''' Get raw data as integer, based on offset and size '''
        offset = int(source['offset'])
        size = int(source['size'])
        return int(''.join(['1' if digit else '0' for digit in bitarray[offset:offset + size]]), 2)

    @staticmethod
    def _set_raw(target, raw_value, bitarray):
        ''' put value into bit array '''
        offset = int(target['offset'])
        size = int(target['size'])
        for digit in range(size):
            bitarray[offset+digit] = (raw_value >> (size-digit-1)) & 0x01 != 0
        return bitarray

    @staticmethod
    def _get_rangeitem(source, raw_value):
        for rangeitem in source.find_all('rangeitem'):
            if raw_value in range(int(rangeitem.get('start', -1)), int(rangeitem.get('end', -1)) + 1):
                return rangeitem

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

        # Find value description.
        value_desc = source.find('item', {'value': str(raw_value)}) or self._get_rangeitem(source, raw_value)

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
            if target.find('item', {'value': value}) or self._get_rangeitem(target, value):
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

    @staticmethod
    def _set_boolean(target, data, bitarray):
        ''' set given value to target bit in bitarray '''
        bitarray[int(target['offset'])] = data
        return bitarray

    def find_profile(self, bitarray, eep_rorg, rorg_func, rorg_type, direction=None, command=None):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.init_ok:
            self.logger.warn('EEP.xml not loaded!')
            return None

        if eep_rorg not in self.telegrams.keys():
            self.logger.warn('Cannot find rorg in EEP!')
            return None

        if rorg_func not in self.telegrams[eep_rorg].keys():
            self.logger.warn('Cannot find func in EEP!')
            return None

        if rorg_type not in self.telegrams[eep_rorg][rorg_func].keys():
            self.logger.warn('Cannot find type in EEP!')
            return None

        profile = self.telegrams[eep_rorg][rorg_func][rorg_type]

        if command:
            # multiple commands can be defined, with the command id always in same location (per RORG-FUNC-TYPE).
            eep_command = profile.find('command', recursive=False)
            # If commands are not set in EEP, or command is None,
            # get the first data as a "best guess".
            if not eep_command:
                return profile.find('data', recursive=False)

            # If eep_command is defined, so should be data.command
            return profile.find('data', {'command': str(command)}, recursive=False)

        # extract data description
        # the direction tag is optional
        if direction is None:
            return profile.find('data', recursive=False)
        return profile.find('data', {'direction': direction}, recursive=False)

    def get_values(self, profile, bitarray, status):
        ''' Get keys and values from bitarray '''
        if not self.init_ok or profile is None:
            return [], {}

        output = OrderedDict({})
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
        if not self.init_ok or profile is None:
            return data, status

        for shortcut, value in properties.items():
            # find the given property from EEP
            target = profile.find(shortcut=shortcut)
            if not target:
                # TODO: Should we raise an error?
                self.logger.warning('Cannot find data description for shortcut %s', shortcut)
                continue

            # update bit_data
            if target.name == 'value':
                data = self._set_value(target, value, data)
            if target.name == 'enum':
                data = self._set_enum(target, value, data)
            if target.name == 'status':
                status = self._set_boolean(target, value, status)
        return data, status
