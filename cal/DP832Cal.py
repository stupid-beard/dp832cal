
# This was based on bson's python scripts

import datetime, time, math

class DP832Cal:
    known_list = [ "DP832", "DP832A" ]
    
    # Calibration points for channels 1 & 2
    cal_dacv12 = [0.2, 0.5, 1.2, 2, 3.2, 4.1, 5.2, 6.9, 7.5, 8.7, 10.1, 11.8, 12.6, 13.5,
                  15, 15.8, 16.5, 17.3, 18.5, 19.1, 19.9, 20.2, 20.8, 21.8, 22.4, 22.7,
                  23.9, 24.3, 25.7, 26.9, 27.9, 28.5, 28.9, 29.8, 30.2, 32];
    cal_adcv12 = [0, 0.05, 0.1, 0.5, 1, 5, 10, 12.8, 20, 30, 32];
    cal_daci12 = [0.1, 0.25, 0.5, 0.8, 1, 1.25, 1.5, 1.75, 1.9, 2.15, 2.35, 2.5, 2.75,
                  3, 3.2];
    cal_adci12 = [0, 0.01, 0.1, 1, 2, 3, 3.2];
    
    # Calibration points for channel 3
    cal_dacv3 = [0.1, 0.2, 0.4, 0.85, 1.2, 1.8, 2.55, 3.1, 3.4, 4.1, 4.5, 5, 5.3];
    cal_adcv3 = [0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1, 3, 5, 5.3];
    cal_daci3 = [0.1, 0.5, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.2];
    cal_adci3 = [0, 0.1, 1, 2, 3, 3.2];

    # Calibration points, indexable by channel N (1:3)
    cal_dacv = [ [], cal_dacv12, cal_dacv12, cal_dacv3 ]
    cal_adcv = [ [], cal_adcv12, cal_adcv12, cal_adcv3 ]
    cal_daci = [ [], cal_daci12, cal_daci12, cal_daci3 ]
    cal_adci = [ [], cal_adci12, cal_adci12, cal_adci3 ]

    stabilization_time_sec = 2
    
    def __init__(self, psu, dmm):
        super(DP832Cal, self).__init__()
        
        if psu.identity.instrument_model not in self.known_list:
            raise ValueError("Model %s not recognised as a DP832 power supply" % (psu.identity.instrument_model))
        
        self._dmm_setup_callback = None
        self._manual_current_limit = 10
        
        self._psu = psu
        self._dmm = dmm
    
    @property
    def manual_current_limit(self):
        return self._manual_current_limit
    
    @manual_current_limit.setter
    def manual_current_limit(self, value):
        self._manual_current_limit = float(value)
    
    @property
    def dmm_setup_callback(self):
        return self._dmm_setup_callback
    
    @dmm_setup_callback.setter
    def dmm_setup_callback(self, value):
        self._dmm_setup_callback = value
        
    def _setup_dmm(self, function):
        if self._dmm_setup_callback:
            self._dmm_setup_callback(self._dmm, function)
        else:
            self._dmm.measurement_function = function
            self._dmm.auto_range = 'on'

    def _print_instrument(self, inst):
        print("   %s %s (%s) %s" % (inst.identity.instrument_manufacturer,
                                    inst.identity.instrument_model,
                                    inst.identity.instrument_serial_number,
                                    inst.identity.instrument_firmware_revision))
        
    def _print_val(self, what, unit, step, point, value):
        if point != 0:
            value_pct_err=math.fabs((point-value)/point)*100.0
        else:
            value_pct_err=0.0
        print("%5s %2d :  Point:%+6.4g%s - DMM:%+12.8g%s - Err:%4g%%" % (what, step, point, unit, value, unit, value_pct_err))
    
    def _wait_for_enter(self, msg):
        print()
        print(msg)
        input("Press enter to continue: ")
    
    def _calib_single(self, what, value_table, channel, unit, index):
        print()
        print("Running %s for channel %d" % (what, channel))
        values = value_table[channel]
        step   = 0
        ident = unit
        if unit == 'A':
            ident = 'C'
        
        manual = False

        for value in values:
            if unit == 'A' and value > self._manual_current_limit and manual == False:
                manual = True
                print()
                print("WARNING: CURRENT BEYOND DMM LIMIT, MANUAL INPUT REQUIRED")
                self._wait_for_enter("Connect alternative DMM 10A CURRENT inputs to PSU channel %d" % (channel))
                
            self._psu._write("CALibration:Set CH%d,%s,%d,%g%s,%d" % (channel, ident, step, value, unit, index));
            
            time.sleep(self.stabilization_time_sec)
            if not manual:
                value_read = self._dmm.measurement.read(1)
            else:
                value_read = float(input("Enter DMM reading: ").strip())
            
            self._psu._write("CALibration:MEAS CH%d,%s,%d,%g%s,%d" % (channel, ident, step, value_read, unit, index));
            
            self._print_val(what, unit, step, value, value_read);
            step += 1
    
    def calibrate(self, channels=range(1, 4), update=False):
        print("Calibrating:")
        self._print_instrument(self._psu)
        print("With:")
        self._print_instrument(self._dmm)
        
        if self._manual_current_limit < 3.2:
            print()
            print("WARNING: Currents greater than %.01f A will require alternative DMM and manual entry" % (self._manual_current_limit))
        
        print()
        print("Press Ctrl-C at any time to abort")
        print()
        
        # Ensure all channels have a matching calibration date
        now = datetime.date.today().isoformat()
        
        for channel in channels:
            print("CALIBRATING CHANNEL %d ..." % (channel))
            
            # Voltage
            self._wait_for_enter("Connect the DMM VOLTAGE inputs to the PSU channel %d" % (channel))
            self._setup_dmm('dc_volts')
            
            self._psu._write("CALibration:Start 11111,CH%d" % channel)
            self._psu._write("CALibration:Clear CH%d,ALL" % channel)
            self._psu.utility.reset()
            
            self._psu.outputs[channel - 1].enabled = 1
            
            self._calib_single("DAC-V", self.cal_dacv, channel, "V", 1)
            self._calib_single("ADC-V", self.cal_adcv, channel, "V", 0)
            
            self._psu.outputs[channel - 1].enabled = 0
            
            # Current
            self._wait_for_enter("Connect the DMM 10A CURRENT inputs to the PSU channel %d" % (channel))
            self._setup_dmm('dc_current')
            
            self._psu.outputs[channel - 1].enabled = 1
            
            self._calib_single("DAC-I", self.cal_daci, channel, "A", 1)
            
            if self._manual_current_limit < 3.2:
                # If alternative DMM was required, wait for original to be re-connected
                self._psu.outputs[channel - 1].current_limit = 0.1
                self._wait_for_enter("Reconnect original DMM CURRENT inputs to PSU channel %d" % (channel))
            
            self._calib_single("ADC-I", self.cal_adci, channel, "A", 0)
            
            self._psu.outputs[channel - 1].enabled = 0
            
            # Update
            if update:
                print()
                print("Updating calibration data for channel %d" % channel)
                self._psu._write("CALibration:End %s,CH%d" % (now, channel))
                print()
                
            # Done
            print()
            print("Channel %d finished" % channel)
