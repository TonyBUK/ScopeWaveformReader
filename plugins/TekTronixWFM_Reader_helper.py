from plugins.TekTronixWFM_Reader_types import *
import plugins.common_func
import math

def WFMVersionNumberPost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :

    kWaveformHeaderConstants = kAllConstants["WFMWaveformHeaderConstants"]

    if ":WFM#001" == kConvertedValue :
        kWaveformHeaderConstants.WFMWaveformFormat                                                                = WFMWaveformFormatV1
        kWaveformHeaderConstants.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMSummaryFrame].size                = 0
        kWaveformHeaderConstants.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMExplicitDimension1Format].casting = kWaveformHeaderConstants.WFMWaveformFormat.convert
        kWaveformHeaderConstants.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMExplicitDimension2Format].casting = kWaveformHeaderConstants.WFMWaveformFormat.convert
    else :
        kWaveformHeaderConstants.WFMWaveformFormat                                                                = WFMWaveformFormatV2
        kWaveformHeaderConstants.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMExplicitDimension1Format].casting = kWaveformHeaderConstants.WFMWaveformFormat.convert
        kWaveformHeaderConstants.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMExplicitDimension2Format].casting = kWaveformHeaderConstants.WFMWaveformFormat.convert
    #end
#end

def WFMExplicitDimensionFormatPost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :

    # TODO: This needs to also do Under/Over Range.

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1Format : [WFMWaveformHeaderElements.WFMExplicitDimension1NValue, WFMWaveformHeaderElements.WFMExplicitDimension1OverRange, WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange],
        WFMWaveformHeaderElements.WFMExplicitDimension2Format : [WFMWaveformHeaderElements.WFMExplicitDimension2NValue, WFMWaveformHeaderElements.WFMExplicitDimension2OverRange, WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange]
    }

    kBaseType = type(kConvertedValue)
    if kBaseType.EXPLICIT_INT16 == kConvertedValue :
        for kTargetElement in MAPPING[kElement] :
            self.HEADER_DEFINITION[kTargetElement].conversion = plugins.common_func.getSignedLong
        #end
    elif (kBaseType.EXPLICIT_FP32 == kConvertedValue) or (kBaseType.EXPLICIT_FP64 == kConvertedValue) :
        for kTargetElement in MAPPING[kElement] :
            self.HEADER_DEFINITION[kTargetElement].conversion = plugins.common_func.getFloat
        #end
    else :
        for kTargetElement in MAPPING[kElement] :
            self.HEADER_DEFINITION[kTargetElement].conversion = plugins.common_func.getSignedLong
        #end
    #end

#end

def WFMExplicitDimensionNValuePost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1NValue : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2NValue : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # Shift the Data as this was a 16 bit value occupying a 32 bit space
    if type(kTarget[MAPPING[kElement]]).EXPLICIT_INT16 == kTarget[MAPPING[kElement]] :
        kTarget[kElement] = kConvertedValue & 0x0000FFFF
    #end

#end

def WFMCurveStateFlagsPost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :

    kTarget[kElement] = {WFMWaveformStateFlagsMembers.flagOver  : WFMWaveformStateFlags.convert(kUnconvertedValue=kConvertedValue[0], kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=kRawBytesForFile),
                         WFMWaveformStateFlagsMembers.flagUnder : WFMWaveformStateFlags.convert(kUnconvertedValue=kConvertedValue[1], kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=kRawBytesForFile),
                         WFMWaveformStateFlagsMembers.flagValid : WFMWaveformStateFlags.convert(kUnconvertedValue=kConvertedValue[2], kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=kRawBytesForFile),
                         WFMWaveformStateFlagsMembers.flagNulls : WFMWaveformStateFlags.convert(kUnconvertedValue=kConvertedValue[3], kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=kRawBytesForFile)}

#end

def WFMByteOrderVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMByteOrderVerificationType.INVALID
#end

def WFMVersionNumberVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue.startswith(":WFM")
#end

def WFMNumberOfDigitsInByteCountVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    VALID = range(0,9+1)
    return kConvertedValue in VALID
#end

def WFMNumberOfBytesToTheEndOfFileVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    # Note: This also verifies consistency with WFMNumberOfDigitsInByteCount.
    if kConvertedValue > 0 :
        nExpectedDigits = math.floor(math.log10(kConvertedValue)) + 1
        return (len(kRawBytesForFile) == (kConvertedValue + nElementOffsetWithinFile + self.HEADER_DEFINITION[kElement].size)) and (nExpectedDigits == kTarget[WFMHeaderElements.WFMNumberOfDigitsInByteCount])
    else :
        return False
    #end

