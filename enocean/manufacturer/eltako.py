# -*- encoding: utf-8 -*-
from enum import Enum
from enum import IntEnum
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import MSGSTATUS, RORG
import datetime


class HCState(Enum):
    Normal = 2
    Absenkung = 1
    Aus = 0
    Frostschutz = -1


class FSB14State(Enum):
    open_ack = 2
    down_ack = -2
    run_up = 1
    run_down = -1
    stop = 0


class FSB14Cmd(IntEnum):
    up = 1
    down = -1
    stop = 0


class RockerButton(IntEnum):
    RightTop = 0x70
    RightBottom = 0x50
    LeftTop = 0x30
    LeftBottom = 0x10
    Off = 0x00


class RockerEvent(IntEnum):
    Press = 1
    Longpress_2s = 2
    Longpress_5s = 5


def checkEqual(lst):
   return lst[1:] == lst[:-1]

class ButtonEvent():
    def __init__(self, addr, time, button):
        self.addr = addr
        self.time = time
        self.button = button


class FTS14EM:
    def __init__(self):
        self.states = []

    def new_event(self, packet):
        timeNow = datetime.datetime.now()
        if packet.sender[0:2] == [0x00, 0x00] and packet.sender[2] <= 0x19 and packet.sender[2] >= 0x10:
            if packet.rorg == RORG.RPS:
                if packet.data[1] != RockerButton.Off:
                    self.states.insert(0, ButtonEvent(packet.sender_hex, timeNow, RockerButton(packet.data[1])))
                    return None
                else:
                    for i, item in enumerate(self.states):
                        if item.addr == packet.sender_hex:
                            delta_s = (timeNow - item.time).seconds
                            delta_us = (timeNow - item.time).microseconds
                            delta = delta_s + delta_us/1000000.0
                            if delta < 2:
                                ev_type = RockerEvent.Press
                            elif delta >= 2 and delta <= 5:
                                ev_type = RockerEvent.Longpress_2s
                            elif delta > 5:
                                ev_type = RockerEvent.Longpress_5s
                            else:
                                ev_type = RockerEvent.Press
                            msg_id = packet.sender_hex
                            self.states.pop(i)
                            return msg_id, ev_type
                        else:
                            #might be the case on start when a button has just been pressed
                            return None


class FTR65HS:
    def __init__(self, ID, Name):
        self.state = HCState.Normal
        self.NRValue = 0
        self.SetPoint = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.Temp = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.ID = ID
        self.Name = Name

    def decode(self, packet):
        if packet.rorg == RORG.BS4:
            if packet.data[1] == 0x00:
                self.NRValue = 0
                self.state = HCState.Normal
            elif packet.data[1] == 0x19:
                self.NRValue = -4
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x0C:
                self.NRValue = -2
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x06:
                self.NRValue = -1
                self.state = HCState.Absenkung
            else:
                self.NRValue = 0

            #update data point lists
            self.SetPoint.insert(0, packet.data[2]*(40.0 / 255))
            self.Temp.insert(0, (0xFF - packet.data[3])*(40.0 / 255))
            self.SetPoint.pop()
            self.Temp.pop()

            # check if is actually turned of...
            if self.state is not HCState.Absenkung:
                if self.SetPoint[0] != self.Temp[0]:
                    self.state = HCState.Normal
                else:
                    if (self.SetPoint[1] == self.Temp[1] and self.SetPoint[2] != self.SetPoint[1]) or \
                       (self.SetPoint == self.Temp): # and not checkEqual(self.Temp)
                        # last two messages setpoint and temp were equal and setpoint actually changed
                        self.state = HCState.Aus

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            #print('%s, Sollwert: %.2f °C' % (self.Name, self.SetPoint[0]))
            #print('%s, Istwert: %.2f °C' % (self.Name, self.Temp[0]))
            return [self.Temp[0], self.SetPoint[0], self.state.value]


