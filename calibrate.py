#!/usr/bin/env python3

import ivi
import cal

###############################################################################
# Change these as appropriate for your instruments
###############################################################################

psu = ivi.rigol.rigolDP832("TCPIP0::10.1.0.11::INSTR")
dmm = ivi.keithley.keithley2000("ASRL::/dev/ttyS2,9600,8n1::INSTR")

###############################################################################
# Settings
###############################################################################

# Current limit of your DMM's current range
#
# If this is less than 3.2A then you will need an alternative DMM for manual
# entry for currents over this limit.

manual_entry_over_current = 3

# Range of channels to calibrate
#
# Set to range(<min channel>, <max channel + 1>)

#calibrate_channels = range(1, 4)    # All Channels
#calibrate_channels = range(1, 2)    # Channel 1 only
#calibrate_channels = range(2, 3)    # Channel 2 only
calibrate_channels = range(3, 4)    # Channel 3 only

###############################################################################
# Callback function used to setup the DMM for either voltage or current
# function is either dc_volts or dc_current
###############################################################################

def setup_dmm(dmm, function):
    dmm.measurement_function = function
    dmm.auto_range = 'on'
    
    # These may be specific to the Keithley 2000 driver and will need changing
    # if using a different DMM
    dmm.nplc = 1
    dmm.filter.count = 10
    dmm.filter.type = 'repeat'
    dmm.filter.enabled = 'on'

###############################################################################
# WARNING: CALIBRATION VALUES WILL BE CHANGED IF THIS IS SET TO True
###############################################################################

# Update the calibration values for the DMM when True, or just run through
# calibration without updating the values if False.
#
# Warning: When False, the calibration values of the DP832 will still be cleared
# so you will have to restart the PSU to get them back. The calibration for any
# channels affected will be (probably wildly) off until you either restart or
# set this to True.

update_calibration = False

###############################################################################
# You should not need to change anything below here. Probably.
###############################################################################

psu.utility.reset()
dmm.utility.reset()

try:
    calibrator = cal.DP832Cal(psu, dmm)
    calibrator.dmm_setup_callback = setup_dmm
    calibrator.manual_current_limit = manual_entry_over_current
    calibrator.calibrate(calibrate_channels, update_calibration)
except (Exception, KeyboardInterrupt) as e:
    print()
    
    # Resetting will also turn off all outputs
    psu.utility.reset()
    
    print("ERROR: %s" % str(e))
    print("Calibration failed. Your DP832 may need to be restarted to regain calibration values.")
