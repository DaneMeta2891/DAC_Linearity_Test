import openpyxl
import time

from dac_connection_util import dacConnectionUtil
from scope_config import scopeControl

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

    def config_scope_step(self, dac_value:int):
        '''
        config scope to measure voltage for dac_value step

        dac_value (int): dac_value of current step
        '''
        self.scope.vertical_config(self.convert_dacval_to_voltage(dac_value))
        self.scope.reset_meas_stats()

    #todo: test dac_loop
    #todo: find way to provide list of colors to test (currently just a single selection or all)
    def dac_loop(
            self, 
            dac_start_index:int=0, 
            dac_end_index:int=1023, 
            current_mode:tuple = ("lc", "hc"),
            led_colors:tuple = ("red", "green", "blue"),
            output_file_name:str="dac_linearity_output", 
            generate_excel:bool=True,
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

            columns = {
                    "lc" : {
                "red_maximum":"b", "red_top":"c", 
                "green_maximum":"d", "green_top":"e", 
                "blue_maximum":"f", "blue_top":"g" }, 
                    "hc" : {
                "red_maximum":"h", "red_top":"i", 
                "green_maximum":"j", "green_top":"k", 
                "blue_maximum":"l", "blue_top":"m" }, 
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
            self.dac.send_command("set lc-lowc=" + str(0 if (mode == "hc") else 1), False, True)
            for color in led_colors:
                for dac_value in range(dac_start_index, dac_end_index):
                    #cool LCOS if temp is above threshold every 12 steps
                    if (dac_value % 8 == 0):
                        if (self.dac.check_LCOS_temp()):
                            self.dac.cool_LCOS()

                    #set current value for given DAC value and record current/DAC value
                    self.dac.send_command("set " + colors[color] + "=" + format(inc_coefficient * dac_value, '0.2f'), False)

                    if (generate_excel):
                        self.config_scope_step(dac_value)
                        time.sleep(STEP_TIME_DELAY)
                        for meas in ("Top", "Maximum"):
                            meas_return = self.scope.get_target_meas_data(meas, 3)
                            ws[columns[mode][color + "_" + meas.lower()] + str(row_offset + dac_value)] = meas_return
                    
                self.dac.send_command("set " + colors[color] + "=0", False)

        if (generate_excel):
            wb.save(output_file_name + ".xlsx")