#end

def WFMNumberOfBytesPerPointVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue > 0
#end

def WFMByteOffsetToBeginningOfCurveBufferVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue < len(kRawBytesForFile)
#end

def WFMSizeOfWaveFormHeaderBytesVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    kWaveformHeaderConstants = kAllConstants["WFMWaveformHeaderConstants"]
    return kConvertedValue == kWaveformHeaderConstants.size()
#end

def WFMSetTypeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMWaveformSetType.INVALID
#end

# TODO: Any waveforms where this *isn't* exactly 1?
def WFMCntVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue > 0
#end

# TODO: File Format says "normally 1", unclear what an abnormal case would be.
def WFMCurveRefCountVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue > 0
#end

def WFMWaveformSummaryFrameVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMWaveformSummaryFrame.INVALID
#end

def WFMGenericDoubleVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    if type(kConvertedValue) != float :
        return False
    #end
    if False == math.isfinite(kConvertedValue) :
        return False
    #end
    return True

#end

def WFMExplicitDimensionFormatVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1Format : WFMWaveformHeaderElements.WFMExplicitDimension1DimScale,
        WFMWaveformHeaderElements.WFMExplicitDimension2Format : WFMWaveformHeaderElements.WFMExplicitDimension2DimScale,
    }

    # Ingore any Invalid Entries
    if type(kConvertedValue).EXPLICIT_INVALID_FORMAT == kConvertedValue :
        return True
    #end

    if kConvertedValue in [WFMWaveformFormatV2.EXPLICIT_INT16] :
        if kFullTarget[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint] != 2 :
            return False
        #end
    elif kConvertedValue in [WFMWaveformFormatV2.EXPLICIT_INT32, WFMWaveformFormatV2.EXPLICIT_UINT32, WFMWaveformFormatV2.EXPLICIT_FP32] :
        if kFullTarget[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint] != 4 :
            return False
        #end
    elif kConvertedValue in [WFMWaveformFormatV2.EXPLICIT_UINT64, WFMWaveformFormatV2.EXPLICIT_FP64] :
        if kFullTarget[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint] != 8 :
            return False
        #end
    elif kConvertedValue in [WFMWaveformFormatV2.EXPLICIT_UINT8, WFMWaveformFormatV2.EXPLICIT_INT8] :
        if kFullTarget[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint] != 1 :
            return False
        #end
    #end

    # Scale Should be Non-Zero
    return kTarget[MAPPING[kElement]] != 0.0

#end

def WFMExplicitDimensionNValueVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1NValue : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2NValue : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1OverRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2OverRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # We know what the value should be for Floating Point inputs (NaN), everything else is unknown
    kBaseType = type(kTarget[MAPPING[kElement]])
    if kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_FP32, kBaseType.EXPLICIT_FP64] :
        return math.isnan(kConvertedValue)
    elif kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_INT16] :
        return 0 == (kUnconvertedValue & 0xFFFF0000)
    #end

    return True
#end

def WFMExplicitDimensionOverRangeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1NValue : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2NValue : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1OverRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2OverRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # We know what the value should be for Floating Point inputs (+INF), everything else is unknown
    kBaseType = type(kTarget[MAPPING[kElement]])
    if kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_FP32, kBaseType.EXPLICIT_FP64] :
        return math.isinf(kConvertedValue) and (kConvertedValue > 0)
    #end

    return True
#end

def WFMExplicitDimensionUnderRangeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1NValue : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2NValue : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1OverRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2OverRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format,
        WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # We know what the value should be for Floating Point inputs (-INF), everything else is unknown
    kBaseType = type(kTarget[MAPPING[kElement]])
    if kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_FP32, kBaseType.EXPLICIT_FP64] :
        return math.isinf(kConvertedValue) and (kConvertedValue < 0)
    #end

    OTHER = {
        WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension1OverRange,
        WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange : WFMWaveformHeaderElements.WFMExplicitDimension2OverRange
    }

    # Ingore any Invalid Entries
    if type(kTarget[MAPPING[kElement]]).EXPLICIT_INVALID_FORMAT == kTarget[MAPPING[kElement]] :
        return True
    #end

    # Over should not be smaller than Under
    return kTarget[OTHER[kElement]] >= kConvertedValue

