from plugins.TekTronixLLWFM_Reader_types import *
import plugins.common_func

def LLWFMLengthConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    return int(kUnconvertedValue)
#end

def LLWFMFileLengthConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    return int(kUnconvertedValue)
#end

def LLWFMLengthPost(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kRawBytesForFile) :
    self.HEADER_DEFINITION[LLWFMHeaderElements.LLWFMFileLength].size = kConvertedValue
#end

def LLWFMHeaderVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue == "LLWFM #"
#end

def LLWFMLengthVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue > 0
#end

def LLWFMFileLengthVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return len(kRawBytesForFile) == (kConvertedValue + self.size())
#end

def LLWFMWaveformDataSizeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return (kConvertedValue + 10) == kFullTarget[LLWFMElements.LLWFMHeader][LLWFMHeaderElements.LLWFMFileLength]
#end

def LLWFMChecksumVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    # TODO: Calculate Checksum and Compare

    # Checksum Offset
    # Checksum is calculated *after* the LLWFMWaveformDataSize1 field.
    nChecksumOffset = kAllConstants["LLWFMHeaderConstants"].size() + \
                      kAllConstants["LLWFMWaveformHeaderConstants"].offset(LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown2)

    return kConvertedValue == (sum(plugins.common_func.getUnsignedShortArray(kByteArray=kRawBytesForFile, kOrder=self._ORDER, nOffset=nChecksumOffset, nSize=len(kRawBytesForFile) - self.size() - nChecksumOffset)) & 0xFFFF)

#end