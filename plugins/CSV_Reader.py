import array
import typing
import csv
import io

import plugins.common_basetypes
from plugins.common_basetypes import ErrorLevelHandling

class Reader(plugins.common_basetypes.Reader) :

    TIME_COL        = None
    DATA_COL        = 0
    MIN_SIZE        = 1
    MAX_SIZE        = 1
    DELIMITER       = ","

    __kTimes        = None
    __kWaveform     = None

    __kByteBuffer   = None

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :

        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        kOptions    = self.getOptions(kPluginOptions=kPluginOptions)
        kCSV        = list(csv.reader(io.StringIO(self.__kByteBuffer.decode()), delimiter=kOptions["Delimiter"]))

        nTimeCol    = kOptions["TimeCol"]
        nDataCol    = kOptions["DataCol"]

        self.__kWaveform = [float(kEntry[nDataCol]) for kEntry in kCSV]

        if None != nTimeCol :
            self.__kTimes = [float(kEntry[nTimeCol]) for kEntry in kCSV]
        else :
            self.__kTimes = list(range(0, len(self.__kWaveform)))
        #end

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
            "TimeCol"   : self.TIME_COL,
            "DataCol"   : self.DATA_COL,
            "MinSize"   : self.MIN_SIZE,
            "MaxSize"   : self.MAX_SIZE,
            "Delimiter" : self.DELIMITER
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

        # This does a spot check of the first row only.
        try :

            kOptions    = self.getOptions(kPluginOptions=kPluginOptions)
            kCSV        = csv.reader(io.StringIO(kFileBuffer.decode()), delimiter=kOptions["Delimiter"])
            kValidRange = range(kOptions["MinSize"], kOptions["MaxSize"] + 1)
            nTimeCol    = kOptions["TimeCol"]
            nDataCol    = kOptions["DataCol"]

            kFirstRow   = kCSV.__next__()
            if None != nTimeCol :
                float(kFirstRow[nTimeCol])
            #end
            float(kFirstRow[nDataCol])

            bValid      = len(kFirstRow) in kValidRange

            return bValid

        except Exception as e :
            return False
        #end

    #end

    def getWaveform(self) -> list :
        return self.__kWaveform
    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        return self.__kTimes, self.__kWaveform
    #end

#end
