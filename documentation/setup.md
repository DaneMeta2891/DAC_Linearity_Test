# Hardware:

## Required Hardware:
- keysight oscilloscope (MSOX4054A)
    - 1 passive probe
    - ethernet cable
    - power cable
- 1 goertek board
    - usb-A to mini-usb cable
    - 12V DC power supply
    - flex cable
- reworked DAC
    - sense wire (reference probe_point.png)
    - ground wire

# Setup:
    1) goertek setup
        1 - power and connect to goertek board via usb (refer to goertek pdf)
        2 - connect to DAC via flex cable
    2) scope setup
        1 - connect to scope via ethernet cable
            1 - find host name menu->utilities->I/O menu
            2 - use cli to configure host_name (refer to cli_manual)
        2 - connect passive probe to sense wire and ground wire
    
# Installation:
     - Supported python versions (verified): 3.7, 3.8, 3.10
        - if your version of python3 is not in the above list it probably still works
    1) repo
        1 - clone gitrepo
        2 - create virtual environment
            1 - python -m venv [venv_directory]
        3 - activate venv
        4 - install required packages from requirements.txt (in documentation)
        pip install -r requirements.txt

# Usage
    1) Script entry point is main.py, will take arguments outlined in cli_manual.py

## Notes:
    1) if dac_linearity_output.xlsx (or whatever filename you provided via the optional argument) is open in an editor the script may be unable to save the output data