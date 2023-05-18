import array
import struct
import typing

def _validateAndGetInput(kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None) :
    
    kByteBuffer = None
    
    # Let's be nice with the Input Type, this was basically borrowed in spirit from png.py.
    # We're basically allowing anything that looks like it's either a file name, or an input data buffer.
    if None == kInput :
        raise TypeError("Reader(FILENAME|FILEBUFFER|BYTES/BYTEARRAY)")
    #end

    # File Name
    if isinstance(kInput, str) :
        with open(kInput, "rb") as kFile :
            kByteBuffer = kFile.read()
        #end

    # Array Like Thing
    elif isinstance(kInput, array.array) or isinstance(kInput, bytes) or isinstance(kInput, bytearray) :
        kByteBuffer = bytes(kInput)

    # Input Stream
    elif hasattr(kInput, "read") :
        kByteBuffer = kInput.read()

    # Otherwise... no idea what this is.
    else :
        raise TypeError("Reader(FILENAME|FILEBUFFER|BYTES/BYTEARRAY)")
    #end

    assert(None != kByteBuffer)

    return kByteBuffer

#end

def __validateSizeWithRangeCheck(kByteArray : bytes, nOffset : int, nSize : int) -> int :
    if None == nSize :
        nSize = len(kByteArray) - nOffset
    elif (nOffset + nSize) > len(kByteArray) :
        nSize = len(kByteArray) - nOffset
    #end
    return nSize
#end

def __validateSize(kByteArray : bytes, nOffset : int, nSize : int) -> int :
    if None == nSize :
        nSize = len(kByteArray) - nOffset
    #end
    return nSize
#end

def getByteArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 1) -> bytes:
    assert(nSize >= 1)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize}s", kByteArray, nOffset)[0]
#end

def getSignedChar(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 1) -> int :
    assert(1 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}b", kByteArray, nOffset)[0]
#end

def getUnsignedChar(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 1) -> int :
    assert(1 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}B", kByteArray, nOffset)[0]
#end

def getSignedShort(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 2) -> int :
    assert(2 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}h", kByteArray, nOffset)[0]
#end

def getUnsignedShort(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 2) -> int :
    assert(2 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}H", kByteArray, nOffset)[0]
#end

def getSignedLong(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 4) -> int :
    assert(4 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}l", kByteArray, nOffset)[0]
#end

def getUnsignedLong(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 4) -> int :
    assert(4 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}L", kByteArray, nOffset)[0]
#end

def getSignedLongLong(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 8) -> int :
    assert(8 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}q", kByteArray, nOffset)[0]
#end

def getUnsignedLongLong(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 8) -> int :
    assert(8 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}Q", kByteArray, nOffset)[0]
#end

def getFloat(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 4) -> float :
    assert(4 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}f", kByteArray, nOffset)[0]
#end

def getDouble(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = 8) -> float :
    assert(8 == nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}d", kByteArray, nOffset)[0]
#end

def getSignedCharArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize}b", kByteArray, nOffset)
#end

def getUnsignedCharArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize}B", kByteArray, nOffset)
#end

def getSignedShortArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 2) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//2}h", kByteArray, nOffset)
#end

def getSignedShortArrayWithRangeCheck(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple:

    nSize = __validateSizeWithRangeCheck(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    if nSize <= 0 :
        return tuple()
    #end

    assert((nSize % 2) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//2}h", kByteArray, nOffset)
#end

def getUnsignedShortArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 2) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//2}H", kByteArray, nOffset)
#end

def getSignedLongArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 4) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//4}l", kByteArray, nOffset)
#end

def getUnsignedLongArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 4) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//4}L", kByteArray, nOffset)
#end

def getSignedLongLongArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 8) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//8}q", kByteArray, nOffset)
#end

def getUnsignedLongLongArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 8) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//8}Q", kByteArray, nOffset)
#end

def getFloatArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 4) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//4}f", kByteArray, nOffset)
#end

def getDoubleArray(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> tuple :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    assert((nSize % 8) == 0)
    assert(kOrder in ["<", ">"])
    return struct.unpack_from(f"{kOrder}{nSize//8}d", kByteArray, nOffset)

#end

def getString(kByteArray : bytes, kOrder : str, nOffset : int = 0, nSize : int = None) -> str :
    nSize = __validateSize(kByteArray=kByteArray, nOffset=nOffset, nSize=nSize)
    kSanitizedArray = []
    for k in getByteArray(kByteArray=kByteArray, kOrder=kOrder, nOffset=nOffset, nSize=nSize) :
        if k < 0x20 or k >= 0x80 :
            break
        #end
        kSanitizedArray.append(chr(k))
    #end
    return "".join(kSanitizedArray)
#end

def decodeRealFromByteBuffer(kByteBuffer : bytes) :
    return float(decodeStringFromByteBuffer(kByteBuffer=kByteBuffer))
#end

def decodeIntFromIntByteBuffer(kByteBuffer : bytes) :
    return int(decodeStringFromByteBuffer(kByteBuffer=kByteBuffer), 10)
#end

def decodeIntFromHexByteBuffer(kByteBuffer : bytes) :
    return int(decodeStringFromByteBuffer(kByteBuffer=kByteBuffer), 16)
#end

def decodeStringFromByteBuffer(kByteBuffer : bytes) :
    return kByteBuffer.decode()
#end