# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from enocean.protocol.eep import EEP
eep = EEP()
# profiles = eep.


def test_first_range():
    offset = -40
    values = range(0x01, 0x0C)
    for i in range(len(values)):
        minimum = float(i * 10 + offset)
        maximum = minimum + 40
        profile = eep.find_profile([], 0xA5, 0x02, values[i])

        assert minimum == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('min').text)
        assert maximum == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('max').text)


def test_second_range():
    offset = -60
    values = range(0x10, 0x1C)
    for i in range(len(values)):
        minimum = float(i * 10 + offset)
        maximum = minimum + 80
        profile = eep.find_profile([], 0xA5, 0x02, values[i])

        assert minimum == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('min').text)
        assert maximum == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('max').text)


def test_rest():
    profile = eep.find_profile([], 0xA5, 0x02, 0x20)
    assert -10 == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('min').text)
    assert +41.2 == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('max').text)

    profile = eep.find_profile([], 0xA5, 0x02, 0x30)
    assert -40 == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('min').text)
    assert +62.3 == float(profile.find('value', {'shortcut': 'TMP'}).find('scale').find('max').text)
