# TekTronixISF_Reader
#
# Scope Types: TDS3000 & TDS3000B
#
# Expected File Extention: .isf

from plugins.TekTronixISF_Reader_types import *
from plugins.common_basetypes import ErrorLevelHandling

import plugins.common_func
import plugins.common_basetypes
import plugins.common_errorhandler
import plugins.TekTronixISF_Reader_helper

import typing
import array

# The following are items I've found in the waveforms to date

# :WFMPRE:
# BYT_NR : 1 or 2
# BIT_NR : BYT_NR * 8
# ENCDG  : ASC or BIN (ASC = Comma Delimited, BIN = Binary Packed)
# BN_FMT : RI or RP (Signed Integer or Unsigned Integer) - Binary Packed Only
# BYT_OR : MSB or LSB (Bit Order, MSB first or LSB first) - Binary Packed Only
# NR_PT  : Number of Points in the Curve Query
# WFID   : Text Description of Waveform
# PT_FMT : Y or ENV (Point or Envelope (Min/Max Pairs))
# XINCR  : Time Interval (Seconds or Hz depending on Non-FFT/FFT)
# PT_OFF : Horizontal Offset for Data Points
# XZERO  : Time of First Sample
# XUNIT  : "s" or "Hz" (goes with XINCR)
# YMULT  : Scaling Factor for Data Points
# YZERO  : Zero Reference for Data Points
# YOFF   : Vertical Offset for Data Points
# YUNIT  : "V", "VV", "s", "Hz", "%", "div", "S/s", "ohms", "A", "W", "min",
#          "degrees", "?", "AA", "hr", "day", "dB", "B", "/Hz", "IRE", "V/V", "V/A", "VW",
#          "V/W", "VdB", "V/dB", "A/V", "A/A", "AW", "A/W", "AdB", "A/dB", "WV",
#          "W/V", "WA", "W/A", "WW", "W/W", "WdB", "W/dB", "dBV", "dB/V", "dBA",
#          "dB/A", "dBW", "dB/W", "dBdB", or "dB/dB"
# :CURVE : #X<Y> where X is the number of Y bytes, i.e. #5YYYYY.

