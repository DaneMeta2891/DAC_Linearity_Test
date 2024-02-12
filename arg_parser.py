from argparse import ArgumentParser, ArgumentError

class arg_parser:
    def __init__(self):
        self.parser = ArgumentParser()

        subparser = self.parser.add_subparsers(help="command:\noptions: run, run_all or config", dest="cmd", required=True)

        config = subparser.add_parser("config")
        config.add_argument("--host_name", type=str, default="", help="host name, can be found within the scope's IP_config menu")
        config.add_argument("--channel", type=int, default=-1, help="channel dac probe is connected to")
        config.add_argument("--step_delay", type=int, default=-1, help="time delay before measurement data is captured per step")

        run = subparser.add_parser("run")
        run.add_argument("--current_mode", type=str, nargs='+', choices=["lc","hc"], help="current mode", required=True)
        run.add_argument("--leds", type=str, nargs='+', choices=["red","green","blue","all"], help="target dac", required=True)

        self.dac_range_arg = run.add_argument("--dac_range", type=str, help="dac range, format: all or (start_val)-(end_val) inclusive", required=True)
        self.display_mode_arg = run.add_argument("--display_mode", type=str, default="l-grid=2", help="display mode, mipi or l-grid=(1-8)")

        run.add_argument("--output_filename", type=str, default="dac_linearity_output", help="filename of output excel doc")

        run.add_argument("-d", "--debug", action="store_true", help="enable console debug output")

        run_all = subparser.add_parser("run_all")
        run_all.add_argument("-d", "--debug", action="store_true", help="enable console debug output")

    def parse_args(self):
        args = self.parser.parse_args()
        test_settings = []

        if (args.cmd == "run_all"):
            test_settings.append("run")
            test_settings.append([["lc", "hc"], ["all"], [0,1023], "l-grid=2", "dac_linearity_output", args.debug])
        elif (args.cmd == "run"):
            test_settings.append("run")
            test_settings.append([
                args.current_mode,
                args.leds,
                self.parse_DAC_range(args.dac_range),
                self.parse_display_mode(args.display_mode),
                args.output_filename,
                args.debug
            ])
        elif (args.cmd == "config"):
            test_settings.append("config")
            test_settings.append(args.host_name)
            test_settings.append(args.channel)
            test_settings.append(args.step_delay)
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
                raise ArgumentError(self.display_mode_arg, "Error, invalid argument: use \"mipi\" or \"l-grid=(1-8)\"")
        else:
            raise ArgumentError(self.display_mode_arg, "Error, invalid argument: use \"mipi\" or \"l-grid=(1-8)\"")