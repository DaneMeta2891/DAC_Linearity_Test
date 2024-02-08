import openpyxl
import time

from dac_connection_util import dacConnectionUtil
from scope_config import scopeControl

#todo: record both max and top values

#time delay before gettig mean value per setp
STEP_TIME_DELAY = 30

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
        voltage (V) = current (A) * 0.046 (ohms)
        
        LC mode;
        voltage (V) = current (A) * 5.1 (ohms)
        
        current_mode (str): DAC current setting
            "lc" or "hc"
        dac_value (int): dac value to convert to voltage
        '''
        #converted dac_value to expected current (in mA)
        expected_current_mA = dac_value * (HC_CONST if (current_mode == "hc") else LC_CONST)

        #convert mA to A
        expected_current = expected_current_mA * 0.001

        return expected_current * 0.046 if (current_mode == "hc") else expected_current * 5.1
    
    def convert_voltage_to_current(self, current_mode:str, voltage:float)->float:
        '''
        convert a measured voltage value to the corresponding current value (mA)

        HC mode:
        current (A) = voltage (V) / 0.046 (ohms)

        LC mode:
        current (A) = voltage (V) / 5.1 (ohms)

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
    
    def get_scope_means(self, channel:int=1):
        '''
        gets mean for top and max measurements
        '''
        return (self.scope.get_target_meas_data("Top", channel, 3), self.scope.get_target_meas_data("Maximum", channel, 3))

    def dac_loop(
            self, 
            scope_channel:int = 1,
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
            ws.append(["","","LC_Mode","","","","","","HC_Mode"])
            ws.append(["DAC_Value","Red","","Green","","Blue","","Red","","Green","","Blue",""])
        
            row_offset = 3
            #todo, finish changes to loop, write max and top to seperate columns
            columns = {"LC_Mode" : {
                "red_max":"b", "red_top":"c", 
                "green_max":"d", "green_top":"e", 
                "blue_max":"f", "blue_top":"g" }, 
                        "HC_Mode" : {
                "red_max":"h", "red_top":"i", 
                "green_max":"j", "green_top":"k", 
                "blue_max":"l", "blue_top":"m" }, 
                }

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
                for dac_value in range(dac_start_index, dac_end_index):
                    #cool LCOS if temp is above threshold every 12 steps
                    if (dac_value % 8 == 0):
                        if (self.dac.check_LCOS_temp()):
                            self.dac.cool_LCOS()

                    #set current value for given DAC value and record current/DAC value
                    self.dac.send_command("set " + colors[color] + "=" + format(inc_coefficient * dac_value, '0.2f'), True)

                    if (generate_excel):
                        self.config_scope_step(dac_value, scope_channel)
                        time.sleep(STEP_TIME_DELAY)
                        ws[columns[mode][color] + str(row_offset + dac_value)] = 
                    
                self.dac.send_command("set " + colors[color] + "=0", True)

        if (generate_excel):
            wb.save(output_file_name + ".xlsx")