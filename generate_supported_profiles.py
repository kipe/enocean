#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs

from enocean.protocol.eep import EEP

ROW_FORMAT = '|{:8s}|{:50s}|{:8s}|{:70s}|\n'
BASE_URL = "https://github.com/topic2k/enocean4ha/blob/topix/SUPPORTED_PROFILES.md#"

eep = EEP()

with codecs.open('SUPPORTED_PROFILES.md', 'w', 'utf-8') as f_handle:
    write = f_handle.write
    write("# Supported profiles\n")
    write(
        "All profiles (should) correspond to the official"
        " [EEP](https://www.enocean-alliance.org/eep/) by EnOcean.\n\n"
    )

    # table of contents
    for telegram in eep.soup.find_all('telegram'):
        write("<details>")
        write(f"<summary> {telegram['description']} ({telegram['rorg']}) </summary>\n\n")
        for func in telegram.find_all('profiles'):
            for profile in func.find_all('profile'):
                write(
                    f"- [FUNC {func['func']} - TYPE {profile['type']} - {profile['description']}]"
                    f"({BASE_URL}rorg-{telegram['rorg']}---func-{func['func']}---type-{profile['type']}-"
                    f"--{profile['description'].lower().replace(' ', '-')})\n"
                )

        write("\n</details>\n\n")
    write('\n\n---\n\n')

    # contents
    for telegram in eep.soup.find_all('telegram'):
        write(f"### {telegram['description']} ({telegram['rorg']})\n\n")
        for func in telegram.find_all('profiles'):
            for profile in func.find_all('profile'):
                write(
                    f"##### RORG {telegram['rorg']} - FUNC {func['func']}"
                    f" - TYPE {profile['type']} - {profile['description']}\n\n"
                )

                for data in profile.find_all('data'):
                    header = []

                    if data.get('direction'):
                        header.append(f"direction: {data.get('direction')}")
                    if data.get('command'):
                        header.append(f"command: {data.get('command')}")
                    if header:
                        write(f"###### {' '.join(header)}\n")

                    write(ROW_FORMAT.format('shortcut', 'description', 'type', 'values'))
                    write(ROW_FORMAT.format('-'*8, '-'*50, '-'*8, '-'*4))
                    for child in data.children:
                        if child.name is None:
                            continue

                        values = []
                        for item in child.children:
                            if item.name is None:
                                continue

                            if item.name == 'rangeitem':
                                values.append(f"{item['start']}-{item['end']} - {item['description']}")
                            elif item.name == 'item':
                                values.append(f"{item['value']} - {item['description']}")
                            elif item.name == 'range':
                                parent = item.parent

                                range_min = float(item.find('min').text)
                                range_max = float(item.find('max').text)
                                scale = parent.find('scale')
                                if scale:
                                    scale_min = float(scale.find('min').text)
                                    scale_max = float(scale.find('max').text)
                                else:
                                    scale_min = ''
                                    scale_max = ''
                                unit = item.get('unit') or parent.get('unit')

                                values.append(f"{range_min}-{range_max} ↔ {scale_min}-{scale_max} {unit}")

                        if not values:
                            write(ROW_FORMAT.format(child['shortcut'], child['description'], child.name, ''))
                            continue

                        write(ROW_FORMAT.format(
                            child.get('shortcut', ''),
                            child.get('description', ''),
                            child.name, values[0]
                        ))
                        for i in range(1, len(values)):
                            write(ROW_FORMAT.format('', '', '', values[i]))
                    write('\n')
            write('\n')