class FAE14:
    def __init__(self, ID, Name, sID):
        self.state = HCState.Normal
        self.NRValue = 0
        self.SetPoint = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.Temp = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.ID = ID
        self.Name = Name
        self.sID = sID

    def decode(self, packet):
        if packet.rorg == RORG.BS4:
            if packet.data[1] == 0x00:
                self.NRValue = 0
                self.state = HCState.Normal
            elif packet.data[1] == 0x19:
                self.NRValue = -4
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x0C:
                self.NRValue = -2
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x06:
                self.NRValue = -1
                self.state = HCState.Absenkung
            else:
                self.NRValue = 0

            #update data point lists
            self.SetPoint.insert(0, packet.data[2]*(40.0 / 255))
            self.Temp.insert(0, (0xFF - packet.data[3])*(40.0 / 255))
            self.SetPoint.pop()
            self.Temp.pop()

            # check if is actually turned of...
            if self.state is not HCState.Absenkung:
                if self.SetPoint[0] != self.Temp[0]:
                    self.state = HCState.Normal
                else:
                    if (self.SetPoint[1] == self.Temp[1] and self.SetPoint[2] != self.SetPoint[1]) or \
                       (self.SetPoint == self.Temp): # and not checkEqual(self.Temp)
                        # last two messages setpoint and temp were equal and setpoint actually changed
                        self.state = HCState.Aus

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            #print('%s, Sollwert: %.2f °C' % (self.Name, self.SetPoint[0]))
            #print('%s, Istwert: %.2f °C' % (self.Name, self.Temp[0]))
            return [self.Temp[0], self.SetPoint[0], self.state.value]

        elif packet.rorg == RORG.RPS:
            if packet.data[1] == 0x70:
                self.NRValue = 0
                if self.state == HCState.Normal:
                    self.state = HCState.Normal
                else:
                    self.state = HCState.Aus
            elif packet.data[1] == 0x50:
                self.NRValue = -4
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x30:
                self.NRValue = -2
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x10:
                self.NRValue = 0
                self.state = HCState.Frostschutz

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            return [self.state.value]

    def send_SetPoint(self, SetPoint, learn=0, block=0):
        if not learn:
            stateByte = ((int(block) & 0x01) << 1) | 0x01 << 3

            spTemp = SetPoint*(255/40.0)

            sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                                sender=self.sID,
                                                command=[0x00, int(spTemp), 0x00, stateByte],
                                                status=MSGSTATUS.BS4
                                                )

        else:
            sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                              sender=self.sID,
                                              command=[0x40, 0x30, 0x0D, 0x85],
                                              status=MSGSTATUS.BS4
                                              )

        return [sendMsg]

    def send_Release(self):
        stateByte = (0x01 << 1) | 0x01 << 3

        spTemp = 0x00

        sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                            sender=self.sID,
                                            command=[0x00, int(spTemp), 0x00, stateByte],
                                            status=MSGSTATUS.BS4
                                            )

        return [sendMsg]


class TFUTH:
    def __init__(self, ID, Name):
        self.state = HCState.Normal
        self.NRValue = 0
        self.SetPoint = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.Temp = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.RHL = 0.0
        self.ID = ID
        self.Name = Name

    def decode(self, packet):
        if packet.rorg == RORG.BS4:
            if packet.data[1] == 0x00:
                self.NRValue = 0
                self.state = HCState.Normal
            elif packet.data[1] == 0x19:
                self.NRValue = -4
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x0C:
                self.NRValue = -2
                self.state = HCState.Absenkung
            elif packet.data[1] == 0x06:
                self.NRValue = -1
                self.state = HCState.Absenkung
            else:
                self.NRValue = 0

            # update data point lists
            self.SetPoint.insert(0, packet.data[2]*(40.0 / 255))
            self.Temp.insert(0, (0xFF - packet.data[3])*(40.0 / 255))
            self.SetPoint.pop()
            self.Temp.pop()

            # check if is actually turned of...
            if self.state is not HCState.Absenkung:
                if self.SetPoint[0] != self.Temp[0]:
                    self.state = HCState.Normal
                else:
                    if (self.SetPoint[1] == self.Temp[1] and self.SetPoint[2] != self.SetPoint[1]) or \
                       (self.SetPoint == self.Temp):   # and not checkEqual(self.Temp)
                       # last two messages setpoint and temp were equal and setpoint actually changed
                        self.state = HCState.Aus

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            #print('%s, Sollwert: %.2f °C' % (self.Name, self.SetPoint[0]))
            #print('%s, Istwert: %.2f °C' % (self.Name, self.Temp[0]))
            return [self.Temp[0], self.SetPoint[0], self.state.value]

    def decode_humidity(self, packet):
        if packet.rorg == RORG.BS4:
            self.RHL = packet.data[2]*(100.0/250)
            #print('%s, rel. Feuchte: %.2f%%' % (self.Name, self.RHL))
            return self.RHL


