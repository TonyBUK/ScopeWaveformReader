from plugins.AgilentWFM_Reader_types import *
import plugins.common_func
import zlib

def WFMTimeStampConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    return {
        "hh"         : int(kUnconvertedValue[3]),
        "mm"         : int(kUnconvertedValue[2]),
        "ss"         : int(kUnconvertedValue[1]),
        "fractional" : int(kUnconvertedValue[0]),
    }
#end

def WFMDateConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    return {
        "DD"         : int(kUnconvertedValue[0]),
        "MM"         : int(kUnconvertedValue[1]),
        "YYYY"       : int(kUnconvertedValue[2] + 1960),
    }
#end

def WFMRawWaveformRawConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    # TODO: Are there any other formats that should be dealt with here?
    return plugins.common_func.getSignedShortArray(kByteArray=kUnconvertedValue, kOrder="<", nOffset=0, nSize=(kFullTarget[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMNumberOfPoints] + 1) * 2)
#end

def WFMRawWaveformZLibConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    return WFMRawWaveformRawConvert(zlib.decompress(kUnconvertedValue), kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile)
#end

# For my own sanity, header upgrades will be incremental from the "lowest", one at a time.
# This does mean there's a slight effeciency loss, in that the header will be adjusted
# multiple times, but it does simplify processing considerably.

def __WFMFileVersionUpgradeV6(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Calculate the Raw Buffer Size
    # Note: For now we don't try to arbitrate the size, that will be the task of the conversion routine
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size() - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def __WFMFileVersionUpgradeV7(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Perform the Previous Upgrade(s)
    __WFMFileVersionUpgradeV6(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile)

    # Perform the Upgrades specific to this variant
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock3].size += 4
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size(True) - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def __WFMFileVersionUpgradeV8(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Perform the Previous Upgrade(s)
    __WFMFileVersionUpgradeV7(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile)

    # Perform the Upgrades specific to this variant
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock3].size += 4
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock7].size += 4
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size(True) - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def __WFMFileVersionUpgradeV9(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Perform the Previous Upgrade(s)
    __WFMFileVersionUpgradeV8(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile)

    # Perform the Upgrades specific to this variant
    # TODO: Swap Raw Waveform Parser for ZLIB Parser
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMWaveformHeader].size     = 4
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].conversion  = plugins.common_func.getByteArray
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].casting     = WFMRawWaveformZLibConvert
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size() - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def __WFMFileVersionUpgradeV10(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Perform the Previous Upgrade(s)
    __WFMFileVersionUpgradeV9(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile)

    # Perform the Upgrades specific to this variant
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock7].size -= 16
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size(True) - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def __WFMFileVersionUpgradeV11(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile) :

    # Perform the Previous Upgrade(s)
    __WFMFileVersionUpgradeV10(self, kHeader, kWaveformHeader, kWaveform, kRawBytesForFile)

    # Perform the Upgrades specific to this variant
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock5].size += 4
    kWaveformHeader.HEADER_DEFINITION[WFMWaveformHeaderElements.WFMUnknownBlock7].size += 8
    kWaveform.HEADER_DEFINITION[WFMWaveformElements.WFMRawWaveform].size        = len(kRawBytesForFile) - kHeader.size() - kWaveformHeader.size(True) - kWaveform.offset(WFMWaveformElements.WFMRawWaveform)

#end

def WFMFileVersionPost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :

    # Perform the Version Upgrade as Required
    UPGRADES = {
        6  : __WFMFileVersionUpgradeV6,
        7  : __WFMFileVersionUpgradeV7,
        8  : __WFMFileVersionUpgradeV8,
        9  : __WFMFileVersionUpgradeV9,
        10 : __WFMFileVersionUpgradeV10,
        11 : __WFMFileVersionUpgradeV11
    }
    UPGRADES[kConvertedValue] (self, kAllConstants["WFMHeaderConstants"], kAllConstants["WFMWaveformHeaderConstants"], kAllConstants["WFMWaveformConstants"], kRawBytesForFile)
 
 #end

def WFMHeaderIdentifierVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMHeaderIdentifierType.INVALID
#end

def WFMFileVersionVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMFileVersionType.INVALID
#end

def WFMFileFormatVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMFileFormatType.INVALID
#end

def WFMAxisUnitsVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != WFMAxisUnitsType.INVALID
#end
