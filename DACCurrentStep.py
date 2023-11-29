import openpyxl
from argparse import ArgumentParser, ArgumentError

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging output")

    parser.add_argument("--RUN_ALL", action="store_true", help="Run all DACs on LC and HC mode")

    parser.add_argument("--current_mode", type=str, choices=["LC","HC"], help="Current mode")
    parser.add_argument("--dac_to_display", type=str, choices=["red","green","blue","ALL"], help="Target DAC")
    
    dac_range = parser.add_argument("--dac_range", type=str, help="DAC range, format: ALL or (start_val)-(end_val)")
    display_mode = parser.add_argument("--display_mode", type=str, nargs="+", help="Display mode, MIPI or l-grid (1-8)")

    #check if not(--RUN_ALL is used, ensure all other args are provided)

    args = parser.parse_args()
    test_settings = []
    if args.RUN_ALL:
        #ask what l-grid setting to use
        test_settings.append(["LC", "ALL", [0,1023], "l-grid=2"])
        test_settings.append(["HC", "ALL", [0,1023], "l-grid=2"])
    else:
        test_settings.append([
            args.current_mode,
            args.dac_to_display,
            parse_DAC_range(args.dac_range, dac_range),
            parse_display_mode(args.display_mode, display_mode)
        ])

    return test_settings

#parse DAC range arg string 
#implement better error checking to ensure string is formatted correctly
def parse_DAC_range(range_str, dac_range_arg):
    if (range_str.lower() == "all"):
        return [0, 1023]
    dac_range = range_str.split("-")
    for i in range(len(dac_range)):
        dac_range[i] = int(dac_range[i])
        if dac_range[i] > 1023: raise ArgumentError(dac_range_arg, "Error, Value provided exceeded 1023")
    return dac_range

def parse_display_mode(display_Args, display_mode_arg):
    if display_Args[0].lower() == "mipi":
        return "l-mipi=1"
    elif display_Args[0].lower() == "l-grid":
        if len(display_Args) == 2:
            if 1 <= int(display_Args[1]) <= 8:
                return "l-grid=" + display_Args[1]
            else:
                raise ArgumentError(display_mode_arg, "Error, l-grid: second arg outside of range (1-8)")
        else:
            raise ArgumentError(display_mode_arg, "Error, l-grid: incorrect number of arguments provided")
    else:
        raise ArgumentError(display_mode_arg, "Error, invalid argument: use \"MIPI\" or \"l-grid (1-8)\"")


parse_args()