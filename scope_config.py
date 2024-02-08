from scope_com import scopeConnectionUtil
import time

#scope configuration object
class scopeControl:
    INVALID_RETURN = "9.9E+37"
    def __init__(self):
        self.scope_com = scopeConnectionUtil()
        self.scope_com.connect()
    
    def __del__(self):
        self.scope_com.disconnect()

    def horizontal_config(self, timescale:float):
        '''
        configures timescale

        timescale (float): time in seconds
        '''
        self.scope_com.send(":TIMebase:SCAle " + format(timescale, '0.9f'))

    def trigger_config(self, channel:int, level:float):
        '''
        configures trigger source and level

        channel (int): the trigger source channel
        voltage (float): the trigger level in volts
        '''
        self.scope_com.send(":TRIGger:SOURce " + "CHAN" + str(channel))
        self.scope_com.send(":TRIGger:LEVel " + format(level, '0.4f'))
    
    def set_voltage_scale(self, channel:int, voltage:float):
        '''
        sets voltage scale
        
        channel (int): the trigger source channel
        voltage (float): the trigger level in volts
        '''
        self.scope_com.send(":CHANnel" + str(channel) + ":SCALe " + format(voltage, '0.4f'))
    
    def set_voltage_offset(self, channel:int, voltage:float):
        '''
        sets voltage offset

        channel (int): the trigger source channel
        voltage (float): the trigger level in volts
        '''
        self.scope_com.send(":CHANnel" + str(channel) + ":OFFSet " + format(voltage, '0.4f'))
    
    def vertical_config(self, channel:int, voltage:float):
        '''
        configures vertical scale/offset

        channel (int): the trigger source channel
        voltage (float): the trigger level in volts
        '''
        self.set_voltage_scale(1, voltage/3)
        self.set_voltage_offset(1, voltage/3)
        self.trigger_config(1, voltage/2.0)
    
    def scope_setup_config(self, channel:int = 1):
        '''
        resets scope to default then configures it for data collection
        '''
        #reset scope to defaults
        self.scope_com.send("*RST")

        #config channels
        self.set_channel_display(channel)

        #clear existing measurements
        self.scope_com.send(":MEASure1:CLEar")

        #add measurements
        self.scope_com.send(":MEASure:VMAX CHANnel1")
        self.scope_com.send(":MEASure:VTOP CHANnel1")

        #enable stat display
        self.meas_stats_display(True)

        #config high res mode
        self.set_high_res_mode()

        #default scale and trigger settings, will be set dependent on expected voltage value per DAC setting
        self.vertical_config(1, 0.1)

        #set timescale to 5ms
        self.horizontal_config(0.005)

    def meas_stats_display(self, display:bool):
        '''
        enable or disable stats display

        display (bool): True to enable, False to disable
        '''
        self.scope_com.send(":MEASure:STATistics:DISPlay " + str(int(display)))
    
    def reset_meas_stats(self):
        '''
        reset measurement stat sample count
        '''
        self.scope_com.send(":MEASure:STATistics:RESet")
    
    def set_high_res_mode(self):
        '''
        sets high resolution mode
        '''
        self.scope_com.send(":ACQuire:TYPE HRESolution")

    def get_all_meas_data(self):
        '''
        parses out all meas stats and returns dictionary
        '''
        meas_data = self.scope_com.send_recv(":MEASure:RESults?")
        return_dict = dict()
        current_key = ""
        for data in meas_data.split(","):
            try:
                converted_data = float(data)
                if (current_key != ""):
                    return_dict[current_key].append(converted_data)
            except ValueError:
                return_dict[data] = list()
                current_key = data
        return return_dict

    def get_target_meas_data(self, target_meas:str, channel:int, stat_index:int):
        '''
        parses out desired statistic from target measurement

        target_meas (string): meas ID string
        stat_index (int): index of meas stat to return
            meas index list (current, min, max, mean, std_dev, num_samples)
        example:
        get_meas_data("Maximum(1)", 3) returns mean of max on channel 1
        '''

        meas_data = self.scope_com.send_recv(":MEASure:RESults?")
        target_meas_header = target_meas + "(" + str(channel) + ")"
        value_counter = 0
        target_stat_list = False
        for data in meas_data.split(","):
            try:
                converted_data = float(data)
                if (value_counter == stat_index and target_stat_list):
                    return converted_data
                value_counter += 1
            except ValueError:
                value_counter = 0
                target_stat_list = True if (data == target_meas_header) else False
        print("Target measurement not found")
        return -1

    def set_channel_display(self, ch_to_enable:int):
        '''
        enables the channel provided, disabled all others

        ch_to_enable (int): channel to enable
        '''
        for i in range(4):
            enable = True if (i == ch_to_enable - 1) else False
            self.scope_com.send(":CHANnel" + str(i + 1) + ":DISPlay " + str(int(enable)))
scopeControl().scope_setup_config(1)