class FSB14:
    def __init__(self, ID, Name, tRun_s, tFull_s, sID):
        self.state = FSB14State.open_ack
        self.pos = 0.0
        self.ID = ID
        self.Name = Name
        self.tRun_s = tRun_s
        self.tFull_s = tFull_s
        self.sID = sID
        self.isMoving = False

    def decode(self, packet):
        if packet.rorg == RORG.RPS:
            if packet.data[1] == 0x70:
                self.pos = 0.0
                self.state = FSB14State.open_ack
                self.isMoving = False
            if packet.data[1] == 0x50:
                self.pos = 100.0
                self.state = FSB14State.down_ack
                self.isMoving = False
            if packet.data[1] == 0x01:
                self.state = FSB14State.run_up
                self.isMoving = True
            if packet.data[1] == 0x02:
                self.state = FSB14State.run_down
                self.isMoving = True

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            #print('%s, Position: %.2f%%' % (self.Name, self.pos))
            return [self.pos, self.state.value]

        if packet.rorg == RORG.BS4:
            self.state = FSB14State.stop
            self.isMoving = False

            drivetime_ms = (packet.data[1] << 8) | packet.data[2]
            drivetime_s = drivetime_ms/10.0

            if packet.data[3] == 0x01:
                self.pos -= drivetime_s/self.tRun_s*100.0
            if packet.data[3] == 0x02:
                self.pos += drivetime_s/self.tRun_s*100.0

            #print('%s, Status: %s ' % (self.Name, self.state.value))
            #print('%s, Position: %.2f%%' % (self.Name, self.pos))
            return [self.pos, self.state.value]

    def send_Move(self, newpos=None, newState=None, learn=0, block=0):
        if not learn:
            if newState is not None:
                newState = FSB14Cmd(newState)

            stateByte = ((int(block) & 0x01) << 2) | (0x01 << 1) | 0x01 << 3

            if newState == FSB14Cmd.stop:
                compState = 0x00
                self.isMoving = False
                sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                                sender=self.sID,
                                                command=[0x00, 0x00, compState, stateByte],
                                                status=MSGSTATUS.BS4
                                                )
            else:
                if newpos is None:
                    if newState == FSB14Cmd.up:
                        newpos = 0.0
                    elif newState == FSB14Cmd.down:
                        newpos = 100.0
                    else:
                        return []

                deltapos = abs(newpos - self.pos)
                runtime = (self.tRun_s/100.0)*deltapos*10

                if newpos == 0.0 or newpos == 100.0:
                    runtime = self.tFull_s * 10

                if newpos > self.pos:
                    #down
                    compState = 0x02
                else:
                    #up
                    compState = 0x01

                #override, not properly initialized...
                if self.pos < 0.0 or self.pos > 100.0:
                    #do an init run...sorry
                    runtime = self.tFull_s * 10
                    compState = 0x01

                sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                                  sender=self.sID,
                                                  command=[((int(runtime) & 0xFF00) >> 8), int(runtime) & 0xFF, compState, stateByte],
                                                  status=MSGSTATUS.BS4
                                                  )

                self.isMoving = True

        else:
            sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                              sender=self.sID,
                                              command=[0xFF, 0xF8, 0x0D, 0x80],
                                              status=MSGSTATUS.BS4
                                              )

        return [sendMsg]


class FWS61:
    def __init__(self, ID, Name):
        self.ID = ID
        self.Name = Name

    def decode(self, packet):
        if packet.data[4] == 0x1A or packet.data[4] == 0x18:
            dawn = packet.data[1]*(1000.0/255)
            temp = (packet.data[2]*(120.0/255))-40.0
            wind = packet.data[3]*(70.0/255)
            if packet.data[4] == 0x1A:
                rain = 1
            elif packet.data[4] == 0x18:
                rain = 0

            #print('%s, Dämmerung: %.2f Lux' % (self.Name, dawn))
            #print('%s, Temperatur: %.2f °C' % (self.Name, temp))
            #print('%s, Wind: %.2f m/s' % (self.Name, wind))
            #print('%s, %s' % (self.Name, rain))
            return [0, dawn, temp, wind, rain]
        elif packet.data[4] == 0x28:
            sun_west = packet.data[1]*(150.0/255)
            sun_south = packet.data[2]*(150.0/255)
            sun_east = packet.data[3]*(150.0/255)
            #print('%s, Sonne West: %.2f kLux' % (self.Name, sun_west))
            #print('%s, Sonne Süd: %.2f kLux' % (self.Name, sun_south))
            #print('%s, Sonne Ost: %.2f kLux' % (self.Name, sun_east))
            return [1, sun_west, sun_south, sun_east]

