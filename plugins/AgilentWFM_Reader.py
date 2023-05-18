# AgilentWFM_Reader
#
# Scope Types: TBD
#
# Expected File Extention: .wfm

from plugins.AgilentWFM_Reader_types import *
from plugins.common_basetypes import ErrorLevelHandling

import plugins.common_func
import plugins.common_basetypes
import plugins.common_errorhandler
import plugins.AgilentWFM_Reader_helper

import typing
import array

# Header Format
# =============
#
# Note: For Header Elements where the data is classes as unused, that only means it is unused from the perspective of waveform decoding.
#       It is likely it still contains data that would be used by the scope when loaded, such as trigger positions / setup etc.
#
# [0x0000 .. 0x0000] 0x2B           : File Identifier
# [0x0001 .. 0x0003] ???            : Unknown - Does not seem to be used or checked
# [0x0004 .. 0x0007]                : File Version
#                                     0x06000000
#                                     0x07000000
#                                     0x08000000
#                                     0x09000000
#                                     0x0A000000
#                                     0x0B000000

# File Version - 0x06000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053]                : YDispRange - IEEE 32 Bit Float
# [0x0054 .. 0x005B]                : YDispOrg   - IEEE 64 Bit Float
# [0x005C .. 0x0063]                : YInc       - IEEE 64 Bit Float
# [0x0064 .. 0x006B]                : YOrg       - IEEE 64 Bit Float
# [0x006C .. 0x006F] ???            : Unknown - Does not seem to be used or checked
# [0x0070 .. 0x0073]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x0074 .. 0x0077] ???            : Unknown - Does not seem to be used or checked
# [0x0078 .. 0x007B] ???            : Unknown - Does not seem to be used or checked
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083]                : Number of Points : Signed 32 Bit Long
# [0x0084 .. 0x0087]                : XDispRange - IEEE 32 Bit Float
# [0x0088 .. 0x008F]                : XDispOrg   - IEEE 64 Bit Float
# [0x0090 .. 0x0097]                : XInc       - IEEE 64 Bit Float
# [0x0098 .. 0x009F]                : XOrg       - IEEE 64 Bit Float
# [0x00A0 .. 0x00A3] ???            : Unknown - Does not seem to be used or checked
# [0x00A4 .. 0x00A7]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00A8 .. 0x00AB] ???            : Unknown - Does not seem to be used or checked
# [0x00AC .. 0x00AF] ???            : Unknown - Does not seem to be used or checked
# [0x00B0 .. 0x00B3] ???            : Unknown - Does not seem to be used or checked
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# [0x0114 .. 0x0117] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following two items.
# [0x0118 .. 0x011B] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0 .. 2.
#                                     Could be some sort of byte swap rule set?
# [0x011C .. 0xXXXX]                : Waveform Data encoded as raw signed 16 bit points (Intel Order).
#
# Note : Only half the data actually appears to be used, the other half is unknown?

