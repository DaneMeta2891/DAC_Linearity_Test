import serial
from argparse import ArgumentParser

class DAC_Connection_Util:
    def __init__(self, COM_port = ""):
        self.s = serial.Serial(port=input("Enter COMPort: ") if COM_port == "" else COM_port, baudrate=115200, timeout=1)
        while (True):
            userCmd = input("Enter Command: ")
            if (userCmd != ""):
                self.send_command(userCmd)
            else:
                break
        self.s.close()
        #self.s.write(b':set mode=5\r\n')
        #check if response is equal to this [b'\n', b':set mode=5,ack\r\n']
        #print(self.s.readlines())
    
    def send_command(self, command_string):
        #readlines may return a list, if not remove [0]
        #will probably have to use index 1 or 2 to read useful information (may depend on command)
        #when reading values clear buffer first with readlines()
        self.s.write((":" + command_string + "\r\n").encode())
        print(self.s.readlines())

DAC_Connection_Util()