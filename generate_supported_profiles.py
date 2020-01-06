#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import codecs
from enocean_async.protocol.eep import EEP

ROW_FORMAT = '|{:8s}|{:50s}|{:8s}|{:70s}|\n'


eep = EEP()

with codecs.open('SUPPORTED_PROFILES.md', 'w', 'utf-8') as f_handle:
    f_handle.write('# Supported profiles\n')
    f_handle.write('All profiles (should) correspond to the official [EEP](http://www.enocean-alliance.org/eep/) by EnOcean.\n\n')

    for telegram in eep.soup.find_all('telegram'):
        f_handle.write('### %s (%s)\n' % (telegram['description'], telegram['rorg']))
        for func in telegram.find_all('profiles'):
            # f_handle.write('#####  FUNC %s - %s\n' % (func['func'], func['description']))
            for profile in func.find_all('profile'):
                f_handle.write('##### RORG %s - FUNC %s - TYPE %s - %s\n\n' % (telegram['rorg'], func['func'], profile['type'], profile['description']))

                for data in profile.find_all('data'):
                    header = []

                    if data.get('direction'):
                        header.append('direction: %s' % (data.get('direction')))
                    if data.get('command'):
                        header.append('command: %s' % (data.get('command')))

                    if header:
                        f_handle.write('###### %s\n' % ' '.join(header))

                    f_handle.write(ROW_FORMAT.format('shortcut', 'description', 'type', 'values'))
                    f_handle.write(ROW_FORMAT.format('--------', '--------------------------------------------------', '--------', '----'))
                    for child in data.children:
                        if child.name is None:
                            continue

                        values = []
                        for item in child.children:
                            if item.name is None:
                                continue

                            if item.name == 'rangeitem':
                                values.append('%s-%s - %s' % (item['start'], item['end'], item['description']))
                            elif item.name == 'item':
                                values.append('%s - %s' % (item['value'], item['description']))
                            elif item.name == 'range':
                                parent = item.parent

                                range_min = float(item.find('min').text)
                                range_max = float(item.find('max').text)
                                scale = parent.find('scale')
                                scale_min = float(scale.find('min').text)
                                scale_max = float(scale.find('max').text)

                                values.append('%s-%s ↔ %s-%s %s' % (range_min, range_max, scale_min, scale_max, parent['unit']))
                        if not values:
                            f_handle.write(ROW_FORMAT.format(child['shortcut'], child['description'], child.name, ''))
                            continue

                        f_handle.write(ROW_FORMAT.format(child['shortcut'], child['description'], child.name, values[0]))
                        for i in range(1, len(values)):
                            f_handle.write(ROW_FORMAT.format('', '', '', values[i]))
                    f_handle.write('\n')
                f_handle.write('\n')

            f_handle.write('\n')