# File Version - 0x07000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053] ???            : Unknown - Does not seem to be used or checked
# [0x0053 .. 0x0057]                : YDispRange - IEEE 32 Bit Float
# [0x0058 .. 0x005F]                : YDispOrg   - IEEE 64 Bit Float
# [0x0060 .. 0x0067]                : YInc       - IEEE 64 Bit Float
# [0x0068 .. 0x006F]                : YOrg       - IEEE 64 Bit Float
# [0x0070 .. 0x0073] ???            : Unknown - Does not seem to be used or checked
# [0x0074 .. 0x0077]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x0078 .. 0x007B] ???            : Unknown - Does not seem to be used or checked
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083] ???            : Unknown - Does not seem to be used or checked
# [0x0084 .. 0x0087]                : Number of Points : Signed 32 Bit Long
# [0x0088 .. 0x008B]                : XDispRange - IEEE 32 Bit Float
# [0x008C .. 0x0093]                : XDispOrg   - IEEE 64 Bit Float
# [0x0094 .. 0x009B]                : XInc       - IEEE 64 Bit Float
# [0x009C .. 0x00A3]                : XOrg       - IEEE 64 Bit Float
# [0x00A4 .. 0x00A7] ???            : Unknown - Does not seem to be used or checked
# [0x00A8 .. 0x00AB]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00AC .. 0x00AF] ???            : Unknown - Does not seem to be used or checked
# [0x00B0 .. 0x00B3] ???            : Unknown - Does not seem to be used or checked
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# [0x0114 .. 0x0117] ???            : Unknown - Does not seem to be used or checked
# [0x0118 .. 0x011B] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following two items.
# [0x011C .. 0x011F] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0 .. 2.
#                                     Could be some sort of byte swap rule set?
# [0x0120 .. 0xXXXX]                : Waveform Data encoded as raw signed 16 bit points (Intel Order).
#                                     May be influenced by TBD?
#
# Note : Only half the data actually appears to be used, the other half is unknown?

# File Version - 0x08000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053] ???            : Unknown - Does not seem to be used or checked
# [0x0054 .. 0x0057] ???            : Unknown - Does not seem to be used or checked
# [0x0058 .. 0x005B]                : YDispRange - IEEE 32 Bit Float
# [0x005C .. 0x0063]                : YDispOrg   - IEEE 64 Bit Float
# [0x0064 .. 0x006B]                : YInc       - IEEE 64 Bit Float
# [0x006C .. 0x0073]                : YOrg       - IEEE 64 Bit Float
# [0x0074 .. 0x0077] ???            : Unknown - Does not seem to be used or checked
# [0x0078 .. 0x007B]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083] ???            : Unknown - Does not seem to be used or checked
# [0x0084 .. 0x0087] ???            : Unknown - Does not seem to be used or checked
# [0x0088 .. 0x008B]                : Number of Points : Signed 32 Bit Long
# [0x008C .. 0x008F]                : XDispRange - IEEE 32 Bit Float
# [0x0090 .. 0x0097]                : XDispOrg   - IEEE 64 Bit Float
# [0x0098 .. 0x009F]                : XInc       - IEEE 64 Bit Float
# [0x00A0 .. 0x00A7]                : XOrg       - IEEE 64 Bit Float
# [0x00A8 .. 0x00AB] ???            : Unknown - Does not seem to be used or checked
# [0x00AC .. 0x00AF]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00B0 .. 0x00B3] ???            : Unknown - Does not seem to be used or checked
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# [0x0114 .. 0x0117] ???            : Unknown - Does not seem to be used or checked
# [0x0118 .. 0x011B] ???            : Unknown - Does not seem to be used or checked
# [0x011C .. 0x011F] ???            : Unknown - Does not seem to be used or checked
# [0x0120 .. 0x0123] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following two items.
# [0x0124 .. 0x0127] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0 .. 2.
#                                     Could be some sort of byte swap rule set?
# [0x0128 .. 0xXXXX]                : Waveform Data encoded as raw signed 16 bit points (Intel Order).
#                                     May be influenced by TBD?
#
# Note : Only half the data actually appears to be used, the other half is unknown?

