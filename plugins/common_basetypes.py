import array
import enum
import plugins.common_errorhandler
import plugins.common_func
import typing

# Note: Data Classes are slower, as they're essentially dictionary lookups under the hood
class HeaderFixedWidthElement() :

    def __init__(self, size : int, conversion : typing.Callable, error : typing.Callable, casting : typing.Callable, post : typing.Callable, validate : typing.Callable) :
        self.size       = size
        self.conversion = conversion
        self.error      = error
        self.casting    = casting
        self.post       = post
        self.validate   = validate
    #end

    size       : int
    conversion : typing.Callable
    error      : typing.Callable
    casting    : typing.Callable
    post       : typing.Callable
    validate   : typing.Callable

#end

# Note: Data Classes are slower, as they're essentially dictionary lookups under the hood
class HeaderTaggedElement() :

    def __init__(self, name : str, min_count : int, max_count : int, decode : typing.Callable, error : int, casting : typing.Callable, post : typing.Callable, validate : typing.Callable) :
        self.name       = name
        self.min_count  = min_count
        self.max_count  = max_count
        self.decode     = decode
        self.error      = error
        self.casting    = casting
        self.post       = post
        self.validate   = validate
    #end

    name       : str
    min_count  : int
    max_count  : int
    decode     : typing.Callable
    error      : int
    casting    : typing.Callable
    post       : typing.Callable
    validate   : typing.Callable

#end

class ErrorLevel() :
    WARNING     = 0
    ERROR       = 1
#end

class ErrorLevelHandling() :
    NONE        = 0 # No Warnings or Errors
    INFO        = 1 # Everything as Warning
    NORMAL      = 2 # Warnings as Warnings, Errors as Errors
    ALL         = 3 # Everything as Error
#end

class Reader() :

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :
        assert(False)
    #end

    def __enter__(self) :
        assert(False)
    #end

    def __exit__(self, type, value, traceback) :
        assert(False)
    #end

    def __iter__(self) :
        assert(False)
    #end

    @classmethod
    def isValid(self, kFileBuffer : bytearray, kPluginOptions : dict = None) -> bool :
        assert(False)
    #end

    def getWaveform(self) -> list :
        assert(False)
    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        assert(False)
    #end

#end

