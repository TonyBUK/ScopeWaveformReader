import enum
import plugins.common_basetypes

# Note: Any types of GenericBaseEnum/GenericBaseClass will need to declare an INVALID entry which is assigned if the conversion fails.
#       All that matters is this value is *unique*, -1 has just been used for convenience.
#
#       GenericBaseClass is for when only a simple constant store is needed, GenericBaseEnum is for when features, such as deriving
#       the type of the class from a member is needed.
#
#       Inheretence Selection is predicated on avoiding Enums unless it can be helped, since these effectively force
#       dictionary lookups.  The only reason to require Enums currently are:
#
#       1. Polymorphism
#       2. Iteration

class WFMHeaderIdentifierType(plugins.common_basetypes.GenericBaseClass) :
    AGILENT = 0x2B
    INVALID = -1
#end

class WFMFileVersionType(plugins.common_basetypes.GenericBaseClass) :
    V6      = 6
    V7      = 7
    V8      = 8
    V9      = 9
    V10     = 10
    V11     = 11
    INVALID = -1
#end

class WFMFileFormatType(plugins.common_basetypes.GenericBaseClass) :
    RAW         = 0x00000000
    PEAK_DETECT = 0x00000001
    HI_RES      = 0x00000002
    INVALID     = -1
#end

class WFMAxisUnitsType(plugins.common_basetypes.GenericBaseClass) :
    UNKNOWN         = 0x00000000
    VOLTS           = 0x00000001
    WATT            = 0x00000002
    AMP             = 0x00000003
    OHM             = 0x00000004
    REFLECT_C       = 0x00000005
    GAIN            = 0x00000006
    DECIBEL         = 0x00000007
    DEGREE          = 0x00000008
    CONSTANT        = 0x00000009
    LOGIC           = 0x0000000A
    SECOND          = 0x0000000B
    METER           = 0x0000000C
    INCH            = 0x0000000D
    HERTZ           = 0x0000000E
    PERCENT         = 0x0000000F
    RATIO           = 0x00000010
    SAMPLE          = 0x00000011
    W_POINT         = 0x00000012
    DIVISION        = 0x00000013
    DECIBEL_M       = 0x00000014
    HOUR            = 0x00000015
    HOUR_2          = 0x00000016
    WAVEFORM        = 0x00000017
    HITS            = 0x00000018
    BIT             = 0x00000019
    FEET            = 0x0000001A
    INDUCTANCE      = 0x0000001B
    CAPACITANCE     = 0x0000001C
    MINUTE          = 0x0000001D
    TEMPERATURE     = 0x0000001E
    UNIT_INTERVAL   = 0x0000001F
    INVALID         = -1
#end

@enum.unique
class WFMElements(enum.IntEnum) :
    WFMHeader           = 0
    WFMWaveformHeader   = 1 + WFMHeader
    WFMWaveform         = 1 + WFMWaveformHeader
#end

@enum.unique
class WFMHeaderElements(enum.IntEnum) :
    WFMHeaderIdentifier = 0
    WFMUnknownBlock1    = 1 + WFMHeaderIdentifier
    WFMFileVersion      = 1 + WFMUnknownBlock1
#end

@enum.unique
class WFMWaveformHeaderElements(enum.IntEnum) :
    WFMUnknownBlock1    = 0
    WFMUnknownFileType  = 1 + WFMUnknownBlock1
    WFMUnknownBlock2    = 1 + WFMUnknownFileType
    WFMMaxBandwidth     = 1 + WFMUnknownBlock2
    WFMMinBandwidth     = 1 + WFMMaxBandwidth
    WFMTimeStamp        = 1 + WFMMinBandwidth
    WFMDate             = 1 + WFMTimeStamp
    WFMFileFormat       = 1 + WFMDate
    WFMUnknownBlock3    = 1 + WFMFileFormat
    WFMYDispRange       = 1 + WFMUnknownBlock3
    WFMYDispOrg         = 1 + WFMYDispRange
    WFMYInc             = 1 + WFMYDispOrg
    WFMYOrg             = 1 + WFMYInc
    WFMUnknownBlock4    = 1 + WFMYOrg
    WFMYUnits           = 1 + WFMUnknownBlock4
    WFMUnknownBlock5    = 1 + WFMYUnits
    WFMNumberOfPoints   = 1 + WFMUnknownBlock5
    WFMXDispRange       = 1 + WFMNumberOfPoints
    WFMXDispOrg         = 1 + WFMXDispRange
    WFMXInc             = 1 + WFMXDispOrg
    WFMXOrg             = 1 + WFMXInc
    WFMUnknownBlock6    = 1 + WFMXOrg
    WFMXUnits           = 1 + WFMUnknownBlock6
    WFMUnknownBlock7    = 1 + WFMXUnits
#end

@enum.unique
class WFMWaveformElements(enum.IntEnum) :
    WFMUnknownDataType  = 0
    WFMWaveformHeader   = 1 + WFMUnknownDataType
    WFMRawWaveform      = 1 + WFMWaveformHeader
#end