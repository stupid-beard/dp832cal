#!/usr/bin/env python3

import ivi
import cal

psu = ivi.rigol.rigolDP832("TCPIP0::10.1.0.11::INSTR")
psu.utility.reset()

dmm = ivi.keithley.keithley2000("ASRL::/dev/ttyS2,9600,8n1::INSTR")
dmm.utility.reset()
dmm.measurement.continuous = 'on'


try:
    calibrator = cal.DP832Cal(psu, dmm)
    calibrator.max_current = 3
    calibrator.calibrate(range(1, 2), True)
except (Exception, KeyboardInterrupt) as e:
    print()
    
    # Error - turn off PSU outputs
    #print("Shutting off PSU outputs")
    #for chan in range(0, 3):
        #psu.outputs[chan].enabled = 0
    
    psu.utility.reset()
    dmm.utility.reset()
    
    print("ERROR: %s" % str(e))
    print("Calibration failed. Terminating.")
