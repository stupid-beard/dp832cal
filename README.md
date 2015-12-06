# Rigol DP832 Calibration Script

This script allows calibration of a DP832 using any multimeter supported by python-ivi. The calibration script was based heavily on a previous script by [bson on the EEVBlog forums](http://www.eevblog.com/forum/testgear/rigol-dp832-firmware-updates-and-bug-list/msg650855/#msg650855), which in turn was based on a [MATLAB script by LaurentR](http://www.eevblog.com/forum/testgear/rigol-dp832-firmware-updates-and-bug-list/msg587350/#msg587350).

The SCPI calibration information came from [TooOldForThis](http://www.eevblog.com/forum/testgear/rigol-dp832-firmware-updates-and-bug-list/msg556101/#msg556101) and [ted572](http://www.eevblog.com/forum/testgear/rigol-dp832-firmware-updates-and-bug-list/msg558318/#msg558318).

## Requirements

* [python-ivi](https://github.com/python-ivi/python-ivi)
* A Rigol DP832 Power Supply
* A 6.5 Digit Multimeter supported by python-ivi

If you have a Keithley 2000 or compatible meter, I have initial support implemented in a (fork of python-ivi)[https://github.com/stupid-beard/python-ivi/tree/feature/keithley2000].

This was written using Python 3 on Linux and has not been tested on other platforms. It will require minor hackery to work on Python 2.

## Using it

See the comments at the top of calibrate.py and change the settings as appropriate, then run the script.

## Quick note on current ranges

You need a meter capable of measuring currents of 3.2A to complete calibration. A hack has been implemented to allow use of a handheld DMM and manual data entry for the currents above the maximum supported by your meter.

This is controlled by the manual_entry_over_current option in calibrate.py.

You will be prompted to switch the leads when appropriate. If you have any doubt press ctrl+c to abort; the current output will be increased as soon as you hit enter on the prompt.