class GenericBaseClass() :

    # Note: This is a bit of a special case.  The method is primarily invoked statically based on the enum
    #       type.

    @classmethod
    def convert(self, kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :

        _T = self()
        for e in dir(self) :
            if not callable(getattr(_T, e)) and not e.startswith("__") :
                if getattr(_T, e) == kUnconvertedValue :
                    return kUnconvertedValue
                #end
            #end
        #end
        return self.INVALID
    #end

#end

@enum.unique
#class GenericBaseEnum(enum.IntEnum) :
class GenericBaseEnum(enum.Enum) :

    # Note: This is a bit of a special case.  The method is primarily invoked statically based on the enum
    #       type.

    @classmethod
    def convert(self, kUnconvertedValue, kAllConstants, kTarget, kFullTarget, kElement, kRawBytesForFile) :

        for e in self :
            if e.value == kUnconvertedValue :
                return e
            #end
        #end
        return self.INVALID
    #end

#end

# Uncomment this if you'd really rather use Enums throughout.
# GenericBaseClass = GenericBaseEnum

# This is used for text headers whereby the contents are stored using some form of tagging.
# Note: This is for *FLAT* hierarchies only.  If something requires nesting, it must either
#       first be flattened, or use some form of tree based parsing.
class GenericTaggedConstants() :

    __REVERSE_LOOKUP = None

    def createReverseLookup(self) :

        self.__REVERSE_LOOKUP = {}
        for e, d in self.HEADER_DEFINITION.items() :
            self.__REVERSE_LOOKUP[d.name] = e
        #end

    #end

    def storeElements(self, kData : dict, kElements, kAllConstants : dict, kTarget : dict, kFullTarget : dict, kErrorHandling : ErrorLevelHandling) :

        # Part 1: Parse the data and store the elements
        for e, d in kData.items() :

            e = self.__REVERSE_LOOKUP[e]
            if self.HEADER_DEFINITION[e].max_count > 1 :
                if e not in kTarget :
                    kTarget[e] = []
                #end

                if len(kTarget[e]) >= self.HEADER_DEFINITION[e].max_count :
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"Too many instances of {e}=0x" + "".join([f"{k:02X}" for k in d]) + f" found, max = {self.HEADER_DEFINITION[e].max_count}.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
                    continue
                #end

                kTarget[e].append(self.getElement(kElement=e, kByteBuffer=d, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kErrorHandling=kErrorHandling))

            elif self.HEADER_DEFINITION[e].max_count == 1 :
                if e in kTarget :
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"Multiple instances of {e}=0x" + "".join([f"{k:02X}" for k in d]) + f" found.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
                    continue
                #end
                kTarget[e] = self.getElement(kElement=e, kByteBuffer=d, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kErrorHandling=kErrorHandling)
            else :
                plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"One or more instances of {e}=0x" + "".join([f"{k:02X}" for k in d]) + f" found.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
            #end

        #end

        # Part 2: For all data items, perform the Validation
        #
        # Note: This performed separately *because* unliked fixed constants, whereby the parse order is predictable, with tagged constants,
        #       we really need all the data to be parsed in a preliminary fashion in order to validate data elements which have dependencies.
        for e,d in kData.items() :

            e = self.__REVERSE_LOOKUP[e]
            assert(e in kTarget)

            if list == type(kTarget[e]) :
                for kPair in kTarget[e] :
                    self.validateElement(kConvertedValue=kPair[0], kUnconvertedValue=kPair[1], kElement=e, kByteBuffer=d, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kErrorHandling=kErrorHandling)
                #end
            else :
                self.validateElement(kConvertedValue=kTarget[e][0], kUnconvertedValue=kTarget[e][1], kElement=e, kByteBuffer=d, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kErrorHandling=kErrorHandling)
            #end

        #end

        # Part 3: Store only the Converted Data
        for e,d in kData.items() :

            e = self.__REVERSE_LOOKUP[e]
            assert(e in kTarget)

            if list == type(kTarget[e]) :
                for i, kPair in enumerate(kTarget[e]) :
                    kTarget[e][i] = kPair[0]
                #end
            else :
                kTarget[e] = kTarget[e][0]
            #end

        #end

        # Part 4: Ensure all required data is present
        for e in kElements :

            nMinCount = self.HEADER_DEFINITION[e].min_count

            if nMinCount > 1 :

                if e not in kTarget :
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"No instances of {e} found.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
                else :
                    nInstances = len(kTarget[e])
                    if nInstances < self.HEADER_DEFINITION[e].min_count :
                        plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"Too few instances of {e} found, min = {self.HEADER_DEFINITION[e].min_count}.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
                    #end
                #end

            elif nMinCount == 1 :

                if e not in kTarget :
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=f"No instances of {e} found.", kErrorLevel=self.HEADER_DEFINITION[e].error, kErrorHandling=kErrorHandling)
                #end

            #end

        #end

    #end

    def getElement(self, kElement, kByteBuffer : bytes(), kAllConstants : dict, kTarget : dict, kFullTarget : dict, kErrorHandling : ErrorLevelHandling) :

        # Try to prevent multiple hash lookups
        kHeaderElement = self.HEADER_DEFINITION[kElement]

        # Extract the Unconverted Value
        kUnconvertedValue = kByteBuffer

        # Extract the Decoded Value
        kDecodedValue = kByteBuffer
        if None != kHeaderElement.decode :
            kDecodedValue = kHeaderElement.decode(kByteBuffer=kDecodedValue)
        #end

        # Convert the Value
        kConvertedValue   = kDecodedValue
        if None != kConvertedValue :
            if None != kHeaderElement.casting :
                kConvertedValue = kHeaderElement.casting(kUnconvertedValue=kConvertedValue, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=bytes())
            #end

            # Perform the Post Steps
            if None != kHeaderElement.post :
                kHeaderElement.post(self=self, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kConvertedValue=kConvertedValue, kRawBytesForFile=bytes())
            #end
        #end

        return tuple([kConvertedValue, kUnconvertedValue])

    #end

    def validateElement(self, kConvertedValue, kUnconvertedValue, kElement, kByteBuffer : bytes(), kAllConstants : dict, kTarget : dict, kFullTarget : dict, kErrorHandling : ErrorLevelHandling) :

        # Try to prevent multiple hash lookups
        kHeaderElement = self.HEADER_DEFINITION[kElement]

        # Validate the Unconverted/Converted Value
        if kErrorHandling != ErrorLevelHandling.NONE :

            if (None == kConvertedValue) or (None != kHeaderElement.validate) :

                if None == kConvertedValue :

                    kErrorMessage = f"Invalid Data detected for {kElement.name} 0x" + "".join([f"{k:02X}" for k in kByteBuffer])
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=kErrorMessage, kErrorLevel=kHeaderElement.error, kErrorHandling=kErrorHandling)

                elif False == kHeaderElement.validate(self=self, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kConvertedValue=kConvertedValue, kUnconvertedValue=kUnconvertedValue, kRawBytesForFile=bytes(), nElementOffsetWithinFile=0) :

                    kErrorMessage = f"Invalid Data detected for {kElement.name} 0x" + "".join([f"{k:02X}" for k in kByteBuffer])
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=kErrorMessage, kErrorLevel=kHeaderElement.error, kErrorHandling=kErrorHandling)

                #end

            #end

        #end

    #end

#end

