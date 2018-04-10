# -*- encoding: utf-8 -*-
from enocean.manufacturer.eltako import *

roomsensors = []
roomsensors.append(FTR65HS(u'EL:TA:KO:ID', 'my/mqtt/topic'))
roomsensors.append(FTR65HS(u'EL:TA:KO:ID', 'my/mqtt/topic'))
roomsensors.append(FTR65HS(u'EL:TA:KO:ID', 'my/mqtt/topic'))

shutters = []
shutters.append(FSB14(u'EL:TA:KO:ID', 'my/mqtt/topic', 25.0, 30.0, [0x00, 0x01, 0x02, 0x03]))
shutters.append(FSB14(u'EL:TA:KO:ID', 'my/mqtt/topic', 25.0, 30.0, [0x00, 0x01, 0x02, 0x03]))
shutters.append(FSB14(u'EL:TA:KO:ID', 'my/mqtt/topic', 25.0, 30.0, [0x00, 0x01, 0x02, 0x03]))

dimmer = []
dim1 = FUD14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03])
dimmer.append(dim1)
dim2 = FUD14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03], [0x00, 0x01, 0x02, 0x03])
dimmer.append(dim2)
dim3 = FUD14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03], [0x00, 0x01, 0x02, 0x03], [0x00, 0x01, 0x02, 0x03])
dimmer.append(dim3)


hygrometer = []
hygrometer.append(TFUTH(u'EL:TA:KO:ID', 'my/mqtt/topic'))
hygrometer.append(TFUTH(u'EL:TA:KO:ID', 'my/mqtt/topic'))

thermostate = []
thermostate.append(FAE14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03]))
thermostate.append(FAE14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03]))

weatherstation = FWS61(u'EL:TA:KO:ID', 'my/mqtt/topic')
rockers = FTS14EM()

switches = []
sw1 = FSR_FTN_14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03])
switches.append(sw1)
sw2 = FSR_FTN_14(u'EL:TA:KO:ID', 'my/mqtt/topic', [0x00, 0x01, 0x02, 0x03])
switches.append(sw2)