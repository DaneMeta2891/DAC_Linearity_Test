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
#find out how to set LC mode
#find out what causes the LCOS to heat up, and what can be disabled to expedite cooling
#use set en-lcos=0 (1 for enable) to disable LCOS for cooling down
#ask what lc-init does, why both lc-init and en-lcos exist
#lc-lowc=1 (1 for low current mode, 0 for normal current mode)

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
                    self.extract_return_val(userCmd[1:])
                else:
                    self.send_command(userCmd)
            else:
                self.s.close()
                break
    
    def send_command(self, command_string, loop_until_success = False):
        for attempt_num in range(5):
            self.s.flush()
            self.s.write((":" + command_string + "\r\n").encode())

            #check for errors the return or continue to retry until attempt limit is reached
            error_list = [odd_element for odd_element in self.s.readlines()[1::2] if (odd_element.decode()[-5:-2] != "ack")]
            if not(loop_until_success):
                return False if len(error_list) > 0 else True
            elif (loop_until_success and len(error_list) == 0):
                return True
            else:
                print("Unable to detect command ack, retry attempt " + str(attempt_num + 1))
            
            #short delay before second attempt
            time.sleep(2)
    
    def extract_return_float(self, command_string):
        self.s.flush()
        self.s.write((":" + command_string + "\r\n").encode())
        try:
            return_val = self.s.readlines()[0].decode()
            print(str(type(return_val)) + ": " + str(return_val))
            return float(return_val)
        except:
            print("Output format not recognized")
            return -1.0
    
    def check_LCOS_temp(self):
        return

    def cool_LCOS(self, disable_time=15):
        #set current to LEDs to zero then disable all LEDs
        self.send_command("set ri=0:set gi=0:set bi=0")
        self.send_command("set a-l=0")

        #disable LCOS then wait
        
        self.send_command("set en_lcos=0")
        time.sleep(disable_time)

        #enable LCOS then wait until it's ready to receive commands again
        self.send_command("set en_lcos=1")
        #play with this value to garuntee no error, or check for ack string in return call else retry
        #once lcos has been re-enabled there is no need to re-able LEDs with a-l
        time.sleep(5)
        self.send_command("set mode=5")

        return
    
    def generate_DAC_char_xlsx(self, output_file_name):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Enter","Column","Headers","Here"])
        wb.save(output_file_name + ".xlsx")

DAC_Connection_Util()