# This is used for binary headers whereby the contents primarily follow a fixed layout.
class GenericFixedWidthConstants() :

    _SIZE    = None
    _ORDER   = ""

    def setOrder(self, kOrder : str) -> str :
        self._ORDER = kOrder
    #end

    def storeElement(self, kAllConstants : dict, kRawBytesForBlock : bytes, kRawBytesForFile : bytes, nOffset : int, kElement, kTarget : dict, kFullTarget : dict, kErrorHandling : ErrorLevelHandling) :

        # Store the Converted Value
        kTarget[kElement] = self.getElement(kAllConstants, kRawBytesForBlock, kRawBytesForFile, nOffset, kElement, kTarget, kFullTarget, kErrorHandling)

    #end

    def getElement(self, kAllConstants : dict, kRawBytesForBlock : bytes, kRawBytesForFile : bytes, nOffset : int, kElement, kTarget : dict, kFullTarget : dict, kErrorHandling : ErrorLevelHandling) :

        # Try to prevent multiple hash lookups
        kHeaderElement = self.HEADER_DEFINITION[kElement]

        # Handle the Case where a Header Element has been deliberately stubbed out
        if 0 == kHeaderElement.size :
            return
        #end

        # Extract the Unconverted Value
        nOffsetWithinBlock = self.offset(kElement=kElement)
        nSize   = kHeaderElement.size
        if (nOffsetWithinBlock + nSize) > len(kRawBytesForBlock) :
            kUnconvertedValue = None
        else :
            kUnconvertedValue = kHeaderElement.conversion(kByteArray = kRawBytesForBlock,
                                                          kOrder     = self._ORDER,
                                                          nOffset    = nOffsetWithinBlock,
                                                          nSize      = nSize)
        #end

        # Convert the Value
        kConvertedValue   = kUnconvertedValue
        if None != kConvertedValue :
            if None != kHeaderElement.casting :
                kConvertedValue = kHeaderElement.casting(kUnconvertedValue=kUnconvertedValue, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kRawBytesForFile=kRawBytesForFile)
            #end

            # Perform the Post Steps
            if None != kHeaderElement.post :
                kHeaderElement.post(self=self, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kConvertedValue=kConvertedValue, kRawBytesForFile=kRawBytesForFile)
            #end
        #end

        # Validate the Unconverted/Converted Value
        if kErrorHandling != ErrorLevelHandling.NONE :

            if (None == kConvertedValue) or (None != kHeaderElement.validate) :

                nOffsetWithinFile  = nOffsetWithinBlock + nOffset
                nPossibleSize      = min(nSize, len(kRawBytesForBlock) - nOffsetWithinBlock)
                if nPossibleSize <= 0 :
                    kRaw = bytearray()
                else :
                    kRaw               = plugins.common_func.getByteArray(kByteArray = kRawBytesForBlock,
                                                                          kOrder     = self._ORDER,
                                                                          nOffset    = nOffsetWithinBlock,
                                                                          nSize      = min(nSize, nPossibleSize))
                #end

                if None == kConvertedValue :

                    kErrorMessage = f"Invalid Data detected for {kElement.name} [0x{nOffsetWithinFile:08X}] 0x" + "".join([f"{k:02X}" for k in kRaw])
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=kErrorMessage, kErrorLevel=kHeaderElement.error, kErrorHandling=kErrorHandling)

                elif False == kHeaderElement.validate(self=self, kAllConstants=kAllConstants, kTarget=kTarget, kFullTarget=kFullTarget, kElement=kElement, kConvertedValue=kConvertedValue, kUnconvertedValue=kUnconvertedValue, kRawBytesForFile=kRawBytesForFile, nElementOffsetWithinFile=nOffsetWithinFile) :

                    kErrorMessage = f"Invalid Data detected for {kElement.name} [0x{nOffsetWithinFile:08X}] 0x" + "".join([f"{k:02X}" for k in kRaw])
                    plugins.common_errorhandler.ErrorHandler(kErrorMessage=kErrorMessage, kErrorLevel=kHeaderElement.error, kErrorHandling=kErrorHandling)

                #end

            #end

        #end

        return kConvertedValue

    #end

    # TODO: Caching has been disabled from offset.  The main issue is that size/offsets are often changed
    #       due to file versioning etc., so caching actively gets in the way.  Much of this is because
    #       the Header Dict is directly accessible, and not guarded by accessors/mutators, meaning the
    #       data can be changed post caching.  Size has a rubbish workaround to "force" re-calculation,
    #       however it would be better if the re-caching was triggered by mutators.  It could then just
    #       be handled incrementally rather than invalidating / re-calculating.

    # Note: This caches the Offsets to try to reduce the overhead of progressive parsing
    def offset(self, kElement) -> int :

        nOffset = 0
        for e in self.HEADER_TYPE :
            if e == kElement :
                return nOffset
            #end
            nOffset += self.HEADER_DEFINITION[e].size
        #end

        assert(False)

    #end

    # Note: This caches the Offsets to try to reduce the overhead of progressive parsing
    def size(self, bForce=False) -> int :

        if bForce or (None == self._SIZE) :

            nSize = 0
            for e in self.HEADER_TYPE :
                if e in ["__module__"] : continue
                nSize += self.HEADER_DEFINITION[e].size
            #end
            self._SIZE = nSize

        #end

        return self._SIZE

    #end

#end
