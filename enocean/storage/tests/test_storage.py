# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
from enocean.storage import Storage
from enocean.decorators import timing

PATH = '/tmp/enocean-tests.json'

# NOTE: Always end the tests with Storage.wipe, so nothing is left behind.


@timing(1000)
def test_storage_creation():
    s = Storage(PATH)
    s.save()
    assert os.path.exists(PATH)
    s.wipe()
    assert not os.path.exists(PATH)
    s.wipe()


@timing(1000)
def test_storage_version():
    s = Storage('/tmp/enocean.json')
    assert s.version == 1
    assert not os.path.exists(PATH)
    s.wipe()


@timing(100)
def test_used_offsets():
    s = Storage(PATH)
    assert s.next_offset == 0
    assert s.used_offsets == []
    for i in range(0, 127):
        s.add_to_used_offsets(i)
        assert s.next_offset == i + 1
    assert s.used_offsets == list(range(0, 127))

    s.add_to_used_offsets(127)
    try:
        s.next_offset
        assert False
    except ValueError:
        pass
    assert s.used_offsets == list(range(0, 128))

    try:
        s.add_to_used_offsets(4096)
        assert False
    except ValueError:
        pass

    s.remove_from_used_offsets(45)
    assert s.next_offset == 45
    assert s.used_offsets == list(range(0, 45)) + list(range(46, 128))
    s.wipe()


# IMO this shouldn't take more than 100 ms.
@timing(100, 100)
def test_devices_add_remove():
    s = Storage(PATH)
    assert s.load_device('DE:AD:BE:EF') is None

    s.save_device(
        [0xDE, 0xAD, 0xBE, 0xEF],
        0xA5,
    )

    device = s.load_device('DE:AD:BE:EF')
    assert device is not None
    assert device.get('device_id') == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.get('eep_rorg') == 0xA5
    assert device.get('eep_func') is None
    assert device.get('eep_type') is None
    assert device.get('transmitter_offset') is None

    device['eep_func'] = 0x01
    device['eep_type'] = 0x01
    device['transmitter_offset'] = 1
    s.save_device(**device)
    assert s.next_offset == 0
    assert s.used_offsets == [1]

    # Reload Storage, just to make sure save was successful.
    s.load()

    device = s.load_device('DE:AD:BE:EF')
    assert device is not None
    assert device.get('device_id') == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.get('eep_rorg') == 0xA5
    assert device.get('eep_func') == 0x01
    assert device.get('eep_type') == 0x01
    assert device.get('transmitter_offset') == 1
    assert 1 in s.used_offsets

    # Reload Storage, just to make sure save was successful.
    s.load()
    s.remove_device('DE:AD:BE:EF')
    assert s.devices == {}

    s.wipe()