# File Version - 0x09000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053] ???            : Unknown - Does not seem to be used or checked
# [0x0054 .. 0x0057] ???            : Unknown - Does not seem to be used or checked
# [0x0058 .. 0x005B]                : YDispRange - IEEE 32 Bit Float
# [0x005C .. 0x0063]                : YDispOrg   - IEEE 64 Bit Float
# [0x0064 .. 0x006B]                : YInc       - IEEE 64 Bit Float
# [0x006C .. 0x0073]                : YOrg       - IEEE 64 Bit Float
# [0x0074 .. 0x0077] ???            : Unknown - Does not seem to be used or checked
# [0x0078 .. 0x007B]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083] ???            : Unknown - Does not seem to be used or checked
# [0x0084 .. 0x0087] ???            : Unknown - Does not seem to be used or checked
# [0x0088 .. 0x008B]                : Number of Points : Signed 32 Bit Long
# [0x008C .. 0x008F]                : XDispRange - IEEE 32 Bit Float
# [0x0090 .. 0x0097]                : XDispOrg   - IEEE 64 Bit Float
# [0x0098 .. 0x009F]                : XInc       - IEEE 64 Bit Float
# [0x00A0 .. 0x00A7]                : XOrg       - IEEE 64 Bit Float
# [0x00A8 .. 0x00AB] ???            : Unknown - Does not seem to be used or checked
# [0x00AC .. 0x00AF]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00B0 .. 0x00B3] ???            : Unknown - Does not seem to be used or checked
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# [0x0114 .. 0x0117] ???            : Unknown - Does not seem to be used or checked
# [0x0118 .. 0x011B] ???            : Unknown - Does not seem to be used or checked
# [0x011C .. 0x011F] ???            : Unknown - Does not seem to be used or checked
# [0x0120 .. 0x0123] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following items.
# [0x0124 .. 0x0127] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0x0002 .. 0xFFC3.
#                                     Could be some sort of byte swap rule set?
# [0x0128 .. 0x012B] ???            : Unknown - Does not seem to be used or checked - Some sort of ZLIB Header?
# [0x012C .. 0xXXXX]                : Waveform Data encoded as ZLIB Compressed Data.

# File Version - 0x0A000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053] ???            : Unknown - Does not seem to be used or checked
# [0x0054 .. 0x0057] ???            : Unknown - Does not seem to be used or checked
# [0x0058 .. 0x005B]                : YDispRange - IEEE 32 Bit Float
# [0x005C .. 0x0063]                : YDispOrg   - IEEE 64 Bit Float
# [0x0064 .. 0x006B]                : YInc       - IEEE 64 Bit Float
# [0x006C .. 0x0073]                : YOrg       - IEEE 64 Bit Float
# [0x0074 .. 0x0077] ???            : Unknown - Does not seem to be used or checked
# [0x0078 .. 0x007B]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083] ???            : Unknown - Does not seem to be used or checked
# [0x0084 .. 0x0087] ???            : Unknown - Does not seem to be used or checked
# [0x0088 .. 0x008B]                : Number of Points : Signed 32 Bit Long
# [0x008C .. 0x008F]                : XDispRange - IEEE 32 Bit Float
# [0x0090 .. 0x0097]                : XDispOrg   - IEEE 64 Bit Float
# [0x0098 .. 0x009F]                : XInc       - IEEE 64 Bit Float
# [0x00A0 .. 0x00A7]                : XOrg       - IEEE 64 Bit Float
# [0x00A8 .. 0x00AB] ???            : Unknown - Does not seem to be used or checked
# [0x00AC .. 0x00AF]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00B0 .. 0x00B3] ???            : Unknown - Does not seem to be used or checked
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following items.
# [0x0114 .. 0x0117] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0x0002 .. 0xFFC3.
#                                     Could be some sort of byte swap rule set?
# [0x0118 .. 0x011B] ???            : Unknown - Does not seem to be used or checked - Some sort of ZLIB Header?
# [0x011C .. 0xXXXX]                : Waveform Data encoded as ZLIB Compressed Data.