class FUD14:
    def __init__(self, ID, Name, sIDdim, sIDsleep=[0, 0, 0, 0], sIDwake=[0, 0, 0, 0]):
        self.ID = ID
        self.Name = Name
        self.isOn = 0
        self.dimval = 0.0
        self.sIDdim = sIDdim
        self.sIDsleep = sIDsleep
        self.sIDwake = sIDwake

    def decode(self, packet):
        if packet.rorg == RORG.BS4:
            if packet.data[4] == 0x08:
                self.isOn = 0
            elif packet.data[4] == 0x09:
                self.isOn = 1
            else:
                self.isOn = 0
            self.dimval = packet.data[2]

            #print('%s, Dimmwert: %d%% Status: %d' % (self.Name, self.dimval, self.isOn))
            return [self.dimval, self.isOn]
        if packet.rorg == RORG.RPS:
            if packet.data[1] == 0x50:
                self.isOn = 0
            elif packet.data[1] == 0x70:
                self.isOn = 1
            #print('%s, Status: %d ' % (self.Name, self.isOn))
            return [self.dimval, self.isOn]

    def send_DimMsg(self, newVal=None, newState=None, dimSpeed=0, learn=0, block=0):
        if not learn:
            if newVal is None and newState is None:
                return []

            if newVal == 0:
                newState = 0
                newVal = self.dimval #safe current value in actuator for manual switch use
            elif newVal is None:
                if newState == 1:
                    newVal = 100.0
                else:
                    newVal = self.dimval

            if newState is None:
                if self.isOn == 0 and newVal != 0:
                    newState = 1
                else:
                    newState = self.isOn

            stateByte = (int(newState) & 0x01) | ((int(block) & 0x01) << 2) | 0x01 << 3
            sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                            sender=self.sIDdim,
                                            command=[0x02, int(newVal) & 0xFF, int(dimSpeed) & 0xFF, stateByte],
                                            status=MSGSTATUS.BS4
                                            )
        else:
            sendMsg = RadioPacket.create_ESP2(rorg=RORG.BS4, rorg_func=0x00, rorg_type=0x00,
                                              sender=self.sIDdim,
                                              command=[0xE0, 0x40, 0x0D, 0x80],
                                              status=MSGSTATUS.BS4
                                              )
        return [sendMsg]

    def send_SleepDimMsg(self):
        onMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                        sender=self.sIDsleep,
                                        command=[0x30, 0x00, 0x00, 0x00],
                                        status=MSGSTATUS.T2NMsg
                                        )

        offMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                         sender=self.sIDsleep,
                                         command=[0x00, 0x00, 0x00, 0x00],
                                         status=MSGSTATUS.T2UMsg
                                         )
        return [onMsg, offMsg]


    def send_WakeDimMsg(self):
        onMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                        sender=self.sIDwake,
                                        command=[0x30, 0x00, 0x00, 0x00],
                                        status=MSGSTATUS.T2NMsg
                                        )

        offMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                         sender=self.sIDwake,
                                         command=[0x00, 0x00, 0x00, 0x00],
                                         status=MSGSTATUS.T2UMsg
                                         )
        return [onMsg, offMsg]


class FSR_FTN_14:
    def __init__(self, ID, Name, sID):
        self.ID = ID
        self.Name = Name
        self.isOn = 0
        self.sIDonoff = sID

    def decode(self, packet):
        if packet.rorg == RORG.RPS:
            if packet.data[1] == 0x50:
                self.isOn = 0
            elif packet.data[1] == 0x70:
                self.isOn = 1
            #print('%s, Status: %d ' % (self.Name, self.isOn))

            return self.isOn

    def send_toggle(self, RockerPos = RockerButton.RightTop):
        onMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                        sender=self.sIDonoff,
                                        command=[RockerPos, 0x00, 0x00, 0x00],
                                        status=MSGSTATUS.T2NMsg
                                        )

        offMsg = RadioPacket.create_ESP2(rorg=RORG.RPS, rorg_func=0x00, rorg_type=0x00,
                                         sender=self.sIDonoff,
                                         command=[RockerButton.Off, 0x00, 0x00, 0x00],
                                         status=MSGSTATUS.T2UMsg
                                         )
        return [onMsg, offMsg]

