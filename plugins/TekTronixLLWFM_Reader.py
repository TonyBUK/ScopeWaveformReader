# TekTronixLLWFM_Reader
#
# Scope Types: ????
#
# Expected File Extention: .wfm

from plugins.TekTronixLLWFM_Reader_types import *
from plugins.common_basetypes import ErrorLevelHandling

import plugins.common_func
import plugins.common_basetypes
import plugins.common_errorhandler
import plugins.TekTronixLLWFM_Reader_helper

import typing
import array

# Note: All Header information has been reverse engineered by myself using TekTronixs' cnvrtwfm.exe
#       application to convert from the LLWFM file to ISF / CSV.

# Header Format
# =============
#
# [0x0000] 0x4C L
# [0x0001] 0x4C L
# [0x0002] 0x57 W
# [0x0003] 0x46 F
# [0x0004] 0x4D M
# [0x0005] 0x20 ' '
# [0x0006] 0x23 #
# [0x0007] 0xXX DD (ASCII) '0' - '9'
#
# Where DD is the number of ASCII Digits to follow, i.e. if DD is '4' then the next 4 bytes will
# be occupied by a 4 digit number, encoded in ASCII, and will represent the *remaining* data length
# of the Waveform File.
#
# Since the length of the identifier + file length could be between 8 and 17 bytes depending upon the
# value of DD, we'll treat the remainder of the data as relative to the *end* of the file length test
# sequence.  However, in all likelyhood, for you this value will be 4, thereby making the length of the
# pre-amble 12 bytes, so if you're unsure, just add 12.
#
# Note: This format seems to broadly be a binary encoded ISF file, so many of the items can be thought of
#       in relation to that format.
#
# [0x0000 .. 0x0003] Unknown
# [0x0004 .. 0x0007] Signed Long Value duplicating DD (-10)
# [0x0008 .. 0x000F] Unknown
# [0x0010 .. 0x0017] Unknown IEEE 754 Double Encoded Value
# [0x0018 .. 0x001F] Unknown IEEE 754 Double Encoded Value
# [0x0020 .. 0x0027] Unknown IEEE 754 Double Encoded Value
# [0x0028 .. 0x0029] 0x011D seems to be expected for Sample Mode
# [0x002A .. 0x002B] 0x0062 seems to be expected for Y Sample, 0x0061 for Envelope Mode
# [0x002C .. 0x0033] Unknown IEEE 754 Double Encoded Value
# [0x0034 .. 0x0035] 0x0235 DC Coupling, 0x0236 AC Coupling
# [0x0036 .. 0x0037] Units for division
# [0x0038 .. 0x003F] IEEE 754 Double - X Axis Increment/Multiplication Value
# [0x0040 .. 0x0041] Unknown - Probably units/ Moding??? (TBD)
# [0x0042 .. 0x0049] IEEE 754 Double - Y Sample Zero Reference
# [0x004A .. 0x0051] IEEE 754 Double - Y Sample Offset        / 25.0 (TBV)
# [0x0052 .. 0x0059] IEEE 754 Double - Y Multiplication Value * 25.0 (TBV)
# [0x005A .. 0x005D] Signed Long - Number of Points in Waveform
# [0x005E .. 0x005F] Signed Short - Trigger Point for Wavefrom / (Number of Points in Waveform * 100)
# [0x0060 .. 0x0061] More coupling or moding?
# [0x0062 .. 0x0063] More coupling or moding?
# [0x0064 .. 0x0065] Signed Short - Number of Points in Waveform
# [0x0066 .. 0x0084] Unknown
#
# Note: For the Waveform Size, it will actually be larger than the Number of Points in the Waveform
#       as this has a pre-charge and post-charge.  These are always 16 from what I've seen, however
#       I'm working on the assumption that this might not always be true, and that the Waveform is
#       centrally located within this, with any extra points being evenly distributed for pre and
#       post charge.

