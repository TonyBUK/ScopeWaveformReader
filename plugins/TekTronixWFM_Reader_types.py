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

class WFMByteOrderVerificationType(plugins.common_basetypes.GenericBaseClass) :

    PPC     = 0xF0F0
    INTEL   = 0x0F0F
    INVALID = -1

    @classmethod
    def getOrder(self, kOrder) :
        if self.INTEL == kOrder :
            return "<"
        elif self.PPC == kOrder :
            return ">"
        #end
        return ""
    #end

#end

class WFMWaveformSetType(plugins.common_basetypes.GenericBaseClass) :
    SingleWaveformSet                       = 0
    FastFrameSet                            = 1
    INVALID                                 = -1
#end

@enum.unique
class WFMWaveformDataType(plugins.common_basetypes.GenericBaseEnum) :
    WFMDATA_SCALAR_MEAS                     = 0
    WFMDATA_SCALAR_CONST                    = 1
    WFMDATA_VECTOR                          = 2
    WFMDATA_INVALID                         = 4
    WFMDATA_WFMDB                           = 5
    WFMDATA_DIGITAL                         = 6
    INVALID                                 = -1
#end

class WFMWaveformSummaryFrame(plugins.common_basetypes.GenericBaseClass) :
    SUMMARY_FRAME_OFF                       = 0
    SUMMARY_FRAME_Average                   = 1
    SUMMARY_FRAME_Envelope                  = 2
    INVALID                                 = -1
#end

class WFMWaveformPixMapDisplayFormat(plugins.common_basetypes.GenericBaseClass) :
    DSY_FORMAT_INVALID                      = 0
    DSY_FORMAT_YT                           = 1
    DSY_FORMAT_XY                           = 2
    DSY_FORMAT_XYZ                          = 3
    INVALID                                 = -1
#end

@enum.unique
class WFMWaveformFormatV1(plugins.common_basetypes.GenericBaseEnum) :
    EXPLICIT_INT16                          = 0
    EXPLICIT_INT32                          = 1
    EXPLICIT_UINT32                         = 2
    EXPLICIT_UINT64                         = 3
    EXPLICIT_FP32                           = 4
    EXPLICIT_FP64                           = 5
    EXPLICIT_INVALID_FORMAT                 = 6
    INVALID                                 = -1
#end

@enum.unique
class WFMWaveformFormatV2(plugins.common_basetypes.GenericBaseEnum) :
    EXPLICIT_INT16                          = 0
    EXPLICIT_INT32                          = 1
    EXPLICIT_UINT32                         = 2
    EXPLICIT_UINT64                         = 3
    EXPLICIT_FP32                           = 4
    EXPLICIT_FP64                           = 5
    EXPLICIT_UINT8                          = 6
    EXPLICIT_INT8                           = 7
    EXPLICIT_INVALID_FORMAT                 = 8
    INVALID                                 = -1
#end

class WFMWaveformStorageType(plugins.common_basetypes.GenericBaseClass) :
    EXPLICIT_SAMPLE                         = 0
    EXPLICIT_MIN_MAX                        = 1
    EXPLICIT_VERT_HIST                      = 2
    EXPLICIT_HOR_HIST                       = 3
    EXPLICIT_ROW_ORDER                      = 4
    EXPLICIT_COLUMN_ORDER                   = 5
    EXPLICIT_INVALID_STORAGE                = 6
    INVALID                                 = -1
#end

class WFMWaveformSweep(plugins.common_basetypes.GenericBaseClass) :
    SWEEP_ROLL                              = 0
    SWEEP_SAMPLE                            = 1
    SWEEP_ET                                = 2
    SWEEP_INVALID                           = 3
    INVALID                                 = -1
#end

class WFMWaveformTypeOfBase(plugins.common_basetypes.GenericBaseClass) :
    BASE_TIME                               = 0
    BASE_SPECTRAL_MAG                       = 1
    BASE_SPECTRAL_PHASE                     = 2
    BASE_INVALID                            = 3
    INVALID                                 = -1
#end

@enum.unique
class WFMWaveformStateFlagsMembers(enum.IntEnum) :
    flagOver                                = 0
    flagUnder                               = 1
    flagValid                               = 2
    flagNulls                               = 3
#end

class WFMWaveformStateFlags(plugins.common_basetypes.GenericBaseClass) :
    WFM_CURVEFLAG_YES                       = 0
    WFM_CURVEFLAG_NO                        = 1
    WFM_CURVEFLAG_MAYBE                     = 2
    INVALID                                 = -1
