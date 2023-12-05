from arg_parser import arg_parser
from DAC_connection_util import DAC_Connection_Util

def main():
    test_settings = arg_parser().parse_args()
    print(test_settings)

main()