#! /usr/bin/env python3

# Standard libraries
import logging
import json
# import traceback

# Local libraries
from lib.arguments import parse_args
from lib.logger import init_logging
from lib.keys import get_api_key
from lib.exit_code import ExitCode
from gui.termcolor import colored

# Community services
from services.ssl import Ssl
from services.websec import Websec
from services.mobile import Mobile
from services.darkweb import Darkweb
from services.email import Email
from services.cloud import Cloud
from services.checker import Checker
from services.services import Services
from services.config import Config

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
    if args.type == Services.WEBSEC:
        test = Websec(
            target = args.target,
            ip = args.ip,
            recheck = args.recheck,
            api_key = api_key,
            quiet = (args.format != 'colorized_text'),
        )
    elif args.type == Services.SSL:
        test = Ssl(
            target = args.target,
            ip = args.ip,
            recheck = args.recheck,
            api_key = api_key,
            quiet = (args.format != 'colorized_text'),
        )
    elif args.type == Services.DARKWEB:
        test = Darkweb(
            target = args.target,
            recheck = args.recheck,
            api_key = api_key,
            quiet = (args.format != 'colorized_text'),
        )
    elif args.type == Services.MOBILE:
        test = Mobile(
            target = args.target,
            recheck = args.recheck,
            api_key = api_key,
            quiet = (args.format != 'colorized_text'),
        )
    elif args.type == Services.EMAIL:
        test = Email(
            target = args.target,
            recheck = args.recheck,
            api_key = api_key,
            quiet = (args.format != 'colorized_text'),
        )
    elif args.type == Services.CLOUD:

        quick = args.quick != "false"

        test = Cloud(
            target = args.target,
            api_key = api_key,
            recheck = args.recheck,
            quick = quick,
            quiet = (args.format != 'colorized_text'),
        )
    else:
        exit(ExitCode.COMMAND_ERROR)

    # Run test
    try:
        result = test.start()
    except Exception as error:
        logging.error(colored("Error in run test: ", "red") + str(error))
        # print(traceback.format_exc())
        result = {'error': str(error)}
        raw_api_resp(args, result)

        exit(ExitCode.ERROR)

    if args.pipeline and args.type in [Services.WEBSEC, Services.SSL, Services.EMAIL]:
        try:
            config_service = Config.get_config(args.type, args.config_file)
            checker = Checker(args.type)
            checker.check(config_service, result)
            logs = checker.get_log()
        except FileNotFoundError as error:
            logging.error(colored("Error: ", "red") + "can't load config file. " + str(error))
            exit(ExitCode.COMMAND_ERROR)
        except Exception as error:
            # print(traceback.format_exc())
            logging.error(colored("Error: ", "red") + str(error))
            exit(ExitCode.ERROR)

        is_passed = True
        if len(logs) == 0:
            logging.info("No checks have been made")
        for log in logs:
            color = 'green' if log['passed'] else 'red'
            passed_str = 'passed' if log['passed'] else 'failed'
            logging.info(colored(passed_str, color) + ' ' + log['key'])
            if 'msg' in log:
                logging.info(log['msg'])
            if not log['passed']:
                is_passed = False

        exit_msg = colored("FAILED", "red")
        exit_code = ExitCode.CHECK_FAILED
        if is_passed:
            exit_msg = colored("PASSED", "green")
            exit_code = ExitCode.SUCCESS
        logging.info(f"\nChecks {exit_msg}\n")
        logging.info("Test result details: " + test.get_test_link(result))
        exit(exit_code)

    # Printing result
    if args.format == "colorized_text":
        try:
            test.print_report()
        except Exception:
            logging.info(colored("Cannot print report", "red"))

    raw_api_resp(args, result)


# Return raw API response
def raw_api_resp(args, result):
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
    # init()

    # Let's start
    main()