# File Version - 0x0B000000
# =========================
#
# [0x0010 .. 0x0013] 0x00000000     : File Format 0x00000000 = Raw, some values b0rk the parser
# [0x0014 .. 0x0017] ???            : Unknown - Does not seem to be used or checked
# [0x0018 .. 0x001B] ???            : Unknown - Does not seem to be used or checked
# [0x001C .. 0x001F] ???            : Unknown - Does not seem to be used or checked
# [0x0020 .. 0x0023] ???            : Unknown - Does not seem to be used or checked
# [0x0024 .. 0x0027] ???            : Unknown - Does not seem to be used or checked
# [0x0028 .. 0x002B] ???            : Unknown - Does not seem to be used or checked
# [0x002C .. 0x002F] ???            : Unknown - Does not seem to be used or checked
# [0x0030 .. 0x0033]                : Max Bandwidth - IEEE 32 Bit Float
# [0x0034 .. 0x0037]                : Min Bandwidth - IEEE 32 Bit Float
# [0x0038 .. 0x003B]                : Time Stamp encoded as ??:SS:MM:HH - Note: From the fractional value, I need to sample more files to
#                                     see if it's 60ths or 100ths, however, it's unimportant to the waveform decoding...
# [0x003C .. 0x003F]                : Date DD:MM:YY:UU Where DD 1 - 31, MM 1 - 12 and YY is an offset from 1960 and UU seems to be unused.
# [0x0040 .. 0x0043]                : File Format:
#                                       0x00000000 = Raw
#                                       0x01000000 = Peak Detect
#                                       0x02000000 = Hi-Res
# [0x0044 .. 0x0047] ???            : Unknown - Does not seem to be used or checked
# [0x0048 .. 0x004B] ???            : Unknown - Does not seem to be used or checked
# [0x004C .. 0x004F] ???            : Unknown - Does not seem to be used or checked
# [0x0050 .. 0x0053] ???            : Unknown - Does not seem to be used or checked
# [0x0054 .. 0x0057] ???            : Unknown - Does not seem to be used or checked
# [0x0058 .. 0x005B]                : YDispRange - IEEE 32 Bit Float
# [0x005C .. 0x0063]                : YDispOrg   - IEEE 64 Bit Float
# [0x0064 .. 0x006B]                : YInc       - IEEE 64 Bit Float
# [0x006C .. 0x0073]                : YOrg       - IEEE 64 Bit Float
# [0x0074 .. 0x0077] ???            : Unknown - Does not seem to be used or checked
# [0x0078 .. 0x007B]                : YUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x007C .. 0x007F] ???            : Unknown - Does not seem to be used or checked
# [0x0080 .. 0x0083] ???            : Unknown - Does not seem to be used or checked
# [0x0084 .. 0x0087] ???            : Unknown - Does not seem to be used or checked
# [0x0088 .. 0x008B] ???            : Unknown - Does not seem to be used or checked
# [0x008C .. 0x008F]                : Number of Points : Signed 32 Bit Long
# [0x0090 .. 0x0093]                : XDispRange - IEEE 32 Bit Float
# [0x0094 .. 0x009B]                : XDispOrg   - IEEE 64 Bit Float
# [0x009C .. 0x00A3]                : XInc       - IEEE 64 Bit Float
# [0x00A4 .. 0x00AB]                : XOrg       - IEEE 64 Bit Float
# [0x00AC .. 0x00AF] ???            : Unknown - Does not seem to be used or checked
# [0x00B0 .. 0x00B3]                : XUnits:
#                                       0x00000000 = Unknown
#                                       0x01000000 = Volts
#                                       0x02000000 = Watt
#                                       0x03000000 = Amp
#                                       0x04000000 = Ohm
#                                       0x05000000 = Reflect C
#                                       0x06000000 = Gain
#                                       0x07000000 = Decibel
#                                       0x08000000 = Degree
#                                       0x09000000 = Constant
#                                       0x0A000000 = Logic
#                                       0x0B000000 = Second
#                                       0x0C000000 = Meter
#                                       0x0D000000 = Inch
#                                       0x0E000000 = Hertz
#                                       0x0F000000 = Percent
#                                       0x10000000 = Ratio
#                                       0x11000000 = Sample
#                                       0x12000000 = W Point
#                                       0x13000000 = Division
#                                       0x14000000 = Decibel M
#                                       0x15000000 = Hour
#                                       0x16000000 = Hour 2
#                                       0x17000000 = Waveform
#                                       0x18000000 = Hits
#                                       0x19000000 = Bit
#                                       0x1A000000 = Feet
#                                       0x1B000000 = Inductance
#                                       0x1C000000 = Capacitance
#                                       0x1D000000 = Minute
#                                       0x1E000000 = Temperature
#                                       0x1F000000 = Unit Interval
# [0x00B4 .. 0x00B7] ???            : Unknown - Does not seem to be used or checked
# [0x00B8 .. 0x00BB] ???            : Unknown - Does not seem to be used or checked
# [0x00BC .. 0x00BF] ???            : Unknown - Does not seem to be used or checked
# [0x00C0 .. 0x00C3] ???            : Unknown - Does not seem to be used or checked
# [0x00C4 .. 0x00C7] ???            : Unknown - Does not seem to be used or checked
# [0x00C8 .. 0x00CB] ???            : Unknown - Does not seem to be used or checked
# [0x00CC .. 0x00CF] ???            : Unknown - Does not seem to be used or checked
# [0x00D0 .. 0x00D3] ???            : Unknown - Does not seem to be used or checked
# [0x00D4 .. 0x00D7] ???            : Unknown - Does not seem to be used or checked
# [0x00D8 .. 0x00DB] ???            : Unknown - Does not seem to be used or checked
# [0x00DC .. 0x00DF] ???            : Unknown - Does not seem to be used or checked
# [0x00E0 .. 0x00E3] ???            : Unknown - Does not seem to be used or checked
# [0x00E4 .. 0x00E7] ???            : Unknown - Does not seem to be used or checked
# [0x00E8 .. 0x00EB] ???            : Unknown - Does not seem to be used or checked
# [0x00EC .. 0x00EF] ???            : Unknown - Does not seem to be used or checked
# [0x00F0 .. 0x00F3] ???            : Unknown - Does not seem to be used or checked
# [0x00F4 .. 0x00F7] ???            : Unknown - Does not seem to be used or checked
# [0x00F8 .. 0x00FB] ???            : Unknown - Does not seem to be used or checked
# [0x00FC .. 0x00FF] ???            : Unknown - Does not seem to be used or checked
# [0x0100 .. 0x0103] ???            : Unknown - Does not seem to be used or checked
# [0x0104 .. 0x0107] ???            : Unknown - Does not seem to be used or checked
# [0x0108 .. 0x010B] ???            : Unknown - Does not seem to be used or checked
# [0x010C .. 0x010F] ???            : Unknown - Does not seem to be used or checked
# [0x0110 .. 0x0113] ???            : Unknown - Does not seem to be used or checked
# [0x0114 .. 0x0117] ???            : Unknown - Does not seem to be used or checked
# [0x0118 .. 0x011B] ???            : Unknown - Does not seem to be used or checked
# [0x011C .. 0x011F] ???            : Unknown - Does not seem to be used or checked
# TODO: Determine the relationship between the following items.
# [0x0120 .. 0x0123] TBD            : Seems to be some sort of data format specifier.
#                                     Valid range appears to be 0x0002 .. 0xFFC3.
#                                     Could be some sort of byte swap rule set?
# [0x0124 .. 0x0127] ???            : Unknown - Does not seem to be used or checked - Some sort of ZLIB Header?
# [0x0128 .. 0xXXXX]                : Waveform Data encoded as ZLIB Compressed Data.