class Reader(plugins.common_basetypes.Reader) :

    class __LLWFMHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = LLWFMHeaderElements
            self.HEADER_DEFINITION = {
                LLWFMHeaderElements.LLWFMHeader     : plugins.common_basetypes.HeaderFixedWidthElement(size = 7, conversion = plugins.common_func.getString,  error = plugins.common_basetypes.ErrorLevel.ERROR,  casting = None,                                                         post = None,                                                    validate = plugins.TekTronixLLWFM_Reader_helper.LLWFMHeaderVerification),
                LLWFMHeaderElements.LLWFMLength     : plugins.common_basetypes.HeaderFixedWidthElement(size = 1, conversion = plugins.common_func.getString,  error = plugins.common_basetypes.ErrorLevel.ERROR,  casting = plugins.TekTronixLLWFM_Reader_helper.LLWFMLengthConvert,      post = plugins.TekTronixLLWFM_Reader_helper.LLWFMLengthPost,    validate = plugins.TekTronixLLWFM_Reader_helper.LLWFMLengthVerification),
                LLWFMHeaderElements.LLWFMFileLength : plugins.common_basetypes.HeaderFixedWidthElement(size = 0, conversion = plugins.common_func.getString,  error = plugins.common_basetypes.ErrorLevel.ERROR,  casting = plugins.TekTronixLLWFM_Reader_helper.LLWFMFileLengthConvert,  post = None,                                                    validate = plugins.TekTronixLLWFM_Reader_helper.LLWFMFileLengthVerification)
            }
            self.setOrder(">")
        #end
    #end

    class __LLWFMWaveformHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = LLWFMWaveformHeaderElements
            self.HEADER_DEFINITION = {
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown1         : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getByteArray,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformDataSize1              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,     error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = plugins.TekTronixLLWFM_Reader_helper.LLWFMWaveformDataSizeVerification),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown2         : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getByteArray,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown3         : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown4         : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown5         : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderSampleMode1      : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderSampleMode2      : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown6         : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderCouplingMode     : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderSampleUnits      : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getString,         error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderXAxisIncrement   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown7         : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYZeroReference   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYSampleOffset    : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYSampleScaling   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,         error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderNumberOfPoints1  : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderXAxisTrigger     : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getSignedShort,    error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderSampleMode3      : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderSampleMode4      : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,  error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderNumberOfPoints2  : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getSignedShort,    error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = None),
                LLWFMWaveformHeaderElements.LLWFMWaveformHeaderUnknown8         : plugins.common_basetypes.HeaderFixedWidthElement(size = 30, conversion = plugins.common_func.getByteArray,      error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None)
            }
            self.setOrder(">")
        #end
    #end

    class __LLWFMWaveformConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = LLWFMWaveformElements
            self.HEADER_DEFINITION = {
                LLWFMWaveformElements.LLWFMWaveform                             : plugins.common_basetypes.HeaderFixedWidthElement(size = 0, conversion = plugins.common_func.getSignedShortArray,    error = plugins.common_basetypes.ErrorLevel.WARNING,    casting = None, post = None, validate = None)
            }
        #end
    #end

    class __LLWFMChecksumElementsConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = LLWFMChecksumElements
            self.HEADER_DEFINITION = {
                LLWFMChecksumElements.LLWFMChecksum                             : plugins.common_basetypes.HeaderFixedWidthElement(size = 2, conversion = plugins.common_func.getUnsignedShort,   error = plugins.common_basetypes.ErrorLevel.ERROR,      casting = None, post = None, validate = plugins.TekTronixLLWFM_Reader_helper.LLWFMChecksumVerification)
            }
            self.setOrder(">")
        #end
    #end

    class WFMCurveBufferElements() :
        WFMCurveBufferPreCharge                             = 0
        WFMCurveBufferPostCharge                            = 1 + WFMCurveBufferPreCharge
        WFMCurveBuffer                                      = 1 + WFMCurveBufferPostCharge
    #end

    __kTimes        = None
    __kWaveform     = None

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :

        # Read the Decoder Options
        kOptions        = self.getOptions(kPluginOptions=kPluginOptions)

        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        # Waveform Static Header
        kHeaderConstants         = self.__LLWFMHeaderConstants()
        kWaveformHeaderConstants = self.__LLWFMWaveformHeaderConstants()
        kWaveformConstants       = self.__LLWFMWaveformConstants()
        kChecksumConstants       = self.__LLWFMChecksumElementsConstants()
        kAllConstants = {
            "LLWFMHeaderConstants"              : kHeaderConstants,
            "LLWFMWaveformHeaderConstants"      : kWaveformHeaderConstants,
            "LLWFMWaveformConstants"            : kWaveformConstants,
            "LLWFMChecksumElementsConstants"    : kChecksumConstants 
        }

        # Update the Waveform Byte Order
        kWaveformConstants.setOrder(kOrder=kOptions["ByteOrder"])

        # Perform all Decoding / Acquisition in the Header, thereby making the remaining
        # usage a simple series of accessor methods.
        self._kWFM = {}

        # Decode the Static Header First
        self.__encodeLLWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=0, kWFM=self._kWFM, kIndex=LLWFMHeaderElements, kHeaderElement=LLWFMElements.LLWFMHeader, bReevaluateSize=True, kHeaderConstants=kHeaderConstants, kAllConstants=kHeaderConstants, kErrorHandling=kErrorHandling)

        # Update the Waveform Length which can be derived from the File Size
        kWaveformConstants.HEADER_DEFINITION[LLWFMWaveformElements.LLWFMWaveform].size = self._kWFM[LLWFMElements.LLWFMHeader][LLWFMHeaderElements.LLWFMFileLength] - \
                                                                                         kWaveformHeaderConstants.size() - \
                                                                                         kChecksumConstants.size()

        # Decode the File Checksum
        self.__encodeLLWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=kHeaderConstants.size() + kWaveformHeaderConstants.size() + kWaveformConstants.size(bForce=True), kWFM=self._kWFM, kIndex=LLWFMChecksumElements, kHeaderElement=LLWFMElements.LLWFMWaveformFileChecksum, bReevaluateSize=False, kHeaderConstants=kChecksumConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Decode the Waveform Header
        self.__encodeLLWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=kHeaderConstants.size(), kWFM=self._kWFM, kIndex=LLWFMWaveformHeaderElements, kHeaderElement=LLWFMElements.LLWFMWaveformHeader, bReevaluateSize=False, kHeaderConstants=kWaveformHeaderConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Decode the Raw Waveform
        self.__encodeLLWFMHeader  (kBufferRaw=self.__kByteBuffer, nOffset=kHeaderConstants.size() + kWaveformHeaderConstants.size(), kWFM=self._kWFM, kIndex=LLWFMWaveformElements, kHeaderElement=LLWFMElements.LLWFMCurveBuffer, bReevaluateSize=False, kHeaderConstants=kWaveformConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Extract the Number of Points
        nPoints = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderNumberOfPoints1]

        # Extract the X Axis
        nXMult  = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderXAxisIncrement]
        nXOff   = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderXAxisTrigger] * (nPoints / 100.0)
        nXZero  = 0.0

        # Extract the Y Axis
        nYZERO  = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYZeroReference]
        # TODO: I'm struggling to believe this, but the constants appear to be fixed?  Using the TekTronix LLWFM -> ISF converter, having
        #       corrupted all other bits other than the identifier and the digits/length, and these two doubles, they always seem to use this
        #       fixed scaling factor, but that could just be an error in the converter.  Need real waveforms with known values for this.
        nYOFF   = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYSampleOffset] * 25.0
        nYMULT  = self._kWFM[LLWFMElements.LLWFMWaveformHeader][LLWFMWaveformHeaderElements.LLWFMWaveformHeaderYSampleScaling] / 25.0

        # Calculate the Total Number of Points in the File
        nPointsLength = self._kWFM[LLWFMElements.LLWFMHeader][LLWFMHeaderElements.LLWFMFileLength] - kWaveformHeaderConstants.size() - kChecksumConstants.size() # Subtract Header/Checsum Length and divide by the Data Length
        nPointsInFile = nPointsLength // 2 
        nPreLength    = (nPointsInFile - nPoints) // 2
        nPostLength   = nPreLength

        # TODO: Annoyingly the data is either 8 bits with 8 bits padding, or 16 bits.  It's unclear whether there's anything in the header to dicate this.
        #       And the conversion tool forces this to be externally defined, as such, we're going to either allow this to be forced, or try and auto-detect
        #       based on the contents of the waveform itself.
        if 0 == kOptions["DataWidth"] :
            kRawData     = self._kWFM[LLWFMElements.LLWFMCurveBuffer][LLWFMWaveformElements.LLWFMWaveform]
            if all([(X & 0x00FF) == 0 for X in kRawData]) :
                kDecodedData = [X >> 8 for X in kRawData]
            else :
                 # Note: The CSV Convertor will *still* perform a Shift, which seems... wrong.
                kDecodedData = kRawData
