# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from json import JSONEncoder
from enocean.storage.device import Device


class EnOceanEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Device):
            return obj.as_dict()