class Reader(plugins.common_basetypes.Reader):

    class __WFMHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = WFMHeaderElements
            self.HEADER_DEFINITION = {
                WFMHeaderElements.WFMHeaderIdentifier                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 1,      conversion = plugins.common_func.getUnsignedChar,                           error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = WFMHeaderIdentifierType.convert,                              post = None,                                                    validate = plugins.AgilentWFM_Reader_helper.WFMHeaderIdentifierVerification),
                WFMHeaderElements.WFMUnknownBlock1                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 3,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMHeaderElements.WFMFileVersion                        : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = WFMFileVersionType.convert,                                   post = plugins.AgilentWFM_Reader_helper.WFMFileVersionPost,     validate = plugins.AgilentWFM_Reader_helper.WFMFileVersionVerification)
            }
        #end
    #end

    class __WFMWaveformHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = WFMWaveformHeaderElements
            self.HEADER_DEFINITION = {
                WFMWaveformHeaderElements.WFMUnknownBlock1              : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMUnknownFileType            : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMUnknownBlock2              : plugins.common_basetypes.HeaderFixedWidthElement(size = 28,     conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMMaxBandwidth               : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMMinBandwidth               : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMTimeStamp                  : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = plugins.AgilentWFM_Reader_helper.WFMTimeStampConvert,         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMDate                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = plugins.AgilentWFM_Reader_helper.WFMDateConvert,              post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMFileFormat                 : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = WFMFileFormatType.convert,                                    post = None,                                                    validate = plugins.AgilentWFM_Reader_helper.WFMFileFormatVerification),
                WFMWaveformHeaderElements.WFMUnknownBlock3              : plugins.common_basetypes.HeaderFixedWidthElement(size = 12,     conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMYDispRange                 : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMYDispOrg                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMYInc                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMYOrg                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMUnknownBlock4              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMYUnits                     : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = WFMAxisUnitsType.convert,                                     post = None,                                                    validate = plugins.AgilentWFM_Reader_helper.WFMAxisUnitsVerification),
                WFMWaveformHeaderElements.WFMUnknownBlock5              : plugins.common_basetypes.HeaderFixedWidthElement(size = 12,     conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMNumberOfPoints             : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMXDispRange                 : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMXDispOrg                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMXInc                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMXOrg                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,      conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMUnknownBlock6              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformHeaderElements.WFMXUnits                     : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = WFMAxisUnitsType.convert,                                     post = None,                                                    validate = plugins.AgilentWFM_Reader_helper.WFMAxisUnitsVerification),
                WFMWaveformHeaderElements.WFMUnknownBlock7              : plugins.common_basetypes.HeaderFixedWidthElement(size = 112,    conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
            }
        #end
    #end

    class __WFMWaveformConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = WFMWaveformElements
            self.HEADER_DEFINITION = {
                WFMWaveformElements.WFMUnknownDataType                  : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,      conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformElements.WFMWaveformHeader                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 0,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                WFMWaveformElements.WFMRawWaveform                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 0,      conversion = plugins.common_func.getByteArray,                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = plugins.AgilentWFM_Reader_helper.WFMRawWaveformRawConvert,    post = None,                                                    validate = None)
            }
        #end
    #end

    # TODO: No Pre/Post Charge
    class WFMCurveBufferElements() :
