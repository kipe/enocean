# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import enocean.utils


class Device(object):
    ''' Device -class to be used as part of the Storage. '''
    def __init__(self, id, **kwargs):
        self.id = enocean.utils.from_hex_string(id) if not isinstance(id, list) else id
        self.eep_rorg = self.__value_from_hex(kwargs.pop('eep_rorg', None))
        self.eep_func = self.__value_from_hex(kwargs.pop('eep_func', None))
        self.eep_type = self.__value_from_hex(kwargs.pop('eep_type', None))
        self.manufacturer_id = self.__value_from_hex(kwargs.pop('eep_rorg', None))
        self.transmitter_offset = self.__value_from_hex(kwargs.pop('transmitter_offset', None))
        self.update(**kwargs)

    def __repr__(self):
        return '<Device %s %s-%s-%s>' % (
            self.hex_id,
            enocean.utils.to_hex_string(self.eep_rorg) if self.eep_rorg is not None else None,
            enocean.utils.to_hex_string(self.eep_func) if self.eep_func is not None else None,
            enocean.utils.to_hex_string(self.eep_type) if self.eep_type is not None else None,
        )

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    @staticmethod
    def __value_from_hex(value):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            if isinstance(value, str) or isinstance(value, unicode):
                return enocean.utils.from_hex_string(value)
        except ValueError:
            return value

    @property
    def hex_id(self):
        return enocean.utils.to_hex_string(self.id)

    def update(self, force_update=False, **kwargs):
        for key, value in kwargs.items():
            # Don't update data, if
            # - value is None
            # - key is in data
            # and
            # - force_update is False
            # This is because values without None are always preferable.
            if value is None and key in self.__dict__ and force_update is False:
                continue
            # Again, ugly, but allows saving arbitrary data to the storage.
            # Not sure if we want that though?
            self.__dict__[key] = value

    def as_dict(self):
        return self.__dict__
