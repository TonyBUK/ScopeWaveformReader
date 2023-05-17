import array
import os
import typing
import importlib.util
import plugins.common_basetypes
import plugins.common_func

from plugins.common_basetypes import ErrorLevelHandling

AUTORUN = False
PLUGINS = []
PLUGIN_PATH = "plugins"

class Reader(plugins.common_basetypes.Reader):

    __kByteBuffer     = None
    __kPlugin         = None

    def __init__(self, kInput : typing.Union[str, typing.BinaryIO, bytes, bytearray, array.ArrayType] = None, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : dict = None) :

        # Grab the Input Data as a Raw Byte Buffer
        self.__kByteBuffer = plugins.common_func._validateAndGetInput(kInput=kInput)

        if 0 == len(PLUGINS) :
            initialise()
        #end

        # TODO: There's going to be some scenarios where a plugin *could* be the right one if all other possibilities are exhausted, for example, raw data, so maybe have
        #       them return a degree of condifence rather than a boolean, for example, what if I had a "raw" plugin, that pretty much by definition couldn't reject any
        #       data.
        #
        #       Alternatively they could return a priority value that can order the plugins.  If a plugin can definitively prove a format is one it can handle, it
        #       is pushed to the top.  If it can't there will be some arbitration based on how confident it is.
        for kPlugin in PLUGINS :
            if kPlugin.Reader.isValid(kFileBuffer=self.__kByteBuffer, kPluginOptions=kPluginOptions) :
                self.__kPlugin = kPlugin.Reader(kInput=self.__kByteBuffer, kErrorHandling=kErrorHandling, kPluginOptions=kPluginOptions)
                break
            #end
        #end

        if None == self.__kPlugin and kErrorHandling in [ErrorLevelHandling.NORMAL, ErrorLevelHandling.ALL] :
            raise TypeError("No Available Plugins for Type")
        #end

    #end

    def __enter__(self) :
        if None != self.__kPlugin :
            return self.__kPlugin
        #end
        return self
    #end

    def __exit__(self, type, value, traceback) :
        return False
    #end

    # In the event a Plugin was not available, these functions just return *something*
    # iterable in the event the callers error handling is insufficient.

    def __iter__(self) :
        if None != self.__kPlugin :
            return self.__kPlugin.getWaveform().__iter__()
        #end
        return []
    #end

    def getWaveform(self) -> list :
        if None != self.__kPlugin :
            return self.__kPlugin.getWaveform()
        #end
        return []

    #end

    def getWaveformWithTimeStamp(self) -> tuple :
        if None != self.__kPlugin :
            return self.__kPlugin.getWaveformWithTimeStamp()
        #end
        return [], []
    #end

    # This is probably the least desireable way of doing this... basically in order to use this, you must have
    # first instatiated the class, which means it's either failed to select a plugin, or it's selected maybe the
    # wrong plugin, or for whatever reason, there's multiple valid plugins, or you need to fiddle with the options...
    #
    # If you want to forcibly use a specific plugin, there's two other and arguably better ways.
    #
    # Use the scopereader scoped version:
    #
    # scopereader.<plugin>.Reader
    #
    # Use the plugin version directly:
    #
    # import plugin.<plugin>
    #
    # plugin.<plugin>.Reader
    #
    # However this is in place for completeness.
    def setPlugin(self, kPlugin : str, kErrorHandling : ErrorLevelHandling = ErrorLevelHandling.NORMAL, kPluginOptions : list = None) :
        self.__kPlugin = globals()[kPlugin].Reader(kInput=self.__kByteBuffer, kErrorHandling=kErrorHandling, kPluginOptions=kPluginOptions)
    #end

    # This is the catch-all to get any nuanced class options.
    def getPlugin(self) :
        return self.__kPlugin
    #end

#end

def initialise() :

    if len(PLUGINS) > 0 : return
    kPluginAbsolutePath = os.path.join(os.path.dirname(__file__), PLUGIN_PATH)

    for kPlugin in os.listdir(kPluginAbsolutePath) :

        kTokens     = os.path.splitext(kPlugin)
        kBaseName   = kTokens[0]

        if "reader" == kBaseName.lower().split("_")[-1] :

            kSpec   = importlib.util.spec_from_file_location(kBaseName, os.path.join(kPluginAbsolutePath, kPlugin))
            assert(None != kSpec)
            kModule = importlib.util.module_from_spec(kSpec)
            assert(None != kModule)
            kSpec.loader.exec_module(kModule)

            # Append the Module for Searching
            PLUGINS.append(kModule)

            # Make the Module available at the module scope level
            # This allows sub-modules to explicitly pick a plugin.
            globals()[kBaseName] = kModule

        #end

    #end

#end

if AUTORUN :
    initialise()
#end