#        WFMCurveBufferPreCharge                             = 0
#        WFMCurveBufferPostCharge                            = 1 + WFMCurveBufferPreCharge
        WFMCurveBuffer                                      = 0 # 1 + WFMCurveBufferPostCharge
    #end


    __kByteBuffer     = None
    _kWFM             = {}

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :


        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        # Waveform Header Constants
        kWFMHeaderConstants         = self.__WFMHeaderConstants()
        kWFMWaveformHeaderConstants = self.__WFMWaveformHeaderConstants()
        kWFMWaveformConstants       = self.__WFMWaveformConstants()
        kAllConstants = {
            "WFMHeaderConstants"         : kWFMHeaderConstants,
            "WFMWaveformHeaderConstants" : kWFMWaveformHeaderConstants,
            "WFMWaveformConstants"       : kWFMWaveformConstants
        }

        # Perform all Decoding / Acquisition in the Header, thereby making the remaining
        # usage a simple series of accessor methods.
        self._kWFM = {}

        # Decode the Headers/Data
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=0,                                                               kWFM=self._kWFM, kIndex=WFMHeaderElements,         kHeaderElement=WFMElements.WFMHeader,         kHeaderConstants=kWFMHeaderConstants,         kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=kWFMHeaderConstants.size(),                                      kWFM=self._kWFM, kIndex=WFMWaveformHeaderElements, kHeaderElement=WFMElements.WFMWaveformHeader, kHeaderConstants=kWFMWaveformHeaderConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=kWFMHeaderConstants.size() + kWFMWaveformHeaderConstants.size(), kWFM=self._kWFM, kIndex=WFMWaveformElements,       kHeaderElement=WFMElements.WFMWaveform,       kHeaderConstants=kWFMWaveformConstants,       kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Encode the Waveforms

        # Extract the Raw Waveform
        kDecodedData = self._kWFM[WFMElements.WFMWaveform][WFMWaveformElements.WFMRawWaveform]

        # Extract the Number of Points
        nPoints = self._kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMNumberOfPoints]

        # Extract the X Axis
        nXOff   = 0
        nXZero  = self._kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMXOrg]
        nXMult  = self._kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMXInc]

        # Extract the Y Axis
        nYOFF   = 0
        nYZERO  = self._kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMYOrg]
        nYMULT  = self._kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMYInc]

        # TODO: No Pre/Post Charge?

        # Encode the Waveforms
        self.__kWaveform = {
            self.WFMCurveBufferElements.WFMCurveBuffer           : [nYZERO + (nYMULT * (Y - nYOFF)) for Y in kDecodedData],
        }

        self.__kTimes    = {
            self.WFMCurveBufferElements.WFMCurveBuffer           : [nXZero + (nXMult * (X -              nXOff)) for X in range(nPoints+1)],
        }

    #end

    def __enter__(self) :
        return self
    #end

    def __exit__(self, type, value, traceback) :
        return False
    #end

    def __iter__(self) :
        return self.getWaveform().__iter__()
    #end

    # The purpose of this method is to perform the minimum number of tests to identify whether the file *could* be
    # of its specified type.
    @classmethod
    def isValid(self, kFileBuffer : bytearray, kPluginOptions : dict = None) -> bool :

        try :
            self.__WFMHeaderConstants().getElement(None, kFileBuffer, None, 0, WFMHeaderElements.WFMHeaderIdentifier, None, None, ErrorLevelHandling.NORMAL)
        except Exception as e :
            return False
        #end

        return True

    #end

    def getWaveform(self) -> list :
        if None == self.__kWaveform :
            return []
        #end
        return self.__kWaveform[self.WFMCurveBufferElements.WFMCurveBuffer]
    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        if (None == self.__kTimes) or (None == self.__kWaveform) :
            return [], []
        #end
        return self.__kTimes[self.WFMCurveBufferElements.WFMCurveBuffer], self.__kWaveform[self.WFMCurveBufferElements.WFMCurveBuffer]
    #end

    def __encodeWFMHeader(self, kBufferRaw : bytes, nOffset : int, kWFM : dict, kIndex, kHeaderElement, kHeaderConstants, kAllConstants : dict, kErrorHandling : ErrorLevelHandling) :

        kWFM[kHeaderElement] = {}
        kHeader              = kWFM[kHeaderElement]

        nBufferedLength      = kHeaderConstants.size()
        kRawBytesForHeader   = kBufferRaw[nOffset:nOffset+nBufferedLength]
        for e in kIndex :
            if 0 != kHeaderConstants.HEADER_DEFINITION[e].size :
                kHeaderConstants.storeElement(kRawBytesForBlock=kRawBytesForHeader, kAllConstants=kAllConstants, kRawBytesForFile=kBufferRaw, nOffset=nOffset, kElement=e, kTarget=kHeader, kFullTarget=kWFM, kErrorHandling=kErrorHandling)
            else :
                kWFM[kHeaderElement][e] = None
            #end
        #end

    #end

#end