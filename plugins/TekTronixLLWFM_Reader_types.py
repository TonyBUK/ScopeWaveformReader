import enum
import plugins.common_basetypes

class LLWFMElements(plugins.common_basetypes.GenericBaseClass) :

    LLWFMHeader                             = 0
    LLWFMWaveformHeader                     = 1 + LLWFMHeader
    LLWFMCurveBuffer                        = 1 + LLWFMWaveformHeader
    LLWFMWaveformFileChecksum               = 1 + LLWFMCurveBuffer

#end

@enum.unique
class LLWFMHeaderElements(enum.IntEnum) :

    LLWFMHeader     = 0
    LLWFMLength     = LLWFMHeader + 1
    LLWFMFileLength = LLWFMLength + 1

#end

@enum.unique
class LLWFMWaveformHeaderElements(enum.IntEnum) : 

        LLWFMWaveformHeaderUnknown1         = 0
        LLWFMWaveformDataSize1              = 1 + LLWFMWaveformHeaderUnknown1
        LLWFMWaveformHeaderUnknown2         = 1 + LLWFMWaveformDataSize1
        LLWFMWaveformHeaderUnknown3         = 1 + LLWFMWaveformHeaderUnknown2
        LLWFMWaveformHeaderUnknown4         = 1 + LLWFMWaveformHeaderUnknown3
        LLWFMWaveformHeaderUnknown5         = 1 + LLWFMWaveformHeaderUnknown4
        LLWFMWaveformHeaderSampleMode1      = 1 + LLWFMWaveformHeaderUnknown5
        LLWFMWaveformHeaderSampleMode2      = 1 + LLWFMWaveformHeaderSampleMode1
        LLWFMWaveformHeaderUnknown6         = 1 + LLWFMWaveformHeaderSampleMode2
        LLWFMWaveformHeaderCouplingMode     = 1 + LLWFMWaveformHeaderUnknown6
        LLWFMWaveformHeaderSampleUnits      = 1 + LLWFMWaveformHeaderCouplingMode
        LLWFMWaveformHeaderXAxisIncrement   = 1 + LLWFMWaveformHeaderSampleUnits
        LLWFMWaveformHeaderUnknown7         = 1 + LLWFMWaveformHeaderXAxisIncrement
        LLWFMWaveformHeaderYZeroReference   = 1 + LLWFMWaveformHeaderUnknown7
        LLWFMWaveformHeaderYSampleOffset    = 1 + LLWFMWaveformHeaderYZeroReference
        LLWFMWaveformHeaderYSampleScaling   = 1 + LLWFMWaveformHeaderYSampleOffset
        LLWFMWaveformHeaderNumberOfPoints1  = 1 + LLWFMWaveformHeaderYSampleScaling
        LLWFMWaveformHeaderXAxisTrigger     = 1 + LLWFMWaveformHeaderNumberOfPoints1
        LLWFMWaveformHeaderSampleMode3      = 1 + LLWFMWaveformHeaderXAxisTrigger
        LLWFMWaveformHeaderSampleMode4      = 1 + LLWFMWaveformHeaderSampleMode3
        LLWFMWaveformHeaderNumberOfPoints2  = 1 + LLWFMWaveformHeaderSampleMode4
        LLWFMWaveformHeaderUnknown8         = 1 + LLWFMWaveformHeaderNumberOfPoints2

#end

@enum.unique
class LLWFMWaveformElements(enum.IntEnum) :

    LLWFMWaveform                           = 0

#end

@enum.unique
class LLWFMChecksumElements(enum.IntEnum) : 

    LLWFMChecksum                           = 0

#end
