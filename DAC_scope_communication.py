from scope_communication import scopeConnectionUtil

class scope_control:
    SCOPE_IP = ""
    def __init__(self):
        #establish and verify scope connection
        self.scope_com = scopeConnectionUtil()
        self.scope_com.connect(self.SCOPE_IP)
        return
    
    def setup_scope_measurements(self):
        #reset scope then setup scope measurements
        return
    
    def get_measurement_data(self):
        #get and parse current value from measurements
        return
    
    def test_interface(self):
        while (True):
            user_cmd = input("Enter Command: ")
            if (user_cmd != ""):
                if (user_cmd[0] == 'r'):
                    print()
                else:
                    self.send_command()
            else:
                self.s.close()
                break