from arg_parser import arg_parser
from dac_test import dac_test_control

def edit_const(replacement_val:str, var_name:str, file_name:str):
    '''
    edits the [file_name] script [var_name] value to [replacement_val]

    replacement_val (str): str to replace value of variable (var_name) with
    var_name (str): name of variable to replace the value of (with replacement_val)
    file_name (str): file where target var 
    '''
    with open(file_name, 'r') as file:
        script = file.readlines()
    with open(file_name, 'w') as file:
        for line in script:
            if (line.find(var_name + " = ") != -1):
                file.write(var_name + " = " + replacement_val + "\n")
            else:
                file.write(line)

def main():
    test_settings = arg_parser().parse_args()
    if (test_settings[0] == "config"):
        if (test_settings[1] != ""):
            edit_const("\"" + test_settings[1] + "\"", "HOST_NAME", "scope_com.py")
        if (test_settings[2] != -1):
            edit_const(str(test_settings[2]), "SCOPE_CHANNEL", "scope_config.py")
        if (test_settings[3] != -1):
            edit_const(str(test_settings[3]), "STEP_TIME_DELAY", "dac_test.py")
    elif (test_settings[0] == "run"):
        with dac_test_control() as test_control:
            if (not(test_control.check_connections())):
                print("unable to start test")
                return
            test_control.dac_test(test_settings[1])

main()