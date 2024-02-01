from scope_com import scopeConnectionUtil

#todo: automatically configure IP address (if possible)
#todo: create function to config voltage offset/scale based on expected value
class scopeControl:
    INVALID_RETURN = "9.9E+37"
    def __init__(self, scope_ip):
        #establish and verify scope connection
        self.scope_com = scopeConnectionUtil()
        if not(self.scope_com.connect(scope_ip)):
            print("Unable to connect to scope with provided IP")
    
    #function to config voltage scale/offset based on expected voltage value
    def vertical_config(self, channel:int, expected_voltage:float):
        #todo: develop
        return
    
    #set channel voltage scale
    def set_voltage_scale(self, channel:int, voltage:float):
        self.scope_com.send(":CHANnel" + str(channel) + ":SCALe " + format(voltage, '0.2f'))
    
    #set channel offset scale
    def set_voltage_offset(self, channel:int, voltage:float):
        self.scope_com.send(":CHANnel" + str(channel) + ":OFFSet " + format(voltage, '0.4f'))
    
    #scope setup configuration
    def scope_setup_config(self):
        self.scope_com.send("*RST")
        self.set_channel_display([True, False, False, False])

        #clear existing measurements
        self.scope_com.send(":MEASure1:CLEar")

        #add desired measurements
        self.scope_com.send(":MEASure:VMAX CHANnel1")
        self.scope_com.send(":MEASure:VTOP CHANnel1")

        #enable statistics display
        self.meas_stats_display(True)

    #enable or disable measurement stats display
    def meas_stats_display(self, display:bool):
        self.scope_com.send(":MEASure:STATistics:DISPlay " + str(int(display)))
    
    #reset measurement stat sample count
    def reset_meas_stats(self):
        self.scope_com.send(":MEASure:STATistics:RESet")

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

    #input 4 bool list to enable/disable channelss
    def set_channel_display(self, ch_array:list):
        for i in range(len(ch_array)):
            if (ch_array[i]):
                self.scope_com.send(":CHANnel" + str(i + 1) + ":DISPlay " + str(int(ch_array[i])))
    
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
    

control_obj = scopeControl("169.254.185.64")
control_obj.test_interface()