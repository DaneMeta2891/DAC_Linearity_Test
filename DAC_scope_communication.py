from scope_communication import scopeConnectionUtil

class scope_control:
    def __init__(self, scope_ip):
        #establish and verify scope connection
        self.scope_com = scopeConnectionUtil()
        if not(self.scope_com.connect(scope_ip)):
            print("Unable to connect to scope with provided IP")
    
    #configure scope
    def setup_scope_measurements(self):
        self.scope_com.send("*RST")
        return
    
    #get and parse measurement data
    def get_measurement_data(self):
        return
    
    def test_interface(self):
        while (True):
            user_cmd = input("Enter Command: ")
            if (user_cmd != ""):
                if (user_cmd[0] == 'r'):
                    print(self.scope_com.send_recv(user_cmd[1:]))
                else:
                    self.scope_com.send(user_cmd)
            else:
                self.scope_com.disconnect()
                break

scope_control("169.254.61.242").test_interface()