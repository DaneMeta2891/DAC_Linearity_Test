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
                    print(self.extract_return_val(userCmd[1:]))
                elif (userCmd[0] == 'c'):
                    print("Cooling LCOS")
                    self.cool_LCOS()
                else:
                    self.send_command(userCmd, True)
            else:
                self.s.close()
                break
    
    def send_command(self, command_string, debug_flag=False, loop_until_success = False):
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
    
    def extract_return_val(self, command_string):
        self.s.flush()
        self.s.write((":" + command_string + "\r\n").encode())
        try:
            return self.s.readlines()[0].decode().strip()
        except:
            print("Output format not recognized")
            return -1
    
    def check_LCOS_temp(self, temp_threshold=60):
        if (float(self.extract_return_val("get temp-lc")) > temp_threshold):
            return True
        else:
            return False

    #todo: test cool-lcos with debug flag set to true for each command
    def cool_LCOS(self, disable_time=20):
        print("Disabling LCOS for " + str(disable_time) + " seconds")

        #set current to LEDs to zero
        self.send_command("set ri=0:set gi=0:set bi=0")

        #disable LCOS then wait until it cools down
        self.send_command("set en_lcos=0")
        time.sleep(disable_time)

        #enable LCOS then wait until it's ready to receive commands again
        self.send_command("set en_lcos=1")
        time.sleep(5)
        self.send_command("set mode=5", False, True)
    
    #assume 0.33 or 0.03 inc value and move this functionality to within generate_DAC_char_xlsx
    #
    def increment_DAC_value(self, led_color, current_mode, DAC_current_value):
        #continue moving useful sections of this function into generate_DAC_char_xlsx
        self.send_command("set " + color_dict[led_color] + "=" + str(current_value))  
        current_value = initial_current_value = float(self.extract_return_val("get " + color_dict[led_color]))
        DAC_value = int(self.extract_return_val("get " + color_dict[led_color] + "-ad"))
        
        while (DAC_value + 1 != int(self.extract_return_val("get " + color_dict[led_color] + "-ad"))):
            current_value += inc_const
            self.send_command("set " + color_dict[led_color] + "=" + format(current_value, "0.2f"), True, False)
        current_value = float(self.extract_return_val("get " + color_dict[led_color]))
        
        return current_value - initial_current_value

    #generates .xlsx of current (mA) values for any given DAC value
    def generate_DAC_char_xlsx(self, output_file_name):
        wb = openpyxl.Workbook()
        ws = wb.active
        
        #table header
        ws.append(["","","LC_Mode","","","HC_Mode"])
        ws.append(["DAC_Value","Red","Green","Blue","Red","Green","Blue"])

        #constants for incrementation
        row_offset = 4
        columns = {"LC_Mode" : {"Red":"B", "Green":"C", "Blue":"D"}, "HC_Mode" : {"Red":"E", "Green":"F", "Blue":"G"}}
        colors = {"red":"ri", "green":"gi", "blue":"bi"}


        #iterate through all possible permutations to fill out spreadsheet
        self.send_command("set ri=0:set gi=0:set bi=0")
        for mode in ("LC_Mode", "HC_Mode"):
            inc_const = 0.33 if (mode == "HC_Mode") else 0.03
            self.send_command("set lc-lowc=" + str(0 if (mode == "HC_Mode") else 1), False, True)
            for color in ("red", "green", "blue"):
                current_value = 0
                for DAC_value in range(1024):
                    #cool LCOS if temp is above threshold
                    if (self.check_LCOS_temp()):
                        self.cool_LCOS()
                    self.send_command("set " + colors[color] + "=" + format(current_value, '0.2f'))
                    current_value = float(self.extract_return_val("get " + colors[color]))
                    
                    current_value += inc_const

        wb.save(output_file_name + ".xlsx")

DAC_Connection_Util()