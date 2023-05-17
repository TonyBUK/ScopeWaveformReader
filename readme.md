# Scope Waveform Reader

## Introduction

This particular project is one that I'd categorise as "necessity is the mother of all invention".  In a nutshell, a few recent work projects required me to read various waveform files to extract all of the measurements, and whilst I was able to find a few convertors here and there, I wanted something with a bit more... totality.  To let me read pretty much any waveform, and extract the contents as useable data, complete with timestamps.

And since I couldn't find one that met my brief, I decided why not try and write one myself...

## Formats Handled So Far...

- Agilent / Infinium .wfm
    -  Versions 6 - 11
- CSV
- TekTronix ISF
- TekTronix WFM
    - Version 1 - 3
- TekTronix LLWFM

## Usage

The file usage.py shows a couple of different example usages.  In a nutshell, you can either use the plugin system as intended, being to let scopyreader.py arbitrate the file you've provided and find the most appropriate plugin, or you can bypass this entirely and use the plugins directly.

## Road Map

So far I'm just putting this out there as a Python project, since that's relatively quick to prototype new formats, and I'm not overly committed to the exact way the plugin system works so far.  Once I get a few more formats decoded / improve overall maturity, I'm looking to then extend this to a number of other languages, probably C and Matlab would be the sensible ones, however alot of it will depend on demand etc.

The primary objective to start with has been robustness / completeness over speed.  Not that it's particuarly slow, however github has plenty of more bespoke parsers that use libraries such as numpy etc. to focus on speed.  So if that's of concern to you, then absolutely look elsewhere.

The focus here is primarily to document my findings on each file format, and provide a relatively simple way of decoding/accessing data.

## How Can You Help?

Waveforms... I need waveforms.  If you've access to a scope / files that the parser doesn't handle, get in touch.  Ideally I'd want the waveform file itself, and some means of knowing what the data *should* look like.  And of course if there's any documentation / existing parsers, that would help immensely too.  There's no guarentees of course, but so far I've managed to handle each file format I've gotten my grubby hands on.