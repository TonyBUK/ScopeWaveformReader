###############################################################################
# Method 1 - Using the Scope Reader Plugin System
#
# This example uses the scopereader class.  This will effectively take the
# file, and have each of the plugins try to identify whether they can handle
# the file type.  This is probably the way I expect most people to use this,
# as when working correctly, you can basically throw whatever file you want at
# it, and with a bit of luck, it'll spit out a decoded Waveform for you.
###############################################################################

import scopereader

# The Waveform Class can take either the file name, or the file contents as a byte buffer/list/any other iteratable type.
with scopereader.Reader("sample.wfm") as waveform_reader :

    # First Method: You cam just iterate over the reader, and it'll iterate over the Waveform Contents
    for sample in waveform_reader :
        print(sample)
    #end

    # Second Method: You can get the waveform as a list
    waveform = waveform_reader.getWaveform()
    for sample in waveform :
        print(sample)
    #end

    # Third Method: You can get the waveform as two lists, one for the time, and one for the voltage
    time, voltage = waveform_reader.getWaveformWithTimeStamp()
    for t, v in zip(time, voltage) :
        print(t, v)
    #end

#end

###############################################################################
# Method 2 - Bypassing the Scope Reader Plugin System
#
# Each plugin module has the exact same interface as the Scope Reader itself,
# so if the Scope Reader class is misbehaving, or you already know exactly
# which reader you need, you can just access it directly.
###############################################################################

import plugins.TekTronixWFM_Reader

with plugins.TekTronixWFM_Reader.Reader("sample.wfm") as waveform_reader :

    # First Method: You cam just iterate over the reader, and it'll iterate over the Waveform Contents
    for sample in waveform_reader :
        print(sample)
    #end

    # Second Method: You can get the waveform as a list
    waveform = waveform_reader.getWaveform()
    for sample in waveform :
        print(sample)
    #end

    # Third Method: You can get the waveform as two lists, one for the time, and one for the voltage
    time, voltage = waveform_reader.getWaveformWithTimeStamp()
    for t, v in zip(time, voltage) :
        print(t, v)
    #end

#end

###############################################################################
# Full Usage - Note: This is both for the scope reader, and any of the
#                    plugins.
#
# Parameters:
#
# Required: kInput          : File Name OR File Buffer
#
# Optional: kErrorHandling  : This tells the plugins how to handle encountered
#                             errors, there are 4 levels:
#
#                             ErrorLevelHandling.NONE   - No Warnings or Errors
#                             ErrorLevelHandling.INFO   - Warnings as Warnings
#                                                         Errors as Warnings
#                             ErrorLevelHandling.NORMAL - Warnings as Warnings
#                                                         Errors as Errors
#                             ErrorLevelHandling.ALL    - Warnings as Errors
#                                                         Errors as Errors
#
#                             A warning will just output to stderror the error
#                             message, whereas an error will raise an
#                             exception.
#
# TODO: Note: This last parameter is more experimental for now, so consider it
#             experimental.  It's only required for the CSV plugin for now.
#             What I dislike is that it's contrary to the aim of the scope
#             reader class, which tries to provide a normalised interface,
#             whereas this requires you to know exactly which plugin you're
#             using.
#
# Optional: kPluginOptions  : This dictionary will be specific per plugin an
#                             allows customisation specific to that module.
#                             
###############################################################################