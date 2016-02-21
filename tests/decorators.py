# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import time
import functools
from os import environ


def timing(rounds=1, limit=None):
    '''
    Wrapper to implement simple timing of tests.
    Allows running multiple rounds to calculate average time.
    Limit (in milliseconds) can be set to assert, if (average) duration is too high.
    '''
    def decorator(method):
        @functools.wraps(method)
        def f():
            if rounds == 1:
                start = time.time()
                method()
                duration = time.time() - start
            else:
                start = time.time()
                for i in range(rounds):
                    method()
                duration = (time.time() - start) / rounds
            # Use milliseconds for duration counter
            duration = duration * 1e3

            print('Test "%s.%s" took %.06f ms.' % (method.__module__, method.__name__, duration))
            if limit is not None:
                assert limit > duration, 'Timing failure: %.06f > %.06f' % (duration, limit)

        # Run tests with timings, only if WITH_TIMINGS environment variable is set.
        # This is because tests with multiple rounds can take long to process.
        if environ.get('WITH_TIMINGS', None) == '1':
            return f
        return method
    return decorator