#end

def WFMExplicitDimensionLowRangeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1LowRange : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2LowRange : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # This should be a valid floating point value
    kBaseType = type(kTarget[MAPPING[kElement]])
    if kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_FP32, kBaseType.EXPLICIT_FP64] :
        if False == math.isfinite(kConvertedValue) :
            return False
        #end
    #end

    OTHER = {
        WFMWaveformHeaderElements.WFMExplicitDimension1LowRange : WFMWaveformHeaderElements.WFMExplicitDimension1HighRange,
        WFMWaveformHeaderElements.WFMExplicitDimension2LowRange : WFMWaveformHeaderElements.WFMExplicitDimension2HighRange
    }

    # Ingore any Invalid Entries
    if type(kTarget[MAPPING[kElement]]).EXPLICIT_INVALID_FORMAT == kTarget[MAPPING[kElement]] :
        return True
    #end

    # TODO: I've never seen his contain non-zero data.

    # Low should not be bigger than High
    return kTarget[OTHER[kElement]] >= kConvertedValue

#end

def WFMExplicitDimensionPointDensityVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1PointDensity : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2PointDensity : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # This should be a valid floating point value
    if type(kTarget[MAPPING[kElement]]).EXPLICIT_INVALID_FORMAT == kTarget[MAPPING[kElement]] :
        return True
    #end

    # TODO: Does floating point as the format change anything?!?
    #       I have one example, and it has a point density of 0.
    kBaseType = type(kTarget[MAPPING[kElement]])
    if kTarget[MAPPING[kElement]] in [kBaseType.EXPLICIT_FP32, kBaseType.EXPLICIT_FP64] :
        return True
    #end

    # On an Explicit Axis, this is exactly 1
    return 1 == kConvertedValue

#end

def WFMExplicitDimensionHRefVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    MAPPING = {
        WFMWaveformHeaderElements.WFMExplicitDimension1HRef : WFMWaveformHeaderElements.WFMExplicitDimension1Format,
        WFMWaveformHeaderElements.WFMExplicitDimension2HRef : WFMWaveformHeaderElements.WFMExplicitDimension2Format
    }

    # Ignore the value if the dimension is invalid
    if type(kTarget[MAPPING[kElement]]).EXPLICIT_INVALID_FORMAT == kTarget[MAPPING[kElement]] :
        return True
    #end

    # Value has to be a Percentage (0.0 .. 100.0)
    return 0.0 <= kConvertedValue <= 100.0

#end

def WFMCurveEndOfCurveBufferOffsetVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    nBytesPerPoint         = kFullTarget[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint]
    nPostChargeStartOffset = kTarget[WFMWaveformHeaderElements.WFMCurvePostchargeStartOffset]
    nPreChargeLength       = kTarget[WFMWaveformHeaderElements.WFMCurveDataStartOffset]
    nDataLength            = nPostChargeStartOffset - nPreChargeLength
    nPostChargeLength      = kTarget[WFMWaveformHeaderElements.WFMCurvePostchargeStopOffset] - nPostChargeStartOffset

    if 0 == nBytesPerPoint :
        return False
    #end

    if 0 != (nPreChargeLength % nBytesPerPoint) :
        return False
    #end

    if 0 != (nDataLength % nBytesPerPoint) :
        return False
    #end

    if 0 != (nPostChargeLength % nBytesPerPoint) :
        return False
    #end

    return True

#end

def WaveformFileChecksumVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    # The checksum takes every byte in the file, up to the file checksum, and adds them together, storing the result as a 64 bit unsigned integer.
    # Note: The type itself is just left as a Python default int, which is 64 bit signed, however, a valid .wfm file itself couldn't come anywhere
    #       close to saturating the 64 bit limit, making this moot.

    # Assume file size limits (4 gig) means even if every byte was 0xFF, this could at most be 256 * 2^32 or 2^40, and by that point it's basically
    # impractical to analyse.
    #
    # Note: This essentially tries to prevent anything conditional, and incurs a minor speed penalty as a result of the repeated calculation of
    #       the checksum, however, this does prevent the need to slice potentially large chunks of RAM.
    return sum(kRawBytesForFile)-sum(kRawBytesForFile[nElementOffsetWithinFile:]) == kConvertedValue

#end