#                kDecodedData = [X >> 8 for X in kRawData]
            #end
        elif 8 == kOptions["DataWidth"] :
            kDecodedData = [X >> 8 for X in self._kWFM[LLWFMElements.LLWFMCurveBuffer][LLWFMWaveformElements.LLWFMWaveform]]
            # self._kWFM[LLWFMElements.LLWFMCurveBuffer][LLWFMWaveformElements.LLWFMWaveform]
        elif 16 == kOptions["DataWidth"] :
            # Note: The CSV Convertor will *still* perform a Shift, which seems... wrong.
            kDecodedData = self._kWFM[LLWFMElements.LLWFMCurveBuffer][LLWFMWaveformElements.LLWFMWaveform]
#            kDecodedData = [X >> 8 for X in self._kWFM[LLWFMElements.LLWFMCurveBuffer][LLWFMWaveformElements.LLWFMWaveform]]
        else :
            assert(False)
        #end

        self.__kWaveform = {
            self.WFMCurveBufferElements.WFMCurveBufferPreCharge  : [nYZERO + (nYMULT * (Y - nYOFF)) for Y in kDecodedData[:nPreLength]],
            self.WFMCurveBufferElements.WFMCurveBufferPostCharge : [nYZERO + (nYMULT * (Y - nYOFF)) for Y in kDecodedData[nPreLength + nPoints:]],
            self.WFMCurveBufferElements.WFMCurveBuffer           : [nYZERO + (nYMULT * (Y - nYOFF)) for Y in kDecodedData[nPreLength:nPreLength + nPoints]],
        }

        self.__kTimes    = {
            self.WFMCurveBufferElements.WFMCurveBufferPreCharge  : [nXZero + (nXMult * (X - nPreLength - nXOff)) for X in range(nPreLength)],
            self.WFMCurveBufferElements.WFMCurveBufferPostCharge : [nXZero + (nXMult * (X + nPoints    - nXOff)) for X in range(nPostLength)],
            self.WFMCurveBufferElements.WFMCurveBuffer           : [nXZero + (nXMult * (X -              nXOff)) for X in range(nPoints)],
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

    @classmethod
    def getOptions(self, kPluginOptions : dict = None) -> dict:

        kOptions = {
            "DataWidth" : 0,
            "ByteOrder" : ">"
        }

        if None != kPluginOptions :

            for kKey, kData in kPluginOptions.items() :

                if kKey not in kOptions :
                    assert(False)
                #end

                kOptions[kKey] = kData

            #end

        #end

        return kOptions

    #end

    @classmethod
    def isValid(self, kFileBuffer : bytearray, kPluginOptions : dict = None) -> bool :

        try :

            self.__LLWFMHeaderConstants().getElement(None, kFileBuffer, None, 0, LLWFMHeaderElements.LLWFMHeader, None, None, ErrorLevelHandling.NORMAL)

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

    # Can all these be refactored somehow... the code is basically identical with thge exception of the length oddity on the first call

    def __encodeLLWFMHeader(self, kBufferRaw : bytes, nOffset : int, kWFM : dict, kIndex, kHeaderElement, bReevaluateSize : bool, kHeaderConstants, kAllConstants : dict, kErrorHandling : ErrorLevelHandling) :

        kWFM[kHeaderElement] = {}
        kHeader              = kWFM[kHeaderElement]

        nBufferedLength      = kHeaderConstants.size()
        kRawBytesForHeader   = kBufferRaw[nOffset:nOffset+nBufferedLength]

        # Decode the Header Data
        if bReevaluateSize :
            for e in kIndex :
                kHeaderConstants.storeElement(kRawBytesForBlock=kRawBytesForHeader, kAllConstants=kAllConstants, kRawBytesForFile=kBufferRaw, nOffset=nOffset, kElement=e, kTarget=kHeader, kFullTarget=kWFM, kErrorHandling=kErrorHandling)
                if nBufferedLength != kHeaderConstants.size(True) :
                    nBufferedLength    = kHeaderConstants.size()
                    kRawBytesForHeader = kBufferRaw[nOffset:nOffset+nBufferedLength]
                #end
            #end
        else :
            for e in kIndex :
                kHeaderConstants.storeElement(kRawBytesForBlock=kRawBytesForHeader, kAllConstants=kAllConstants, kRawBytesForFile=kBufferRaw, nOffset=nOffset, kElement=e, kTarget=kHeader, kFullTarget=kWFM, kErrorHandling=kErrorHandling)
            #end
        #end

    #end

#end