#end

class WFMWaveformTypeOfChecksum(plugins.common_basetypes.GenericBaseClass) :
    NO_CHECKSUM                             = 0
    CTYPE_CRC16                             = 1
    CTYPE_SUM16                             = 2
    CTYPE_CRC32                             = 3
    CTYPE_SUM32                             = 4
    INVALID                                 = -1
#end

#class WFMElements(plugins.common_basetypes.GenericBaseClass) :
@enum.unique
class WFMElements(enum.IntEnum) :

    WFMHeader                               = 0
    WFMWaveformHeader                       = 1 + WFMHeader
    WFMFastFrames                           = 1 + WFMWaveformHeader
    WFMCurveBuffer                          = 1 + WFMFastFrames
    WFMWaveformFileChecksum                 = 1 + WFMCurveBuffer
    WFMCurveBufferTimes                     = 1 + WFMWaveformFileChecksum
    WFMCurveBufferScaled                    = 1 + WFMCurveBufferTimes

#end

@enum.unique
class WFMHeaderElements(enum.IntEnum) :

    WFMByteOrderVerification                = 0
    WFMVersionNumber                        = 1 + WFMByteOrderVerification
    WFMNumberOfDigitsInByteCount            = 1 + WFMVersionNumber
    WFMNumberOfBytesToTheEndOfFile          = 1 + WFMNumberOfDigitsInByteCount
    WFMNumberOfBytesPerPoint                = 1 + WFMNumberOfBytesToTheEndOfFile
    WFMByteOffsetToBeginningOfCurveBuffer   = 1 + WFMNumberOfBytesPerPoint
    WFMHorizontalZoomScaleFactor            = 1 + WFMByteOffsetToBeginningOfCurveBuffer
    WFMHorizontalZoomPosition               = 1 + WFMHorizontalZoomScaleFactor
    WFMVerticalZoomScaleFactor              = 1 + WFMHorizontalZoomPosition
    WFMVerticalZoomPosition                 = 1 + WFMVerticalZoomScaleFactor
    WFMWaveFormLabel                        = 1 + WFMVerticalZoomPosition
    WFMNumberOfFastFramesMinusOne           = 1 + WFMWaveFormLabel
    WFMSizeOfWaveFormHeaderBytes            = 1 + WFMNumberOfFastFramesMinusOne

#end

