import serial
import serial.tools.list_ports
import time
import openpyxl
from argparse import ArgumentParser

#enable/disable projection:
#set a-l=0 (off) (or rgb for individual colors)
#get ri: gets current (mA) (rgb for different colors)
#get ri-ad: gets DAC value
#set ri=20: sets ri value
#if temp value hits 60*c wait 1 min to allow the device to cool down
#get temp-(rgb) db(DDB) or lc(LCOS), get use LCOS value for temp control
#todo:
#use set en-lcos=0 (1 for enable) to disable LCOS for cooling down
#ask what lc-init does, why both lc-init and en-lcos exist
#lc-lowc=1 (1 for low current mode, 0 for normal current mode)
#after enabling LC mode (set lc-lowc=1) all LEDs will be set to the LC mode current corresponding to the DAC value
#that the LED was set to in HC mode, and vice versa

class DAC_Connection_Util:
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
            print("Unable to detect geortek board")

        #Test loop
        enable_test_loop = True
        while (enable_test_loop and status):
            userCmd = input("Enter Command: ")
            if (userCmd != ""):
                if (userCmd[0] == 'r'):
                    print(self.extract_return_float(userCmd[1:]))
                else:
                    self.send_command(userCmd, False, True)
            else:
                self.s.close()
                break
    
    def send_command(self, command_string, loop_until_success = False, debug_flag=False):
        for attempt_num in range(5):
            self.s.flush()
            self.s.write((":" + command_string + "\r\n").encode())

            command_returns = self.s.readlines()

            if (debug_flag):
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
    
    def extract_return_float(self, command_string):
        self.s.flush()
        self.s.write((":" + command_string + "\r\n").encode())
        try:
            return self.s.readlines()[0].decode().strip()
        except:
            print("Output format not recognized")
            return -1.0
    
    def check_LCOS_temp(self, temp_threshold=60):
        if (float(self.extract_return_float("get temp-lc")) > temp_threshold):
            return True
        else:
            return False

    def cool_LCOS(self, disable_time=20):
        print("Disabling LCOS and cool for " + str(disable_time) + "seconds")

        #set current to LEDs to zero
        self.send_command("set ri=0:set gi=0:set bi=0")

        #disable LCOS then wait until it cools down
        self.send_command("set en_lcos=0")
        time.sleep(disable_time)

        #enable LCOS then wait until it's ready to receive commands again
        self.send_command("set en_lcos=1")
        time.sleep(5)
        self.send_command("set mode=5", True)
    
    #generates .xlsx of current (mA) values for any given DAC value
    def generate_DAC_char_xlsx(self, output_file_name):
        wb = openpyxl.Workbook()
        ws = wb.active
        
        #table header
        ws.append(["","","LC_Mode","","","HC_Mode"])
        ws.append(["DAC_Value","Red","Green","Blue","Red","Green","Blue"])

        #iterate through all possible permutations to fill out spreadsheet
        #set all LED current values to zero
        for mode in ("LC_Mode", "HC_Mode"):
            #set mode to LC or HC
            #max current for LC is 31.37
            for color in ("red", "green", "blue"):
                #define variable to store current(mA) within loop
                for DAC_value in range(1024):
                    #cool LCOS if temp is above threshold
                    if (self.check_LCOS_temp()):
                        self.cool_LCOS()
                    #

        wb.save(output_file_name + ".xlsx")

DAC_Connection_Util()