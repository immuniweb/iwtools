#! /usr/bin/env python3

# Standard libraries
import logging
import pathlib
import json
import time
import sys

# Third-party libraries
from termcolor import colored
from colorama import init
import requests

# Local libraries
from lib.arguments import parse_args
from lib.logger import init_logging
from lib.keys import get_api_key

# Community services
from services.ssl import Ssl
from services.websec import Websec
# from services.mobile import Mobile
# from services.darkweb import Darkweb

# Debug libraries
from pprint import pprint


# Let's start
def main():
    # Parse arguments
    args = parse_args()


    # Init logger
    init_logging(args.output, args.format)


    # API key stuff
    api_key = None

    if args.api_key:
        api_key = args.api_key

    elif args.api_keyfile:
        api_key = get_api_key(args.api_keyfile, args.type)


    # Create test
    if args.type == 'websec':
        test = Websec(
            target = args.target,
            ip = args.ip,
            recheck = args.recheck,
            api_key = api_key,
            quiet = args.format != 'colorized_text',
        )
    elif args.type == 'ssl':
        test = Ssl(
            target = args.target,
            ip = args.ip,
            recheck = args.recheck,
            api_key = api_key,
            quiet = args.format != 'colorized_text',
        )
    elif args.type == 'darkweb':
        test = Ssl(
            target = args.target,
            recheck = args.recheck,
            api_key = api_key,
            quiet = args.format != 'colorized_text',
        )
    elif args.type == 'mobile':
        test = Mobile(
            target = args.target,
            recheck = args.recheck,
            api_key = api_key,
            quiet = args.format != 'colorized_text',
        )


    # Run test
    try:
        result = test.start()
    except Exception as error:
        logging.error(colored(error, 'red'))
        raise


    # Printing result
    if args.format == 'colorized_text':
        test.print_report()


    # Return raw API response
    if args.format in ['raw_json', 'pretty_json']:
        if args.format == 'raw_json':
            result = json.dumps(result)
        else:
            result = json.dumps(result, indent=4)

        if args.output:
            with open(args.output, 'w') as file:
                file.write(result)
        else:
            print(result)


# Init CLI
if __name__ == '__main__':
    # Init Colorama in Windows
    init()

    # Let's start
    main()
