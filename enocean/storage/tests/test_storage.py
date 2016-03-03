# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
import errno
from enocean.storage import Storage, Device
from enocean.tests.decorators import timing

PATH = '/tmp/enocean-tests.json'
# Remove the file to be sure...
try:
    os.unlink(PATH)
except OSError:
    pass


def test_storage_creation_default_path():
    # DO NOT WIPE HERE!!!!
    # Would cause data loss!
    Storage()


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
        assert True
    assert s.used_offsets == list(range(0, 128))

    try:
        s.add_to_used_offsets(4096)
        assert False
    except ValueError:
        assert True

    s.remove_from_used_offsets(45)
    try:
        s.remove_from_used_offsets(45)
    except ValueError:
        pass
    assert s.next_offset == 45
    assert s.used_offsets == list(range(0, 45)) + list(range(46, 128))

    s.used_offsets = []
    assert s.used_offsets == []
    s.wipe()


@timing(100, 100)
def test_devices_add_remove():
    s = Storage(PATH)
    try:
        s.load_device('DE:AD:BE:EF')
        assert False
    except KeyError:
        assert True

    s.save_device(Device(
        id=[0xDE, 0xAD, 0xBE, 0xEF],
        eep_rorg=0xA5,
    ))

    device = s.load_device('DE:AD:BE:EF')
    assert device is not None
    assert device.id == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.eep_rorg == 0xA5
    assert device.eep_func is None
    assert device.eep_type is None
    assert device.transmitter_offset is None

    device.eep_func = 0x01
    device.eep_type = 0x01
    device.transmitter_offset = 1
    device.name = 'test'
    s.save_device(device)
    assert s.next_offset == 0
    assert s.used_offsets == [1]

    try:
        s.used_offsets = 'ASD'
        assert False
    except ValueError:
        assert True

    # Reload Storage, just to make sure save was successful.
    s.load()

    device = s.load_device('DE:AD:BE:EF')
    assert device is not None
    assert device.id == [0xDE, 0xAD, 0xBE, 0xEF]
    assert device.eep_rorg == 0xA5
    assert device.eep_func == 0x01
    assert device.eep_type == 0x01
    assert device.transmitter_offset == 1
    assert device.name == 'test'
    assert 1 in s.used_offsets

    try:
        s.save_device(device.as_dict())
        assert False
    except ValueError:
        pass

    s.remove_device('DE:AD:BE:EF')
    del s.data['devices']
    s.save_device(device)
    # Reload Storage, just to make sure save was successful.
    s.load()

    s.remove_device('DE:AD:BE:EF')
    s.save_device(device)
    # Reload Storage, just to make sure save was successful.
    s.load()

    s.save_device(device)
    # Reload Storage, just to make sure save was successful.
    s.load()
    s.remove_device([0xDE, 0xAD, 0xBE, 0xEF])
    assert s.devices == {}

    try:
        s.remove_device('DE:AD:BE:EF')
        assert False
    except KeyError:
        assert True

    s.wipe()


def test_random():
    # FFS, if this kind of tests fail, and cause issues, shoot @kipe.
    # @kipe wrote:
    #   to be honest, I have no idea on how to do these kinds of tests, except in a very, very
    #   very, very, safe environoment :S
    #   and furthermore, if these kind of tests run in your environment, you're fucked anyways...

    # Try a directory, we are absolutely not allowed to write.
    s = Storage('/usr/var/lib/local/bin/asd')
    try:
        s.save()
    except OSError as exception:
        if exception == errno.EEXIST:
            raise
        pass

    s.location = '/bin/sh'
    try:
        s.wipe()
    except OSError as exception:
        if exception == errno.EPERM:
            pass
