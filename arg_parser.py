from argparse import ArgumentParser, ArgumentError

#todo add hostname config option (look into adding additional parsers) to argparser and have it just edit scope_com.py with edit_host funcs
#todo: add option to configure oscope channel used
class arg_parser:
    def __init__(self):
        self.parser = ArgumentParser()
        self.parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging output")
        self.parser.add_argument("-c", "--config", type, help="configure host name")

        self.parser.add_argument("--run_all", action="store_true", help="Run all DACs on LC and HC mode")

        self.parser.add_argument("--current_mode", type=str, choices=["LC","HC"], help="Current mode")
        self.parser.add_argument("--dac_to_display", type=str, choices=["red","green","blue","ALL"], help="Target DAC")
        
        self.dac_range_arg = self.parser.add_argument("--dac_range", type=str, help="DAC range, format: ALL or (start_val)-(end_val)")
        self.display_mode_arg = self.parser.add_argument("--display_mode", type=str, help="Display mode, MIPI or l-grid=(1-8)")        

    def parse_args(self):
        args = self.parser.parse_args()
        test_settings = []

        if args.RUN_ALL:
            test_settings.append(["LC", "ALL", [0,1023], "l-grid=2", args.debug])
            test_settings.append(["HC", "ALL", [0,1023], "l-grid=2", args.debug])
        elif (args.current_mode != None and args.dac_to_display != None and args.dac_range != None and args.display_mode != None):
            test_settings.append([
                args.current_mode,
                args.dac_to_display,
                self.parse_DAC_range(args.dac_range),
                self.parse_display_mode(args.display_mode),
                args.debug
            ])
        else:
            print("Missing --current_mode, --dac_to_display, --dac_range and --display_mode; or --RUN_ALL")
        return test_settings

    #parse DAC range arg string 
    def parse_DAC_range(self, range_str):
        if (range_str.lower() == "all"):
            return [0, 1023]
        dac_range = range_str.split("-")
        if (not(len(dac_range) == 2 and dac_range[0].isdigit() and dac_range[1].isdigit())):
            raise ArgumentError(self.dac_range_arg, "Error, invalid DAC range format")
        if (dac_range != sorted(dac_range)):
            raise ArgumentError(self.dac_range_arg, "Error, DAC range values out of order")
        for i in range(len(dac_range)):
            dac_range[i] = int(dac_range[i])
            if dac_range[i] > 1023: raise ArgumentError(self.dac_range_arg, "Error, Value provided exceeded 1023")
        return dac_range

    def parse_display_mode(self, display_mode):
        arg_split = display_mode.split("=")
        if arg_split[0].lower() == "mipi":
            return "l-mipi=1"
        elif arg_split[0].lower() == "l-grid":
            if len(arg_split) == 2 and arg_split[1].isdigit():
                if 0 <= int(arg_split[1]) <= 8:
                    return display_mode
                else:
                    raise ArgumentError(self.display_mode_arg, "Error, invalid l-grid value provided")
            else:
                raise ArgumentError(self.display_mode_arg, "Error, invalid argument: use \"MIPI\" or \"l-grid=(1-8)\"")
        else:
            raise ArgumentError(self.display_mode_arg, "Error, invalid argument: use \"MIPI\" or \"l-grid=(1-8)\"")
        