class Reader(plugins.common_basetypes.Reader) :

    class __ISFConstants(plugins.common_basetypes.GenericTaggedConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = ISFElements
            self.HEADER_DEFINITION = {
                ISFElements.ISF_BYT_NR  : plugins.common_basetypes.HeaderTaggedElement(name="BYT_NR",   min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeIntFromIntByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_BYT_NRVerification),
                ISFElements.ISF_BIT_NR  : plugins.common_basetypes.HeaderTaggedElement(name="BIT_NR",   min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeIntFromIntByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_BIT_NRVerification),
                ISFElements.ISF_BN_FMT  : plugins.common_basetypes.HeaderTaggedElement(name="BN_FMT",   min_count = 0,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = ISFBN_FMTType.convert,                                        post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_BN_FMTVerification),
                ISFElements.ISF_NR_PT   : plugins.common_basetypes.HeaderTaggedElement(name="NR_PT",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeIntFromIntByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_XINCR   : plugins.common_basetypes.HeaderTaggedElement(name="XINCR",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeRealFromByteBuffer,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_PT_OFF  : plugins.common_basetypes.HeaderTaggedElement(name="PT_OFF",   min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeIntFromIntByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_XUNIT   : plugins.common_basetypes.HeaderTaggedElement(name="XUNIT",    min_count = 0,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_XZERO   : plugins.common_basetypes.HeaderTaggedElement(name="XZERO",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeRealFromByteBuffer,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_YMULT   : plugins.common_basetypes.HeaderTaggedElement(name="YMULT",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeRealFromByteBuffer,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_YZERO   : plugins.common_basetypes.HeaderTaggedElement(name="YZERO",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeRealFromByteBuffer,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_YOFF    : plugins.common_basetypes.HeaderTaggedElement(name="YOFF",     min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeRealFromByteBuffer,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_YUNIT   : plugins.common_basetypes.HeaderTaggedElement(name="YUNIT",    min_count = 0,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_ENCDG   : plugins.common_basetypes.HeaderTaggedElement(name="ENCDG",    min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = ISFENCDGType.convert,                                         post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_ENCDGTypeVerification),
                ISFElements.ISF_BYT_OR  : plugins.common_basetypes.HeaderTaggedElement(name="BYT_OR",   min_count = 0,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = ISFBYT_ORType.convert,                                        post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_BYT_ORVerification),
                ISFElements.ISF_PT_FMT  : plugins.common_basetypes.HeaderTaggedElement(name="PT_FMT",   min_count = 1,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_WFID    : plugins.common_basetypes.HeaderTaggedElement(name="WFID",     min_count = 0,   max_count = 1,  decode = plugins.common_func.decodeStringFromByteBuffer,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None,                                                         post = None,                                                    validate = None),
                ISFElements.ISF_CURVE   : plugins.common_basetypes.HeaderTaggedElement(name=":CURVE",   min_count = 1,   max_count = 1,  decode = None,                                              error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = plugins.TekTronixISF_Reader_helper.ISF_CURVEConvert,          post = None,                                                    validate = plugins.TekTronixISF_Reader_helper.ISF_CURVEVerification)
            }
            self.createReverseLookup()
        #end
    #end

    __kByteBuffer   = None
    __kTimes        = None
    __kWaveformRaw  = None
    __kWaveform     = None

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :

        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        # Ensure the Basic File is valid
        if False == self.isValid(kFileBuffer=self.__kByteBuffer, kPluginOptions=None) :
            plugins.common_errorhandler.ErrorHandler(kErrorMessage="Failed to perform basic file validation", kErrorLevel=plugins.common_basetypes.ErrorLevel.ERROR, kErrorHandling=kErrorHandling)
        #end

        # Tagged Data
        kTaggedData     = {}

        # Extract the Data Pairs
        kSpace          = " ".encode()[0]
        kSemiColon      = ";".encode()[0]
        kQuote          = "\"".encode()[0]
        kName           = []
        kData           = []
        bProcessingName = True
        bFoundCurve     = False
        nQuoteCount     = 0

        # TODO: Maybe if I can think of a way of generically expressing this to handle *most* cases, we could dispense with the
        #       loop here, however for now this seems like a very bespoke problem per target, especially as this format
        #       specifically mixes text and binary data.

        for kByte in self.__kByteBuffer[len(":WFMPRE:"):] :

            if bProcessingName :

                assert(kQuote != kByte)

                if kByte == kSpace :

                    bProcessingName = False
                    if bytes(kName).decode() == ":CURVE" :
                        bFoundCurve = True
                    #end


                else :
                    kName.append(kByte)
                #end

            else :

                if False == bFoundCurve :

                    if (0 == nQuoteCount) or (2 == nQuoteCount) :

                        if kByte == kSemiColon :

                            kTaggedData[bytes(kName).decode()]  = bytes(kData)
                            bProcessingName                     = True

                            # Reset the Cached Contents
                            nQuoteCount         = 0
                            kName.clear()
                            kData.clear()

                            continue

                        #end
                        
                    #end

                    if kByte == kQuote :
                        nQuoteCount += 1
                        assert(nQuoteCount <= 2)
                    #end

                #end

                kData.append(kByte)

            #end

        #end

        assert(bFoundCurve)
        kTaggedData[bytes(kName).decode()] = bytes(kData)

        # Create the Tagged Constants
        # Note: This may seem redundante here, however technically I'm flattening the structure.
        #       The actual data itself is two nodes:
        #
        # :WFMPRE:
        # - Header Data belongs to this node.
        #
        # :CURVE
        # - Curve Data belongs to this node.
        # 
        # For this format, flattening is trivial enough, however for other formats, it may be that we actually have clear sections
        # that would make sense to process separately.

        kISFConstants = self.__ISFConstants()
        kAllConstants = {
            "ISFConstants" : kISFConstants
        }
        kISF                            = {}
        kISF[ISFFileElements.ISF_DATA]  = {}
        kISFConstants.storeElements(kData=kTaggedData, kElements=ISFElements, kAllConstants=kAllConstants, kTarget= kISF[ISFFileElements.ISF_DATA], kFullTarget=kISF, kErrorHandling=kErrorHandling)

        # Buffer the one and only ISF Data
        kISFData = kISF[ISFFileElements.ISF_DATA]

        # Determine if we're decoding an ASCII Waveform or a Binary Waveform
        if ISFENCDGType.ISF_ASC == kISFData[ISFElements.ISF_ENCDG] :

            self.__kWaveformRaw = [int(k) for k in kISFData[ISFElements.ISF_CURVE][1].decode().split(",")]

        else :

            kEncoders  = {
                tuple([ISFBN_FMTType.ISF_RI, 8])    : plugins.common_func.getSignedCharArray,
                tuple([ISFBN_FMTType.ISF_RI, 16])   : plugins.common_func.getSignedShortArray,
                tuple([ISFBN_FMTType.ISF_RP, 8])    : plugins.common_func.getUnsignedCharArray,
                tuple([ISFBN_FMTType.ISF_RP, 16])   : plugins.common_func.getUnsignedShortArray
            }

            kOrder = {
                ISFBYT_ORType.ISF_MSB : ">",
                ISFBYT_ORType.ISF_LSB : "<"
            }

            self.__kWaveformRaw = kEncoders[tuple([kISFData[ISFElements.ISF_BN_FMT], kISFData[ISFElements.ISF_BIT_NR]])](kByteArray=kISFData[ISFElements.ISF_CURVE][1], kOrder=kOrder[kISFData[ISFElements.ISF_BYT_OR]], nOffset=0, nSize=kISFData[ISFElements.ISF_CURVE][0])

        #end

        # Verify the Waveform
        if kISFData[ISFElements.ISF_NR_PT] != len(self.__kWaveformRaw) :
            plugins.common_errorhandler.ErrorHandler(f"Inconsistent data found. NR_PT ({kISFData[ISFElements.ISF_NR_PT]}) != (Waveform Length ({len(self.__kWaveformRaw)})", kErrorLevel=plugins.common_basetypes.ErrorLevel.ERROR, kErrorHandling=kErrorHandling)
        #end

        # Scale the Waveform
        nYOff  = kISFData[ISFElements.ISF_YOFF]
        nYMult = kISFData[ISFElements.ISF_YMULT]
        nYZero = kISFData[ISFElements.ISF_YZERO]
        self.__kWaveform = [nYZero + (nYMult * (y - nYOff)) for y in self.__kWaveformRaw]

        # Create the Times
        nXOff  = kISFData[ISFElements.ISF_PT_OFF]
        nXMult = kISFData[ISFElements.ISF_XINCR]
        nXZero = kISFData[ISFElements.ISF_XZERO]
        self.__kTimes    = [nXZero + (nXMult * (x - nXOff)) for x in range(len(self.__kWaveformRaw))]

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

    @classmethod
    def isValid(self, kFileBuffer : bytearray, kPluginOptions : dict = None) -> bool :

        try :

            return kFileBuffer[0:8].decode() == ":WFMPRE:"

        except Exception as e :
            return False
        #end

    #end

    def getWaveform(self) -> list :
        if None == self.__kWaveform :
            return []
        #end
        return self.__kWaveform
    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        if (None == self.__kTimes) or (None == self.__kWaveform) :
            return [], []
        #end
        return self.__kTimes, self.__kWaveform
    #end

#end
