# Supported profiles
All profiles (should) correspond to the official [EEP](http://www.enocean-alliance.org/eep/) by EnOcean.

### RPS Telegram (0xF6)
##### RORG 0xF6 - FUNC 0x02 - TYPE 0x02 - Light and Blind Control - Application Style 2

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|R1      |Rocker 1st action                                 |enum    |0 - Button AI                                                         |
|        |                                                  |        |1 - Button AO                                                         |
|        |                                                  |        |2 - Button BI                                                         |
|        |                                                  |        |3 - Button BO                                                         |
|EB      |Energy bow                                        |enum    |0 - released                                                          |
|        |                                                  |        |1 - pressed                                                           |
|R2      |Rocker 2nd action                                 |enum    |0 - Button AI                                                         |
|        |                                                  |        |1 - Button AO                                                         |
|        |                                                  |        |2 - Button BI                                                         |
|        |                                                  |        |3 - Button BO                                                         |
|SA      |2nd action                                        |enum    |0 - No 2nd action                                                     |
|        |                                                  |        |1 - 2nd action valid                                                  |
|T21     |T21                                               |status  |                                                                      |
|NU      |NU                                                |status  |                                                                      |



### 1BS Telegram (0xD5)
##### RORG 0xD5 - FUNC 0x00 - TYPE 0x01 - Single Input Contact

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|CO      |Contact                                           |enum    |0 - open                                                              |
|        |                                                  |        |1 - closed                                                            |



### 4BS Telegram (0xA5)
##### RORG 0xA5 - FUNC 0x02 - TYPE 0x01 - Temperature Sensor Range -40°C to 0°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -40.0-0.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x02 - Temperature Sensor Range -30°C to +10°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -30.0-10.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x03 - Temperature Sensor Range -20°C to +20°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -20.0-20.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x04 - Temperature Sensor Range -10°C to +30°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -10.0-30.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x05 - Temperature Sensor Range 0°C to +40°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 0.0-40.0 °C                                               |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x06 - Temperature Sensor Range +10°C to +50°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 10.0-50.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x07 - Temperature Sensor Range +20°C to +60°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 20.0-60.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x08 - Temperature Sensor Range +30°C to +70°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 30.0-70.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x09 - Temperature Sensor Range +40°C to +80°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 40.0-80.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x0A - Temperature Sensor Range +50°C to +90°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 50.0-90.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x0B - Temperature Sensor Range +60°C to +100°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 60.0-100.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x10 - Temperature Sensor Range -60°C to +20°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -60.0-20.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x11 - Temperature Sensor Range -50°C to +30°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -50.0-30.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x12 - Temperature Sensor Range -40°C to +40°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -40.0-40.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x13 - Temperature Sensor Range -30°C to +50°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -30.0-50.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x14 - Temperature Sensor Range -20°C to +60°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -20.0-60.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x15 - Temperature Sensor Range -10°C to +70°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ -10.0-70.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x16 - Temperature Sensor Range 0°C to +80°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 0.0-80.0 °C                                               |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x17 - Temperature Sensor Range +10°C to +90°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 10.0-90.0 °C                                              |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x18 - Temperature Sensor Range +20°C to +100°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 20.0-100.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x19 - Temperature Sensor Range +30°C to +110°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 30.0-110.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x1A - Temperature Sensor Range +40°C to +120°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 40.0-120.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x1B - Temperature Sensor Range +50°C to +130°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 50.0-130.0 °C                                             |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x20 - 10 Bit Temperature Sensor Range -10°C to +41.2°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |1023.0-0.0 ↔ -10.0-41.2 °C                                            |


##### RORG 0xA5 - FUNC 0x02 - TYPE 0x30 - 10 Bit Temperature Sensor Range -40°C to +62.3°C

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|TMP     |Temperature (linear)                              |value   |1023.0-0.0 ↔ -40.0-62.3 °C                                            |



##### RORG 0xA5 - FUNC 0x06 - TYPE 0x01 - Range 300lx to 60.000lx

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|SVC     |Supply voltage (linear)                           |value   |0.0-255.0 ↔ 0.0-5.1 V                                                 |
|ILL2    |Illumination 2 (linear)                           |value   |0.0-255.0 ↔ 300.0-30000.0 lx                                          |
|ILL1    |Illumination 1 (linear)                           |value   |0.0-255.0 ↔ 600.0-60000.0 lx                                          |
|RS      |Range select                                      |enum    |0 - Range acc. to DB_1 (ILL1)                                         |
|        |                                                  |        |1 - Range acc. to DB_2 (ILL2)                                         |



##### RORG 0xA5 - FUNC 0x10 - TYPE 0x03 - Temperature Sensor and Set Point

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|SP      |Set Point (linear)                                |value   |0.0-255.0 ↔ -100.0-100.0 %                                            |
|TMP     |Temperature (linear)                              |value   |255.0-0.0 ↔ 0.0-40.0 °C                                               |



##### RORG 0xA5 - FUNC 0x11 - TYPE 0x02 - Temperature Controller Output

|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|CVAR    |Actual value of controller                        |value   |0.0-255.0 ↔ 0.0-100.0 %                                               |
|FAN     |Actual value of fan                               |enum    |0 - State 0 Manual                                                    |
|        |                                                  |        |1 - State 1 Manual                                                    |
|        |                                                  |        |2 - State 2 Manual                                                    |
|        |                                                  |        |3 - State 3 Manual                                                    |
|        |                                                  |        |16 - State 0 Automatic                                                |
|        |                                                  |        |17 - State 1 Automatic                                                |
|        |                                                  |        |18 - State 2 Automatic                                                |
|        |                                                  |        |19 - State 3 Automatic                                                |
|        |                                                  |        |255 - Not Available                                                   |
|ASP     |Actual Setpoint                                   |value   |0.0-255.0 ↔ 0.0-51.2 C                                                |
|ALR     |Alarm                                             |enum    |0 - No alarm                                                          |
|        |                                                  |        |1 - Alarm                                                             |
|CTM     |Controller mode                                   |enum    |1 - Heating                                                           |
|        |                                                  |        |2 - Cooling                                                           |
|        |                                                  |        |3 - Off                                                               |
|CTS     |Controller state                                  |enum    |0 - Automatic                                                         |
|        |                                                  |        |1 - Override                                                          |
|ERH     |Energy hold-off                                   |enum    |0 - Normal                                                            |
|        |                                                  |        |1 - Energy hold-off / Dew point                                       |
|RO      |Room occupancy                                    |enum    |0 - Occupied                                                          |
|        |                                                  |        |1 - Unoccupied                                                        |
|        |                                                  |        |2 - StandBy                                                           |
|        |                                                  |        |3 - Frost                                                             |



##### RORG 0xA5 - FUNC 0x20 - TYPE 0x01 - Battery Powered Actuator (BI-DIR)

###### direction: 1
|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|CV      |Current Value                                     |value   |0.0-100.0 ↔ 0.0-100.0 %                                               |
|SO      |Service On                                        |enum    |0 - off                                                               |
|        |                                                  |        |1 - on                                                                |
|ENIE    |Energy input enabled                              |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|ES      |Energy storage sufficiently charged               |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|BCAP    |Battery capacity; change battery next days        |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|CCO     |Contact, cover open                               |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|FTS     |Failure Temperature sensor, out of range          |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|DWO     |Detection, window open                            |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|ACO     |Actuator obstructed                               |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|TMP     |Temperature (linear)                              |value   |0.0-255.0 ↔ 0.0-40.0 °C                                               |

###### direction: 2
|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|SP      |Valve Position                                    |value   |0.0-100.0 ↔ 0.0-100.0 %                                               |
|TMP     |Temperature from RCU                              |value   |0.0-255.0 ↔ 0.0-40.0 °C                                               |
|RIN     |Run init sequence                                 |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|LFS     |Lift set                                          |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|VO      |Valve open / maintenance                          |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|VC      |Valve closed                                      |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|SB      |Summer bit, Reduction of energy consumption       |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|SPS     |Set point selection                               |enum    |0 - Valve position                                                    |
|        |                                                  |        |1 - Temperature set point                                             |
|SPN     |Set point inverse                                 |enum    |0 - false                                                             |
|        |                                                  |        |1 - true                                                              |
|RCU     |Select function                                   |enum    |0 - RCU                                                               |
|        |                                                  |        |1 - service on                                                        |



### VLD Telegram (0xD2)
##### RORG 0xD2 - FUNC 0x01 - TYPE 0x01 - Electronic switch with Local Control

###### command: 4
|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|PF      |Power Failure                                     |enum    |0 - Power Failure Detection disabled/not supported                    |
|        |                                                  |        |1 - Power Failure Detection enabled                                   |
|PFD     |Power Failure Detection                           |enum    |0 - Power Failure Detection not detected/not supported/disabled       |
|        |                                                  |        |1 - Power Failure Detection Detected                                  |
|CMD     |Command indentifier                               |enum    |0-13 - Command ID {value}                                             |
|OC      |Over current switch off                           |enum    |0 - Over current switch off: ready / not supported                    |
|        |                                                  |        |1 - Over current switch off: executed                                 |
|EL      |Error level                                       |enum    |0 - Error level 0: hardware OK                                        |
|        |                                                  |        |1 - Error level 1: hardware warning                                   |
|        |                                                  |        |2 - Error level 2: hardware failure                                   |
|        |                                                  |        |3 - Error level not supported                                         |
|IO      |I/O channel                                       |enum    |0-29 - Output channel {value} (to load)                               |
|        |                                                  |        |30 - Not applicable, do not use                                       |
|        |                                                  |        |31 - Input channel (from mains supply)                                |
|LC      |Local control                                     |enum    |0 - Local control disabled / not supported                            |
|        |                                                  |        |1 - Local control enabled                                             |
|OV      |Output value                                      |enum    |0 - Output value 0% or OFF                                            |
|        |                                                  |        |1-100 - Output value {value}% or ON                                   |
|        |                                                  |        |101-126 - Not used                                                    |
|        |                                                  |        |127 - output value not valid / not set                                |

###### command: 1
|shortcut|description                                       |type    |values                                                                |
|--------|--------------------------------------------------|--------|----                                                                  |
|CMD     |Command indentifier                               |enum    |0-13 - Command ID {value}                                             |
|DV      |Dim value                                         |enum    |0 - Switch to new output value                                        |
|        |                                                  |        |1 - Dim to new output level - dim timer 1                             |
|        |                                                  |        |2 - Dim to new output level - dim timer 2                             |
|        |                                                  |        |3 - Dim to new output level - dim timer 3                             |
|        |                                                  |        |4 - Stop dimming                                                      |
|IO      |I/O channel                                       |enum    |0-29 - Output channel {value} (to load)                               |
|        |                                                  |        |30 - All output channels supported by the device                      |
|        |                                                  |        |31 - Input channel (from mains supply)                                |
|OV      |Output value                                      |enum    |0 - Output value 0% or OFF                                            |
|        |                                                  |        |1-100 - Output value {value}% or ON                                   |
|        |                                                  |        |101-126 - Not used                                                    |
|        |                                                  |        |127 - output value not valid / not set                                |



