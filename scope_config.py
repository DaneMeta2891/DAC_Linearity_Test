from scope_com import scopeConnectionUtil
import time

#todo: create function to config voltage offset/scale based on expected value
class scopeControl:
    INVALID_RETURN = "9.9E+37"
    def __init__(self):
        self.scope_com = scopeConnectionUtil()
        self.scope_com.connect()

    def trigger_config(self, channel:int, voltage:float):
        self.scope_com.send(":TRIGger:SOURce " + "CHAN" + str(channel))
        self.scope_com.send(":TRIGger:LEVel " + format(voltage, '0.4f'))
        self.scope_com.send()

    #set to 2 ms (fixed)
    def horizontal_config(self):
        return
    
    #set channel voltage scale
    def set_voltage_scale(self, channel:int, voltage:float):
        self.scope_com.send(":CHANnel" + str(channel) + ":SCALe " + format(voltage, '0.4f'))
    
    #set channel offset scale
    def set_voltage_offset(self, channel:int, voltage:float):
        self.scope_com.send(":CHANnel" + str(channel) + ":OFFSet " + format(voltage, '0.4f'))
    
    #scope setup configuration
    def scope_setup_config(self, channel = 1):
        self.scope_com.send("*RST")
        self.set_channel_display(channel)

        #clear existing measurements
        self.scope_com.send(":MEASure1:CLEar")

        #add measurements
        self.scope_com.send(":MEASure:VMAX CHANnel1")
        self.scope_com.send(":MEASure:VTOP CHANnel1")

        #config high res mode
        self.set_high_res_mode()

        #50 mv scale with 50 mv offset
        self.set_voltage_scale(channel, .05)
        self.set_voltage_offset(channel, .05)

        #configure trigger
        self.trigger_config(1, 0.01)


        #enable statistics display
        self.meas_stats_display(True)

    #enable or disable measurement stats display
    def meas_stats_display(self, display:bool):
        self.scope_com.send(":MEASure:STATistics:DISPlay " + str(int(display)))
    
    #reset measurement stat sample count
    def reset_meas_stats(self):
        self.scope_com.send(":MEASure:STATistics:RESet")
    
    #sets high resolution mode
    def set_high_res_mode(self):
        self.scope_com.send(":ACQuire:TYPE HRESolution")

    #parses out all meas stats and returns dictionary
    def get_all_meas_data(self):
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

    #parses out desired statistic (specified by stat_index) from target measurement (specified by target_meas)
    #and returns the value as a float
    #Maximum(1),+400E-03,+100E-03,+600E-03,+346.129521702867E-03,+49.9185458117796E-03,70521,Top(1),9.9E+37,+400E-03,+400E-03,+400.000000000000E-03,+0.0E+00,19
    #example: get_meas_data("Maximum(1)", 3) returns float("+346.129521702867E-03")
    def get_target_meas_data(self, target_meas, stat_index):
        meas_data = self.scope_com.send_recv(":MEASure:RESults?")
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
                target_stat_list = True if (data == target_meas) else False
        print("Target measurement not found")
        return -1

    #ch_to_enable: enter the channel to enable, disables all other channels
    def set_channel_display(self, ch_to_enable):
        for i in range(4):
            enable = True if (i == ch_to_enable - 1) else False
            self.scope_com.send(":CHANnel" + str(i + 1) + ":DISPlay " + str(int(enable)))
    
    def test_interface(self):
        outFile = open("Scope_Comm.log", "a")
        while (True):
            user_cmd = input("Enter Command: ")
            if (user_cmd != ""):
                if (user_cmd[0] == 'r'):
                    outFile.write(user_cmd[1:] + "\n")
                    scope_return = self.scope_com.send_recv(user_cmd[1:])
                    outFile.write(scope_return)
                    print(scope_return)
                else:
                    outFile.write(user_cmd)
                    self.scope_com.send(user_cmd)
            else:
                self.scope_com.disconnect()
                break
        outFile.close()
    

control_obj = scopeControl()
control_obj.scope_setup_config()
#control_obj.test_interface()