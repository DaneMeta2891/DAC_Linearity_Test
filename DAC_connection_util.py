import serial
import serial.tools.list_ports
import time

class dacConnectionUtil:
    BAUDRATE = 115200
    TIMEOUT = 1

    def __init__(self):
        status = False
        for port,*_ in serial.tools.list_ports.comports():
            ser = None
            try: 
                print('check:', port)
                ser = serial.Serial(port=port, baudrate=self.BAUDRATE, timeout=self.TIMEOUT)

                ser.flush()
                ser.write(b':set mode=5\r\n')
                time.sleep(1)
                resp = ser.readlines()[-1].strip().decode()

                if resp == ':set mode=5,ack':
                    status = True
                    break

            except:
                print('close ', port)
                if ser:
                    ser.close()
                continue
    
        if (status):
            self.s = ser
        else:
            self.s = None
            print("Unable to detect geortek board")

    def __del__(self):
        self.disconnect()
    
    def check_connected(self):
        '''
        returns true if dac was detected, false if not
        '''
        return False if self.s == None else True
    
    def send_command(self, command:str, debug_flag:bool=False, loop_until_success:bool=False):
        '''
        sends command or set of commands to dac

        command (str): command to send to dac
        debug_flag (bool): if true prints command return to console
        loop_until_success (bool): if true will attempt to send command up to 5 times if ack is not detected in return
        '''
        for attempt_num in range(5):
            self.s.flush()
            self.s.write((command + "\r\n").encode())

            command_returns = self.s.readlines()

            if (debug_flag):
                print(command)
                print(command_returns)

            #check for errors the return or continue to retry until attempt limit is reached
            errors = [odd_element for odd_element in command_returns[1::2] if (odd_element.decode()[-5:-2] != "ack")]
            if not(loop_until_success):
                return False if len(errors) > 0 else True
            elif (loop_until_success and len(errors) == 0):
                return True
            else:
                print("ack not detected, retry..." + str(attempt_num + 1))
            
            #short delay before second attempt
            time.sleep(1)
    
    def extract_return_val(self, command:str):
        '''
        get return value from command_string

        command_string (str): command to send to dac
        '''
        self.s.flush()
        self.s.write((command + "\r\n").encode())
        try:
            return self.s.readlines()[0].decode().strip()
        except:
            print("Output format not recognized")
            return "0"
    
    def check_LCOS_temp(self, temp_threshold:float=60.0):
        '''
        checks LCOS temp

        temp_threshold (float):

        returns: True if the temp is above temp_threshold, False if below
        '''
        for _ in range(5):
            try:
                temp = float(self.extract_return_val(":get temp-lc"))
                if (temp < 0):
                    print("ValueError: invalid return value from \'get temp-lc\'")
                else:
                    break
            except ValueError:
                print("ValueError: unexpected return value from \'get temp-lc\'")
        if (temp > temp_threshold):
            return True
        else:
            return False

    def cool_LCOS(self, disable_time:int = 30):
        '''
        disables LCOS and waits for disable_time to allow it to cool

        disable_time (int): number of seconds to disable LCOS for
        '''
        print("Disabling LCOS for " + str(disable_time) + " seconds")
        #disable current
        self.send_command(":set ri=0:set bi=0:set gi=0")

        #disable LCOS then wait until it cools down
        self.send_command(":set en-lcos=0")
        time.sleep(disable_time)

        #enable LCOS then wait until it's ready to receive commands again
        self.send_command(":set en-lcos=1")
        time.sleep(5)
        self.send_command(":set mode=5", False, True)
    
    def disconnect(self):
        if (self.s != None):
            #disable leds and close connection
            self.send_command(":set mode=5")
            self.s.close()