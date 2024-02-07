import openpyxl
import time

from dac_connection_util import dacConnectionUtil
from scope_config import scopeControl

#todo: record both max and top values

#dac value to expected current conversion constants
HC_CONST = 0.33029
LC_CONST = 0.030665

class dac_test_control:
    def __init__(self):
        self.dac = dacConnectionUtil()
        self.scope = scopeControl()

    def __enter__(self):
        '''
        context setting
        '''
        return self
    
    def __exit__(self, *a):
        '''
        context setting, disconnects scope and DAC
        '''
        del self.dac, self.scope

    def convert_dacval_to_voltage(self, current_mode:str, dac_value:int)->float:
        '''
        convert a dac value to an expected voltage (mV)

        HC mode:
        
        
        current_mode (str): DAC current setting
            "lc" or "hc"
        dac_value (int): dac value to convert to voltage
        '''
        expected_current = dac_value * (HC_CONST if (current_mode == "hc") else LC_CONST)

        return
    
    def convert_voltage_to_current(self, current_mode:str, voltage:float)->float:
        '''
        convert a measured voltage value to the corresponding current value (mA)

        HC mode:
        voltage (V) / 0.046 (ohms) = current (a)

        LC mode:
        voltage (V) / 5.1 (ohms) = current (a)

        current_mode (str): DAC current setting
            "lc" or "hc"
        voltage (float): measured voltage value
        '''

        return voltage/0.046 if (current_mode == "hc") else voltage/5.1

    def config_scope_step(self, dac_value:int, channel:int=1):
        '''
        config scope to measure voltage for dac_value step

        dac_value (int): dac_value of current step
        channel (int): scope channel
        '''
        self.scope.vertical_config(channel, self.convert_dacval_to_voltage(dac_value))
        self.scope.reset_meas_stats()

    def dac_loop(
            self, 
            dac_start_index:int=0, 
            dac_end_index:int=1024, 
            current_mode:tuple = ("lc", "hc"),
            led_colors:tuple = ("red", "green", "blue"),
            output_file_name:str="dac_linearity_output", 
            generate_excel:bool=True
            ):
        '''
        loop through DAC values from start_index to end_index on LEDs in colors list

        dac_start_index (int): start DAC value index
        dac_end_index (int): end DAC value index
        current_mode (tuple): set current mode for loop iteration
            lc=low current, hc=high current
        led_colors (tuple): tuple of LED colors that loop will iterate through
            possible values: "red", "green", "blue"
        output_file_name (str): file name that .xlsx will be saved for
        generate_excel (bool): will save excel doc of current measured by scope if True
        '''
        if (generate_excel):
            wb = openpyxl.Workbook()
            ws = wb.active
        
            #table header
            ws.append(["","","LC_Mode","","","HC_Mode"])
            ws.append(["DAC_Value","Red","Green","Blue","Red","Green","Blue"])

        #constants
        row_offset = 3
        
        if (generate_excel):
            columns = {"LC_Mode" : {"red":"b", "green":"c", "blue":"d"}, "HC_Mode" : {"red":"e", "green":"f", "blue":"g"}}
        colors = {"red":"ri", "green":"gi", "blue":"bi"}

        #write DAC_value column
        for i in range(dac_start_index, dac_end_index):
            ws['a' + str(i + row_offset)] = str(i)

        #iterate through all possible permutations to fill out spreadsheet
        self.dac.send_command("set l-grid=2")
        self.dac.send_command("set ri=0:set gi=0:set bi=0")

        for mode in current_mode:
            inc_coefficient = HC_CONST if (mode == "hc") else LC_CONST
            self.dac.send_command("set lc-lowc=" + str(0 if (mode == "hc") else 1), True, True)
            for color in led_colors:
                for DAC_value in range(dac_start_index, dac_end_index):
                    #cool LCOS if temp is above threshold every 12 steps
                    if (DAC_value % 8 == 0):
                        if (self.dac.check_LCOS_temp()):
                            self.dac.cool_LCOS()

                    #set current value for given DAC value and record current/DAC value
                    self.dac.send_command("set " + colors[color] + "=" + format(inc_coefficient * DAC_value, '0.2f'), True)

                    if (generate_excel):
                        #config scope for step(call func)
                        #wait 30-60 secs
                        #get value (ask if top or max should be used) and store in excel sheet
                        #ws[columns[mode][color] + str(row_offset + DAC_value)] = get scope meas mean value
                    
                self.dac.send_command("set " + colors[color] + "=0", True)

        if (generate_excel):
            wb.save(output_file_name + ".xlsx")