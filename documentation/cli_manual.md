# run
    - main.py is the entry point for the script
        - There are two options which run the test, run and run_all
    - main -h:
        positional arguments:
            {config,run,run_all}  command: options: run, run_all or config

        optional arguments:
            -h, --help            show this help message and exit
## run
    - run has 3 required args and 3 optional args
        - required arguments:
            - current_mode, leds, dac_range
        - optional args:
            - display_mode, output_filename, debug
        - run -h:
            optional arguments:
            -h, --help            show this help message and exit
            --current_mode {lc,hc} [{lc,hc} ...]
                                    current mode
            --leds {red,green,blue,all} [{red,green,blue,all} ...]
                                    target dac
            --dac_range DAC_RANGE
                                    dac range, format: all or (start_val)-(end_val)
                                    inclusive
            --display_mode DISPLAY_MODE
                                    display mode, mipi or l-grid=(1-8)
            --output_filename OUTPUT_FILENAME
                                    filename of output excel doc
            -d, --debug           enable console debug output

## run_all
    - will run all LED colors at both LC and HC mode through every DAC value (0-1023)
        - WARNING: This will result in a very long running test
            - depending on the value of STEP_TIME_DELAY in dac_test (this can be edited with the config cmd)
                - example: (3 (LEDs) * 2 (LC & HC mode) * 1024 (DAC_RANGE) * 30 (STEP_TIME_DELAY)) => 184,320 sec => 51.2 hrs
        - run_all -h:
            optional arguments:
            -h, --help   show this help message and exit
            -d, --debug  enable console debug output
# config
    - allows the user to configure STEP_TIME_DELAY (in dac_test.py), SCOPE_CHANNEL (in scope_config.py), HOST_NAME (in scope_com.py)
        - STEP_TIME_DELAY: edits the time delay after configuring the scope and DAC per step
        - SCOPE_CHANNEL: edits the scope channel which will be configured and from which measurements will be taken
        - HOST_NAME: host name, used to get scope IP. can be found in IP_config of scope
            - WARNING: must be configured correctly in order to connect to the scope
    - examples:
        - python .\main.py config --host_name "a-mx4054a-00115"
        - python .\main.py config --channel 3
    - config -h:
        optional arguments:
        -h, --help            show this help message and exit
        --host_name HOST_NAME
                                host name, can be found within the scope's IP_config
                                menu
        --channel CHANNEL     channel dac probe is connected to
        --step_delay STEP_DELAY
                                time delay before measurement data is captured per
                                step