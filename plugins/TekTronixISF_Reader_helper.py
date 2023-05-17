from plugins.TekTronixISF_Reader_types import *
import plugins.common_func

def ISF_CURVEConvert(kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :
    nLiteralLength = int(bytes(kUnconvertedValue[1:2]).decode())
    nPointCount    = int(bytes(kUnconvertedValue[2:nLiteralLength+2]).decode())
    kBuffer        = kUnconvertedValue[nLiteralLength+2:]
    return [nPointCount, kBuffer]
#end

def ISF_BYT_NRVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    if ISFElements.ISF_BIT_NR not in kTarget :
        return False
    #end

    return (kConvertedValue * 8) == kTarget[ISFElements.ISF_BIT_NR][0]

#end

def ISF_BIT_NRVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    if ISFElements.ISF_BYT_NR not in kTarget :
        return False
    #end

    return kConvertedValue == (kTarget[ISFElements.ISF_BYT_NR][0] * 8)

#end

def ISF_BN_FMTVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != ISFBN_FMTType.INVALID
#end

def ISF_BYT_ORVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :
    return kConvertedValue != ISFBYT_ORType.INVALID
#end

def ISF_ENCDGTypeVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    if kConvertedValue == ISFENCDGType.INVALID :
        return False
    #end

    if kConvertedValue == ISFENCDGType.ISF_BIN :

        if ISFElements.ISF_BN_FMT not in kTarget :
            return False
        #end

        if ISFElements.ISF_BYT_OR not in kTarget :
            return False
        #end

    #end

    return True

#end

def ISF_CURVEVerification(self, kAllConstants, kTarget, kFullTarget, kElement, kConvertedValue, kUnconvertedValue, kRawBytesForFile : bytes, nElementOffsetWithinFile : int) -> bool :

    if ISFElements.ISF_BYT_NR not in kTarget :
        return False
    #end

    if ISFElements.ISF_NR_PT not in kTarget :
        return False
    #end

    return kConvertedValue[0] == (kTarget[ISFElements.ISF_BYT_NR][0] * kTarget[ISFElements.ISF_NR_PT][0])

#end