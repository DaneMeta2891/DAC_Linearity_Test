## V1.00.00

### Initial release

    - The script will configure oscilloscope, drive DAC, take measurements and record the results given provided CLI arguments

## V1.00.1
    - added optional debug arg to run_all cmd
    - changed display_mode arg to be optional and added a default value

## V1.00.2
    - added led-disable commands for all non-active LEDs in any given test step

## V1.00.3
    - added checking for invalid measurement return value
    - fixed issue with cool_lcos(), was not re-enabling LEDs after cooling