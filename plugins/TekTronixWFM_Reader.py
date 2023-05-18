# TekTronixWFM_Reader
#
# Scope Types: TDS5000/B, TDS6000/B/C, TDS/CSA7000/B, DPO7000, DPO70000 and DSA70000 Series.
#
# Expected File Extention: .wfm

from plugins.TekTronixWFM_Reader_types import *
from plugins.common_basetypes import ErrorLevelHandling

import plugins.common_func
import plugins.common_basetypes
import plugins.common_errorhandler
import plugins.TekTronixWFM_Reader_helper

import typing
import array

class Reader(plugins.common_basetypes.Reader):

    class __WFMHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            # Default to Intel Order, this will promptly be overrridden once the WFMByteOrderVerification is
            # parsed, as this is specifically designed to return the same data irrespective of byte order,
            # making this initial state arbitrary.
            #
            # Note: This is needed, as struct.unpack behaves weirdly on my M1 Mac if an order isn't specified.
            self._ORDER            = "<"
            self.HEADER_TYPE       = WFMHeaderElements
            self.HEADER_DEFINITION = {
                WFMHeaderElements.WFMByteOrderVerification              : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,                          error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMByteOrderVerificationType.convert,   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMByteOrderVerification),
                WFMHeaderElements.WFMVersionNumber                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getString,                                 error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = plugins.TekTronixWFM_Reader_helper.WFMVersionNumberPost, validate = plugins.TekTronixWFM_Reader_helper.WFMVersionNumberVerification),
                WFMHeaderElements.WFMNumberOfDigitsInByteCount          : plugins.common_basetypes.HeaderFixedWidthElement(size = 1,  conversion = plugins.common_func.getSignedChar,                             error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMNumberOfDigitsInByteCountVerification),
                WFMHeaderElements.WFMNumberOfBytesToTheEndOfFile        : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMNumberOfBytesToTheEndOfFileVerification),
                WFMHeaderElements.WFMNumberOfBytesPerPoint              : plugins.common_basetypes.HeaderFixedWidthElement(size = 1,  conversion = plugins.common_func.getUnsignedChar,                           error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMNumberOfBytesPerPointVerification),
                WFMHeaderElements.WFMByteOffsetToBeginningOfCurveBuffer : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMByteOffsetToBeginningOfCurveBufferVerification),
                WFMHeaderElements.WFMHorizontalZoomScaleFactor          : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # Flagged as Not For Use
                WFMHeaderElements.WFMHorizontalZoomPosition             : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # Flagged as Not For Use
                WFMHeaderElements.WFMVerticalZoomScaleFactor            : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,                                 error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # Flagged as Not For Use
                WFMHeaderElements.WFMVerticalZoomPosition               : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getFloat,                                  error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # Flagged as Not For Use
                WFMHeaderElements.WFMWaveFormLabel                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 32, conversion = plugins.common_func.getString,                                 error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # N/A
                WFMHeaderElements.WFMNumberOfFastFramesMinusOne         : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,                           error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                    validate = None), # N/A
                WFMHeaderElements.WFMSizeOfWaveFormHeaderBytes          : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,                          error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                    validate = plugins.TekTronixWFM_Reader_helper.WFMSizeOfWaveFormHeaderBytesVerification)
            }
        #end
    #end

    class __WFMWaveformHeaderConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :

            self.WFMWaveformFormat = WFMWaveformFormatV2

            self.HEADER_TYPE       = WFMWaveformHeaderElements
            self.HEADER_DEFINITION = {
                WFMWaveformHeaderElements.WFMSetType                                          : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformSetType.convert,             post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMSetTypeVerification),
                WFMWaveformHeaderElements.WFMCnt                                              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMCntVerification),
                WFMWaveformHeaderElements.WFMAcquisitionCounter                               : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getUnsignedLongLong, error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMTransactionCounter                               : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getUnsignedLongLong, error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMSlotID                                           : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMIsStaticFlag                                     : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMUpdateSpecificationCount                         : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # TODO: Check this
                WFMWaveformHeaderElements.WFMImpDimRefCount                                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Needs Data Type / Pix Map Display Format to validate
                WFMWaveformHeaderElements.WFMExpDimRefCount                                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Needs Data Type / Pix Map Display Format to validate
                WFMWaveformHeaderElements.WFMDataType                                         : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformDataType.convert,            post = None,                                                             validate = None), # Pix Map Display Format to validate
                WFMWaveformHeaderElements.WFMGenPurposeCounter                                : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getUnsignedLongLong, error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMAccumulatedWaveformCount                         : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMTargetAccumulationCount                          : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMCurveRefCount                                    : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMCurveRefCountVerification),
                WFMWaveformHeaderElements.WFMNumberOfRequestedFastFrames                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Fast Frames is Optional
                WFMWaveformHeaderElements.WFMNumberOfAcquiredFastFrames                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # TODO: Unclear how this would relate to the request, could it ever be larger?  Plus I have no waveforms with this present.
                WFMWaveformHeaderElements.WFMSummaryFrame                                     : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,    error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformSummaryFrame.convert,        post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMWaveformSummaryFrameVerification),
                WFMWaveformHeaderElements.WFMPixMapDisplayFormat                              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformPixMapDisplayFormat.convert, post = None,                                                             validate = None), # Unclear how this relates to Data Type
                WFMWaveformHeaderElements.WFMPixMapMaxValue                                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getUnsignedLongLong, error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Unclear how this relates to Data Type

                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimScale,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimScale],      plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimOffset,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimOffset],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimSize,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimSize],       plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1Units,
                                WFMWaveformHeaderElements.WFMExplicitDimension2Units],         plugins.common_basetypes.HeaderFixedWidthElement(size = 20, conversion = plugins.common_func.getString,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # User Defined, nothing to check.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimExtentMin,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimExtentMin],  plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # Flagged as Not For Use
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimExtentMax,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimExtentMax],  plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # Flagged as Not For Use
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimResolution,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimResolution], plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1DimRefPoint,
                                WFMWaveformHeaderElements.WFMExplicitDimension2DimRefPoint],   plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1Format,
                                WFMWaveformHeaderElements.WFMExplicitDimension2Format],        plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = self.WFMWaveformFormat.convert,         post = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionFormatPost, validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionFormatVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1StorageType,
                                WFMWaveformHeaderElements.WFMExplicitDimension2StorageType],   plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformStorageType.convert,         post = None,                                                              validate = None)), # TODO: Verification needs to know wave form type to determine if a value is expected.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1NValue,
                                WFMWaveformHeaderElements.WFMExplicitDimension2NValue],        plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,       error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionNValuePost, validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionNValueVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1OverRange,
                                WFMWaveformHeaderElements.WFMExplicitDimension2OverRange],     plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,       error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionOverRangeVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1UnderRange,
                                WFMWaveformHeaderElements.WFMExplicitDimension2UnderRange],    plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,       error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionUnderRangeVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1HighRange,
                                WFMWaveformHeaderElements.WFMExplicitDimension2HighRange],     plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,       error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1LowRange,
                                WFMWaveformHeaderElements.WFMExplicitDimension2LowRange],      plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getSignedLong,       error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionLowRangeVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1UserScale,
                                WFMWaveformHeaderElements.WFMExplicitDimension2UserScale],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1UserUnits,
                                WFMWaveformHeaderElements.WFMExplicitDimension2UserUnits],     plugins.common_basetypes.HeaderFixedWidthElement(size = 20, conversion = plugins.common_func.getString,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1UserOffset,
                                WFMWaveformHeaderElements.WFMExplicitDimension2UserOffset],    plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1PointDensity,
                                WFMWaveformHeaderElements.WFMExplicitDimension2PointDensity],  plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionPointDensityVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1HRef,
                                WFMWaveformHeaderElements.WFMExplicitDimension2HRef],          plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMExplicitDimensionHRefVerification)),
                **dict.fromkeys([WFMWaveformHeaderElements.WFMExplicitDimension1TrigDelay,
                                WFMWaveformHeaderElements.WFMExplicitDimension2TrigDelay],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid

                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimScale,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimScale],      plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimOffset,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimOffset],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimSize,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimSize],       plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1Units,
                                WFMWaveformHeaderElements.WFMImplicitDimension2Units],         plugins.common_basetypes.HeaderFixedWidthElement(size = 20, conversion = plugins.common_func.getString,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # User Defined, nothing to check.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimExtentMin,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimExtentMin],  plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # Flagged as Not For Use
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimExtentMax,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimExtentMax],  plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # Flagged as Not For Use
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimResolution,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimResolution], plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1DimRefPoint,
                                WFMWaveformHeaderElements.WFMImplicitDimension2DimRefPoint],   plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1Spacing,
                                WFMWaveformHeaderElements.WFMImplicitDimension2Spacing],       plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1UserScale,
                                WFMWaveformHeaderElements.WFMImplicitDimension2UserScale],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1UserUnits,
                                WFMWaveformHeaderElements.WFMImplicitDimension2UserUnits],     plugins.common_basetypes.HeaderFixedWidthElement(size = 20, conversion = plugins.common_func.getString,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # User Defined, nothing to check.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1UserOffset,
                                WFMWaveformHeaderElements.WFMImplicitDimension2UserOffset],    plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1PointDensity,
                                WFMWaveformHeaderElements.WFMImplicitDimension2PointDensity],  plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1HRef,
                                WFMWaveformHeaderElements.WFMImplicitDimension2HRef],          plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: This can be verified, but it's based on the waveform type.
                **dict.fromkeys([WFMWaveformHeaderElements.WFMImplicitDimension1TrigDelay,
                                WFMWaveformHeaderElements.WFMImplicitDimension2TrigDelay],     plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification)), # Assume this has to be valid

                **dict.fromkeys([WFMWaveformHeaderElements.WFMTimeBase1RealPointSpacing,
                                WFMWaveformHeaderElements.WFMTimeBase2RealPointSpacing],       plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                              validate = None)), # TODO: Probably related to the Waveform
                **dict.fromkeys([WFMWaveformHeaderElements.WFMTimeBase1Sweep,
                                WFMWaveformHeaderElements.WFMTimeBase2Sweep],                  plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformSweep.convert,               post = None,                                                              validate = None)), # TODO: Probably related to the Waveform
                **dict.fromkeys([WFMWaveformHeaderElements.WFMTimeBase1TypeOfBase,
                                WFMWaveformHeaderElements.WFMTimeBase2TypeOfBase],             plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformTypeOfBase.convert,          post = None,                                                              validate = None)), # TODO: Probably related to the Waveform

                WFMWaveformHeaderElements.WFMUpdateRealPointOffset                            : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                             validate = None),
                WFMWaveformHeaderElements.WFMUpdateTTOffset                                   : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification),
                WFMWaveformHeaderElements.WFMUpdateFracSec                                    : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getDouble,           error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMGenericDoubleVerification),
                WFMWaveformHeaderElements.WFMUpdateGmtSec                                     : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.WARNING, casting = None,                                   post = None,                                                             validate = None),

                WFMWaveformHeaderElements.WFMCurveStateFlags                                  : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getByteArray,        error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = plugins.TekTronixWFM_Reader_helper.WFMCurveStateFlagsPost,        validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMCurveTypeOfCheckSum                              : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = WFMWaveformTypeOfChecksum.convert,      post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMCurveCheckSum                                    : plugins.common_basetypes.HeaderFixedWidthElement(size = 2,  conversion = plugins.common_func.getUnsignedShort,    error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None), # Flagged as Not For Use
                WFMWaveformHeaderElements.WFMCurvePrechargeStartOffset                        : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None),
                WFMWaveformHeaderElements.WFMCurveDataStartOffset                             : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None),
                WFMWaveformHeaderElements.WFMCurvePostchargeStartOffset                       : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None),
                WFMWaveformHeaderElements.WFMCurvePostchargeStopOffset                        : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = None),
                WFMWaveformHeaderElements.WFMCurveEndOfCurveBufferOffset                      : plugins.common_basetypes.HeaderFixedWidthElement(size = 4,  conversion = plugins.common_func.getUnsignedLong,     error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WFMCurveEndOfCurveBufferOffsetVerification) # Verify all the Previous Data Offsets now it's all known
            }
        #end
    #end

    class __WFMFileChecksumConstants(plugins.common_basetypes.GenericFixedWidthConstants) :
        def __init__(self) :
            self.HEADER_TYPE       = WfmFileChecksumElements
            self.HEADER_DEFINITION = {
                WfmFileChecksumElements.WFMWaveformFileChecksum                               : plugins.common_basetypes.HeaderFixedWidthElement(size = 8,  conversion = plugins.common_func.getUnsignedLongLong, error = plugins.common_basetypes.ErrorLevel.ERROR,   casting = None,                                   post = None,                                                             validate = plugins.TekTronixWFM_Reader_helper.WaveformFileChecksumVerification)
            }
        #end
    #end

    __kByteBuffer     = None
    _kWFM             = {}

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :

        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        # Verify the File Checksum First

        # Waveform Static Header
        kHeaderConstants         = self.__WFMHeaderConstants()
        kWaveformHeaderConstants = self.__WFMWaveformHeaderConstants()
        kFileChecksumConstants   = self.__WFMFileChecksumConstants()
        kAllConstants = {
            "WFMHeaderConstants"         : kHeaderConstants,
            "WFMWaveformHeaderConstants" : kWaveformHeaderConstants,
            "WFMFileChecksumConstants"   : kFileChecksumConstants
        }

        # Perform all Decoding / Acquisition in the Header, thereby making the remaining
        # usage a simple series of accessor methods.
        self._kWFM = {}

        # Decode the Static Header First
        # This may seem odd, however the byte swap order contained within is fundamental to *every* block afterwards.
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=0, kWFM=self._kWFM, kIndex=WFMHeaderElements, kHeaderElement=WFMElements.WFMHeader, bEvaluateByteOrder=True, kHeaderConstants=kHeaderConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Decode the File Checksum, which at least indicates if the file is *basically* valid
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=len(self.__kByteBuffer) - kFileChecksumConstants.size(), kWFM=self._kWFM, kIndex=WfmFileChecksumElements, kHeaderElement=WFMElements.WFMWaveformFileChecksum, bEvaluateByteOrder=False, kHeaderConstants=kFileChecksumConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Decode the Wave Form Header
        self.__encodeWFMHeader(kBufferRaw=self.__kByteBuffer, nOffset=kHeaderConstants.size(), kWFM=self._kWFM, kIndex=WFMWaveformHeaderElements, kHeaderElement=WFMElements.WFMWaveformHeader, bEvaluateByteOrder=False, kHeaderConstants=kWaveformHeaderConstants, kAllConstants=kAllConstants, kErrorHandling=kErrorHandling)

        # Decode the Wave Form Curve Buffer
        self.__encodeWfmCurveBuffer(kBufferRaw=self.__kByteBuffer, kWFM=self._kWFM, kErrorHandling=kErrorHandling)

        # Update any known Types that are version dependent in order to allow the user to interrogate/traverse the contents.
        self.WFMWaveformFormat = kWaveformHeaderConstants.WFMWaveformFormat

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
            self.__WFMHeaderConstants().getElement(None, kFileBuffer, None, 0, WFMHeaderElements.WFMByteOrderVerification, None, None, ErrorLevelHandling.NORMAL)
        except Exception as e :
            return False
        #end

        return True

    #end

    def getWaveform(self) -> list :
        # Note: This performs a shallow copy for speed, however it does mean the end user could corrupt the internal state... but that's up to them.
        return self._kWFM[WFMElements.WFMCurveBufferScaled][WFMCurveBufferElements.WFMCurveBuffer]
    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        # Note: If the end user wants to interleave the data differently, they can, however this has been purposefully done as-is for shallow copying.
        return self._kWFM[WFMElements.WFMCurveBufferTimes][WFMCurveBufferElements.WFMCurveBuffer], \
               self._kWFM[WFMElements.WFMCurveBufferScaled][WFMCurveBufferElements.WFMCurveBuffer]
    #end

    def __encodeWFMHeader(self, kBufferRaw : bytes, nOffset : int, kWFM : dict, kIndex, kHeaderElement, bEvaluateByteOrder : bool, kHeaderConstants, kAllConstants : dict, kErrorHandling : ErrorLevelHandling) :

        kWFM[kHeaderElement] = {}
        kHeader              = kWFM[kHeaderElement]

        nBufferedLength      = kHeaderConstants.size()
        kRawBytesForHeader   = kBufferRaw[nOffset:nOffset+nBufferedLength]

        # Special Case for the Static Header
        if bEvaluateByteOrder :
            # Byte Order
            # Note: The data is stored in a byte order indepdent fashion, meaning it will deocde the same irrespective of order, so we just pick an arbitrary one to start with.
            kHeaderConstants.storeElement(kRawBytesForBlock=kRawBytesForHeader, kAllConstants=kAllConstants, kRawBytesForFile=kBufferRaw, nOffset=nOffset, kElement=WFMHeaderElements.WFMByteOrderVerification, kTarget=kHeader, kFullTarget=kWFM, kErrorHandling=kErrorHandling)
            kByteOrder = kHeader[WFMHeaderElements.WFMByteOrderVerification]
            kHeaderConstants.setOrder(WFMByteOrderVerificationType.getOrder(kByteOrder))
        else :
            kHeaderConstants.setOrder(WFMByteOrderVerificationType.getOrder(kWFM[WFMElements.WFMHeader][WFMHeaderElements.WFMByteOrderVerification]))
        #end

        for e in kIndex :
            # Special Case for the Static Header
            if bEvaluateByteOrder :
                if WFMHeaderElements.WFMByteOrderVerification == e : continue
            #end
            kHeaderConstants.storeElement(kRawBytesForBlock=kRawBytesForHeader, kAllConstants=kAllConstants, kRawBytesForFile=kBufferRaw, nOffset=nOffset, kElement=e, kTarget=kHeader, kFullTarget=kWFM, kErrorHandling=kErrorHandling)
        #end

    #end

    def __encodeWfmCurveBuffer(self, kBufferRaw : bytes, kWFM : dict, kErrorHandling : ErrorLevelHandling) :

        def getAndNormaliseAxis(kHeaderElements : dict, kFirst : WFMWaveformHeaderElements, kLast : WFMWaveformHeaderElements, kReference : WFMWaveformHeaderElements) :

            def normaliseAxis(kElement : WFMWaveformHeaderElements, kFirst : WFMWaveformHeaderElements, kReference : WFMWaveformHeaderElements) :
                return WFMWaveformHeaderElements((kElement.value - kFirst.value) + kReference.value)
            #end

            kSlice   = []
            bSlicing = False
            for kEnum in WFMWaveformHeaderElements :
                if kFirst == kEnum :
                    bSlicing = True
                elif kLast == kEnum :
                    bSlicing = False
                #end
                if bSlicing : kSlice.append(kEnum)
            #end

            return {normaliseAxis(kElement=k, kFirst=kFirst, kReference=kReference) : v for k,v in kHeaderElements.items() if k in kSlice}

        #end

        def setDefaults(kWFM : dict) :
            kWFM[WFMElements.WFMCurveBufferTimes] = {
                WFMCurveBufferElements.WFMCurveBufferPreCharge  : [],
                WFMCurveBufferElements.WFMCurveBuffer           : [],
                WFMCurveBufferElements.WFMCurveBufferPostCharge : []
            }
            kWFM[WFMElements.WFMCurveBuffer] = {
                WFMCurveBufferElements.WFMCurveBufferPreCharge  : [],
                WFMCurveBufferElements.WFMCurveBuffer           : [],
                WFMCurveBufferElements.WFMCurveBufferPostCharge : []
            }
            kWFM[WFMElements.WFMCurveBufferScaled] = {
                WFMCurveBufferElements.WFMCurveBufferPreCharge  : [],
                WFMCurveBufferElements.WFMCurveBuffer           : [],
                WFMCurveBufferElements.WFMCurveBufferPostCharge : []
            }
        #end

        try :

            # Calculate the Curve Buffer Pre-Charge/Record/Post-Charge Sizes
            kByteOrder             = WFMByteOrderVerificationType.getOrder(kWFM[WFMElements.WFMHeader][WFMHeaderElements.WFMByteOrderVerification])
            nPreChargeLength       = kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMCurveDataStartOffset]
            nPostChargeLength      = kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMCurvePostchargeStopOffset] - kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMCurvePostchargeStartOffset]
            nDataLength            = kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMCurvePostchargeStartOffset] - nPreChargeLength
            nPreChargeBufferStart  = kWFM[WFMElements.WFMHeader][WFMHeaderElements.WFMByteOffsetToBeginningOfCurveBuffer]
            nDataBufferStart       = nPreChargeBufferStart + nPreChargeLength
            nPostChargeBufferStart = nDataBufferStart + nDataLength

            # Note : We've already Validaated Bytes Per Point / Pre/Post/Curve Lengths
            nWFMNumberOfBytesPerPoint = kWFM[WFMElements.WFMHeader][WFMHeaderElements.WFMNumberOfBytesPerPoint]
            nPreChargeCount   = nPreChargeLength  // nWFMNumberOfBytesPerPoint
            nPostChargeCount  = nPostChargeLength // nWFMNumberOfBytesPerPoint
            nDataCount        = nDataLength       // nWFMNumberOfBytesPerPoint

            # TODO: Interpretting the Curve Buffer Depends on the Curve Type and Data Format
            if WFMWaveformDataType.WFMDATA_VECTOR == kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMDataType] :

                # Time Axis (X)
                kImplicitAxis = getAndNormaliseAxis(kHeaderElements=kWFM[WFMElements.WFMWaveformHeader], kFirst=WFMWaveformHeaderElements.WFMImplicitDimension1DimScale, kLast=WFMWaveformHeaderElements.WFMImplicitDimension2TrigDelay, kReference=WFMWaveformHeaderElements.WFMImplicitDimension1DimScale)

                # Measured Signal (Y)
                kExplicitAxis = getAndNormaliseAxis(kHeaderElements=kWFM[WFMElements.WFMWaveformHeader], kFirst=WFMWaveformHeaderElements.WFMExplicitDimension1DimScale, kLast=WFMWaveformHeaderElements.WFMExplicitDimension1TrigDelay, kReference=WFMWaveformHeaderElements.WFMExplicitDimension1DimScale)

                # Calculate the Start Times
                nTimeDelta           = kImplicitAxis[WFMWaveformHeaderElements.WFMImplicitDimension1DimScale]
                nDataStartTime       = kImplicitAxis[WFMWaveformHeaderElements.WFMImplicitDimension1DimOffset]
                nPreChargeStartTime  = nDataStartTime - (nPreChargeCount * nTimeDelta)
                nPostChargeStartTime = nDataStartTime + (nDataCount      * nTimeDelta)

                # Note: For most of the Data, we use map to effectively yield processing until the data is actually needed.

                # Convert the Waveforms into Unscaled Values
                kPreChargeUnscaled  = plugins.common_func.getSignedShortArrayWithRangeCheck(kByteArray=kBufferRaw, kOrder=kByteOrder, nOffset=nPreChargeBufferStart,  nSize=nPreChargeLength)
                kDataUnscaled       = plugins.common_func.getSignedShortArrayWithRangeCheck(kByteArray=kBufferRaw, kOrder=kByteOrder, nOffset=nDataBufferStart,       nSize=nDataLength)
                kPostChargeUnscaled = plugins.common_func.getSignedShortArrayWithRangeCheck(kByteArray=kBufferRaw, kOrder=kByteOrder, nOffset=nPostChargeBufferStart, nSize=nPostChargeLength)

                # Convert the Waveforms into Scaled Values

                # Store the Implicit Time Axis
                kWFM[WFMElements.WFMCurveBufferTimes] = {
                    WFMCurveBufferElements.WFMCurveBufferPreCharge  : [(nPreChargeStartTime  + (i * nTimeDelta)) for i in range(nPreChargeCount) ],
                    WFMCurveBufferElements.WFMCurveBuffer           : [(nDataStartTime       + (i * nTimeDelta)) for i in range(nDataCount)      ],
                    WFMCurveBufferElements.WFMCurveBufferPostCharge : [(nPostChargeStartTime + (i * nTimeDelta)) for i in range(nPostChargeCount)]
                }

                # Store the Unscaled Values
                kWFM[WFMElements.WFMCurveBuffer] = {
                    WFMCurveBufferElements.WFMCurveBufferPreCharge  : kPreChargeUnscaled,
                    WFMCurveBufferElements.WFMCurveBuffer           : kDataUnscaled,
                    WFMCurveBufferElements.WFMCurveBufferPostCharge : kPostChargeUnscaled
                }

                # Store the Scaled Values
                nScale              = kExplicitAxis[WFMWaveformHeaderElements.WFMExplicitDimension1DimScale]
                nOffset             = kExplicitAxis[WFMWaveformHeaderElements.WFMExplicitDimension1DimOffset] 
                kWFM[WFMElements.WFMCurveBufferScaled] = {
                    WFMCurveBufferElements.WFMCurveBufferPreCharge  : [(nOffset + (k * nScale)) for k in kPreChargeUnscaled],
                    WFMCurveBufferElements.WFMCurveBuffer           : [(nOffset + (k * nScale)) for k in kDataUnscaled],
                    WFMCurveBufferElements.WFMCurveBufferPostCharge : [(nOffset + (k * nScale)) for k in kPostChargeUnscaled]
                }

                return

            #end

        except Exception as e:

            if kErrorHandling in [ErrorLevelHandling.NONE, ErrorLevelHandling.INFO] :
                setDefaults(kWFM)
                return
            #end
            raise e

        #end

        setDefaults(kWFM)
        plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"Sorry, but only {WFMWaveformDataType.WFMDATA_VECTOR.name} is implemented for now.  Your waveform is of type {kWFM[WFMElements.WFMWaveformHeader][WFMWaveformHeaderElements.WFMDataType].name}, please consider contacting me via by Github repo, https://github.com/TonyBUK/ so that I can possibly add this variant.",
                                                 kErrorLevel=plugins.common_basetypes.ErrorLevel.ERROR, kErrorHandling=kErrorHandling)

    #end

#end