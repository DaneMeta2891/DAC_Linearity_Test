import openpyxl

from dac_connection_util import DAC_Connection_Util
from scope_config import scopeControl

class dac_test_control:
    def __init__(self):
        print()

    #used for context setting
    def __enter__(self):
        return self
    
    def __exit__(self, *a):
        print()

def cycle_DAC()

def generate_DAC_char_xlsx(DAC_control:DAC_Connection_Util, output_file_name:str = "DAC_Linearity_util"):
    '''
    generates .xlsx of current (mA) values for any given DAC value

    output_file_name (str): name of the given output file
    '''
    wb = openpyxl.Workbook()
    ws = wb.active
    
    #table header
    ws.append(["","","LC_Mode","","","HC_Mode"])
    ws.append(["DAC_Value","Red","Green","Blue","Red","Green","Blue"])

    #constants
    row_offset = 3
    
    #todo, change to 1024 once debug is complete
    DAC_range = 1024
    columns = {"LC_Mode" : {"red":"b", "green":"c", "blue":"d"}, "HC_Mode" : {"red":"e", "green":"f", "blue":"g"}}
    colors = {"red":"ri", "green":"gi", "blue":"bi"}

    #write DAC_value column
    for i in range(DAC_range):
        ws['a' + str(i + row_offset)] = str(i)

    #iterate through all possible permutations to fill out spreadsheet
    self.send_command("set l-grid=2")
    self.send_command("set ri=0:set gi=0:set bi=0")

    for mode in ("LC_Mode", "HC_Mode"):
        inc_coefficient = 0.33 if (mode == "HC_Mode") else 0.03
        self.send_command("set lc-lowc=" + str(0 if (mode == "HC_Mode") else 1), True, True)
        for color in ("red", "green", "blue"):
            for DAC_value in range(DAC_range):
                #cool LCOS if temp is above threshold every 12 steps
                if (DAC_value % 8 == 0):
                    if (self.check_LCOS_temp()):
                        self.cool_LCOS()

                #set current value for given DAC value and record current/DAC value
                self.send_command("set " + colors[color] + "=" + format(inc_coefficient * DAC_value, '0.2f'), True)

                #get and write current/DAC value to excel sheet
                ws[columns[mode][color] + str(row_offset + DAC_value)] = self.extract_return_val("get " + colors[color]) + "_" + self.extract_return_val("get " + colors[color] + "-ad")
                
            self.send_command("set " + colors[color] + "=0", True)

    wb.save(output_file_name + ".xlsx")