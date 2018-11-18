import argparse
import sys
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Take in the configuration file")
    parser.add_argument('--config', help='The config file')

    args = parser.parse_args()

    if not args.config:
        print('You need to pass in the config file. Run with --help for more info')
        sys.exit(0)

    try:
        config_filename = args.config
        config_file = open(config_filename)
        config = json.load(config_file)
    except FileNotFoundError:
        print('Error opening the config file')
        sys.exit(0)
    print(config)
    

