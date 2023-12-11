from scope_communication import scopeConnectionUtil

class scope_control:
    INVALID_RETURN = "9.9E+37"
    def __init__(self, scope_ip):
        #establish and verify scope connection
        self.scope_com = scopeConnectionUtil()
        if not(self.scope_com.connect(scope_ip)):
            print("Unable to connect to scope with provided IP")
    
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
        #add max and top channel command
        self.scope_com.send(":MEASure:VMAX CHANnel1")
        self.scope_com.send(":MEASure:VTOP CHANnel1")
    
    #get and parse measurement data
    def get_measurement_data(self):
        meas_data = self.scope_com.send_recv(":MEASure:RESults?")

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
                    outFile.write(user_cmd[1:])
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

scope_control("169.254.185.232").test_interface()