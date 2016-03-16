#!/usr/bin/env python
import codecs
from enocean.protocol.eep import EEP

eep = EEP()

with codecs.open('SUPPORTED_PROFILES.md', 'w', 'utf-8') as f_handle:
    f_handle.write('# Supported profiles\n')
    f_handle.write('All profiles (should) correspond to the official [EEP](http://www.enocean-alliance.org/eep/) by EnOcean.\n\n')

    for telegram in eep.soup.find_all('telegram'):
        f_handle.write('### %s (%s)\n' % (telegram['description'], telegram['type']))
        for func in telegram.find_all('profiles'):
            f_handle.write('- FUNC %s - %s\n' % (func['func'], func['description']))
            for profile in func.find_all('profile'):
                f_handle.write('  - TYPE %s - %s\n' % (profile['type'], profile['description']))
        f_handle.write('\n')
