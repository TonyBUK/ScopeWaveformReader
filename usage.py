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

# Or... you can ignore the scope reader entirely and go straight to the waveform reader of choice.
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