@enum.unique
class WFMWaveformHeaderElements(enum.IntEnum) :

    WFMSetType                                          = 0
    WFMCnt                                              = 1 + WFMSetType 
    WFMAcquisitionCounter                               = 1 + WFMCnt
    WFMTransactionCounter                               = 1 + WFMAcquisitionCounter
    WFMSlotID                                           = 1 + WFMTransactionCounter
    WFMIsStaticFlag                                     = 1 + WFMSlotID
    WFMUpdateSpecificationCount                         = 1 + WFMIsStaticFlag
    WFMImpDimRefCount                                   = 1 + WFMUpdateSpecificationCount
    WFMExpDimRefCount                                   = 1 + WFMImpDimRefCount
    WFMDataType                                         = 1 + WFMExpDimRefCount
    WFMGenPurposeCounter                                = 1 + WFMDataType
    WFMAccumulatedWaveformCount                         = 1 + WFMGenPurposeCounter
    WFMTargetAccumulationCount                          = 1 + WFMAccumulatedWaveformCount
    WFMCurveRefCount                                    = 1 + WFMTargetAccumulationCount
    WFMNumberOfRequestedFastFrames                      = 1 + WFMCurveRefCount
    WFMNumberOfAcquiredFastFrames                       = 1 + WFMNumberOfRequestedFastFrames
    WFMSummaryFrame                                     = 1 + WFMNumberOfAcquiredFastFrames
    WFMPixMapDisplayFormat                              = 1 + WFMSummaryFrame
    WFMPixMapMaxValue                                   = 1 + WFMPixMapDisplayFormat

    WFMExplicitDimension1DimScale                       = 1 + WFMPixMapMaxValue
    WFMExplicitDimension1DimOffset                      = 1 + WFMExplicitDimension1DimScale
    WFMExplicitDimension1DimSize                        = 1 + WFMExplicitDimension1DimOffset
    WFMExplicitDimension1Units                          = 1 + WFMExplicitDimension1DimSize
    WFMExplicitDimension1DimExtentMin                   = 1 + WFMExplicitDimension1Units
    WFMExplicitDimension1DimExtentMax                   = 1 + WFMExplicitDimension1DimExtentMin
    WFMExplicitDimension1DimResolution                  = 1 + WFMExplicitDimension1DimExtentMax
    WFMExplicitDimension1DimRefPoint                    = 1 + WFMExplicitDimension1DimResolution
    WFMExplicitDimension1Format                         = 1 + WFMExplicitDimension1DimRefPoint
    WFMExplicitDimension1StorageType                    = 1 + WFMExplicitDimension1Format
    WFMExplicitDimension1NValue                         = 1 + WFMExplicitDimension1StorageType
    WFMExplicitDimension1OverRange                      = 1 + WFMExplicitDimension1NValue
    WFMExplicitDimension1UnderRange                     = 1 + WFMExplicitDimension1OverRange
    WFMExplicitDimension1HighRange                      = 1 + WFMExplicitDimension1UnderRange
    WFMExplicitDimension1LowRange                       = 1 + WFMExplicitDimension1HighRange
    WFMExplicitDimension1UserScale                      = 1 + WFMExplicitDimension1LowRange
    WFMExplicitDimension1UserUnits                      = 1 + WFMExplicitDimension1UserScale
    WFMExplicitDimension1UserOffset                     = 1 + WFMExplicitDimension1UserUnits
    WFMExplicitDimension1PointDensity                   = 1 + WFMExplicitDimension1UserOffset
    WFMExplicitDimension1HRef                           = 1 + WFMExplicitDimension1PointDensity
    WFMExplicitDimension1TrigDelay                      = 1 + WFMExplicitDimension1HRef

    WFMExplicitDimension2DimScale                       = 1 + WFMExplicitDimension1TrigDelay
    WFMExplicitDimension2DimOffset                      = 1 + WFMExplicitDimension2DimScale
    WFMExplicitDimension2DimSize                        = 1 + WFMExplicitDimension2DimOffset
    WFMExplicitDimension2Units                          = 1 + WFMExplicitDimension2DimSize
    WFMExplicitDimension2DimExtentMin                   = 1 + WFMExplicitDimension2Units
    WFMExplicitDimension2DimExtentMax                   = 1 + WFMExplicitDimension2DimExtentMin
    WFMExplicitDimension2DimResolution                  = 1 + WFMExplicitDimension2DimExtentMax
    WFMExplicitDimension2DimRefPoint                    = 1 + WFMExplicitDimension2DimResolution
    WFMExplicitDimension2Format                         = 1 + WFMExplicitDimension2DimRefPoint
    WFMExplicitDimension2StorageType                    = 1 + WFMExplicitDimension2Format
    WFMExplicitDimension2NValue                         = 1 + WFMExplicitDimension2StorageType
    WFMExplicitDimension2OverRange                      = 1 + WFMExplicitDimension2NValue
    WFMExplicitDimension2UnderRange                     = 1 + WFMExplicitDimension2OverRange
    WFMExplicitDimension2HighRange                      = 1 + WFMExplicitDimension2UnderRange
    WFMExplicitDimension2LowRange                       = 1 + WFMExplicitDimension2HighRange
    WFMExplicitDimension2UserScale                      = 1 + WFMExplicitDimension2LowRange
    WFMExplicitDimension2UserUnits                      = 1 + WFMExplicitDimension2UserScale
    WFMExplicitDimension2UserOffset                     = 1 + WFMExplicitDimension2UserUnits
    WFMExplicitDimension2PointDensity                   = 1 + WFMExplicitDimension2UserOffset
    WFMExplicitDimension2HRef                           = 1 + WFMExplicitDimension2PointDensity
    WFMExplicitDimension2TrigDelay                      = 1 + WFMExplicitDimension2HRef

    WFMImplicitDimension1DimScale                       = 1 + WFMExplicitDimension2TrigDelay
    WFMImplicitDimension1DimOffset                      = 1 + WFMImplicitDimension1DimScale
    WFMImplicitDimension1DimSize                        = 1 + WFMImplicitDimension1DimOffset
    WFMImplicitDimension1Units                          = 1 + WFMImplicitDimension1DimSize
    WFMImplicitDimension1DimExtentMin                   = 1 + WFMImplicitDimension1Units
    WFMImplicitDimension1DimExtentMax                   = 1 + WFMImplicitDimension1DimExtentMin
    WFMImplicitDimension1DimResolution                  = 1 + WFMImplicitDimension1DimExtentMax
    WFMImplicitDimension1DimRefPoint                    = 1 + WFMImplicitDimension1DimResolution
    WFMImplicitDimension1Spacing                        = 1 + WFMImplicitDimension1DimRefPoint
    WFMImplicitDimension1UserScale                      = 1 + WFMImplicitDimension1Spacing
    WFMImplicitDimension1UserUnits                      = 1 + WFMImplicitDimension1UserScale
    WFMImplicitDimension1UserOffset                     = 1 + WFMImplicitDimension1UserUnits
    WFMImplicitDimension1PointDensity                   = 1 + WFMImplicitDimension1UserOffset
    WFMImplicitDimension1HRef                           = 1 + WFMImplicitDimension1PointDensity
    WFMImplicitDimension1TrigDelay                      = 1 + WFMImplicitDimension1HRef

    WFMImplicitDimension2DimScale                       = 1 + WFMImplicitDimension1TrigDelay
    WFMImplicitDimension2DimOffset                      = 1 + WFMImplicitDimension2DimScale
    WFMImplicitDimension2DimSize                        = 1 + WFMImplicitDimension2DimOffset
    WFMImplicitDimension2Units                          = 1 + WFMImplicitDimension2DimSize
    WFMImplicitDimension2DimExtentMin                   = 1 + WFMImplicitDimension2Units
    WFMImplicitDimension2DimExtentMax                   = 1 + WFMImplicitDimension2DimExtentMin
    WFMImplicitDimension2DimResolution                  = 1 + WFMImplicitDimension2DimExtentMax
    WFMImplicitDimension2DimRefPoint                    = 1 + WFMImplicitDimension2DimResolution
    WFMImplicitDimension2Spacing                        = 1 + WFMImplicitDimension2DimRefPoint
    WFMImplicitDimension2UserScale                      = 1 + WFMImplicitDimension2Spacing
    WFMImplicitDimension2UserUnits                      = 1 + WFMImplicitDimension2UserScale
    WFMImplicitDimension2UserOffset                     = 1 + WFMImplicitDimension2UserUnits
    WFMImplicitDimension2PointDensity                   = 1 + WFMImplicitDimension2UserOffset
    WFMImplicitDimension2HRef                           = 1 + WFMImplicitDimension2PointDensity
    WFMImplicitDimension2TrigDelay                      = 1 + WFMImplicitDimension2HRef

    WFMTimeBase1RealPointSpacing                        = 1 + WFMImplicitDimension2TrigDelay
    WFMTimeBase1Sweep                                   = 1 + WFMTimeBase1RealPointSpacing
    WFMTimeBase1TypeOfBase                              = 1 + WFMTimeBase1Sweep

    WFMTimeBase2RealPointSpacing                        = 1 + WFMTimeBase1TypeOfBase
    WFMTimeBase2Sweep                                   = 1 + WFMTimeBase2RealPointSpacing
    WFMTimeBase2TypeOfBase                              = 1 + WFMTimeBase2Sweep

    WFMUpdateRealPointOffset                            = 1 + WFMTimeBase2TypeOfBase
    WFMUpdateTTOffset                                   = 1 + WFMUpdateRealPointOffset
    WFMUpdateFracSec                                    = 1 + WFMUpdateTTOffset
    WFMUpdateGmtSec                                     = 1 + WFMUpdateFracSec

    WFMCurveStateFlags                                  = 1 + WFMUpdateGmtSec
    WFMCurveTypeOfCheckSum                              = 1 + WFMCurveStateFlags
    WFMCurveCheckSum                                    = 1 + WFMCurveTypeOfCheckSum
    WFMCurvePrechargeStartOffset                        = 1 + WFMCurveCheckSum
    WFMCurveDataStartOffset                             = 1 + WFMCurvePrechargeStartOffset
    WFMCurvePostchargeStartOffset                       = 1 + WFMCurveDataStartOffset
    WFMCurvePostchargeStopOffset                        = 1 + WFMCurvePostchargeStartOffset
    WFMCurveEndOfCurveBufferOffset                      = 1 + WFMCurvePostchargeStopOffset

#end

class WFMCurveBufferElements() :
    WFMCurveBufferPreCharge                             = 0
    WFMCurveBufferPostCharge                            = 1 + WFMCurveBufferPreCharge
    WFMCurveBuffer                                      = 1 + WFMCurveBufferPostCharge
#end

@enum.unique
class WfmFileChecksumElements(enum.IntEnum) :
    WFMWaveformFileChecksum                             = 0
#end
