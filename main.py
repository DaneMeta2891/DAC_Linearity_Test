from arg_parser import arg_parser

def main():
    test_settings = arg_parser().parse_args()
    print(test_settings)

main()