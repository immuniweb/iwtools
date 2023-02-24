#! /usr/bin/env python3

# Standard libraries
from ipaddress import ip_address
import argparse
import pathlib
import re


def is_ip(string):
    """Check is string is IP address"""

    try:
        ip_address(string)
        return True
    except:
        return False


def parse_args():
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    argparser.add_argument("type",
        help=(
            "This parameter specifies the test's type.\n"
            "    websec — Website Security Test\n"
            "    mobile — Mobile App Security Test\n"
            "    darkweb — Dark Web Exposure Test\n"
            "    ssl — SSL Security Test\n\n"
        ),
        type=str,
        metavar="TEST_TYPE",
        default="ssl",
        choices=["ssl", "websec", "darkweb", "mobile"]
    )

    api_key_group = argparser.add_mutually_exclusive_group()

    api_key_group.add_argument("--api-key",
        help="Pass your API key for a higher number of daily tests.",
        type=str
    )

    api_key_group.add_argument("--api-keyfile",
        help=(
            "Use file with API keys (more secure that passing as raw argument).\n"
            "Sample file content:\n"
            "websec ssl ABCDE-12345-FGHIJ-67890\n"
            "darkweb 12345-ABCDE-67890-FGHIJ\n\n"
        ),
        type=pathlib.Path
    )

    argparser.add_argument("-r", "--recheck",
        help="Force to refresh the test (API key required).",
        action="store_true"
    )

    argparser.add_argument("-i", "--ip",
        help="Force to use a specific IP address of the test's target.",
        type=str,
        default="any"
    )

    argparser.add_argument("-p", "--pipeline",
        help="Compare test result with config (websec and ssl only).",
        action="store_true",
        default=False
    )

    argparser.add_argument("-o", "--output",
        help="Path to the output file.",
        type=pathlib.Path
    )

    argparser.add_argument("-f", "--format",
        help=(
            "Output format.\n"
            "    colorized_text — Colorful human-readable text.\n"
            "    raw_json — API response in JSON format.\n"
            "    pretty_json — API response in pretty-printed JSON format.\n"
        ),
        type=str,
        metavar="FORMAT",
        default="colorized_text",
        choices=["colorized_text", "raw_json", "pretty_json"]
    )

    argparser.add_argument("target",
        help=(
            "Test's target.\n"
            "    URL for Web Security test\n"
            "    Hostname:Port for SSL Security test\n"
            "    Domain for Dark Web Exposure test\n"
            "    File path of a locally stored mobile application\n"
            "    Page of a mobile app published in application stores\n"
            "    URL of a self-hosted mobile application\n"
        ),
        metavar="TEST_TARGET",
        type=str
    )

    argparser.add_argument("-cfg", "--config-file",
        help=(
           "Use config file. json or yaml."
        ),
        type=pathlib.Path
    )

    args = argparser.parse_args()
    # If something wrong exception SystemExit and exit with code 2

    if args.recheck and (args.api_key is None and args.api_keyfile is None):
        argparser.error("Please pass your API key to refresh the test.")

    if args.type == 'ssl' and not re.match('^[\w-]+\.[\w-]+((\.[\w-]+)+)?:\d+$', args.target):
        argparser.error('Target format should be "hostname:port" for SSL security test.')

    if args.type == 'darkweb' and (is_ip(args.target) or not re.match('^[\w-]+\.[\w-]+((\.[\w-]+)+)?$', args.target)):
        argparser.error('Target format should be domain for dark web exposure test.')

    if args.type == 'websec' and '.' not in args.target:
        argparser.error('Target format should be URL for web security test.')

    if args.type == 'mobile' and '.' not in args.target:
        argparser.error('Target format should be URL or local path for mobile app security test.')

    if not args.ip == 'any' and not is_ip(args.ip):
        argparser.error('An invalid IP address was specified.')

    return args
