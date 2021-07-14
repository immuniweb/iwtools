#! /usr/bin/env python3

import argparse
import pathlib
import re


def parse_args():
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    argparser.add_argument("type",
        help=(
            "This parameter specifies the test's type.\n"
            "    websec — Website Security Test\n"
            "    mobile — Mobile App Security Test\n"
            "    darkweb — Dark Web Exposure Test\n"
            "    ssl — SSL Security Test\n"
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
        help="Use file with api keys (more secure than raw argument).",
        type=pathlib.Path
    )

    argparser.add_argument("-q", "--quiet",
        help="Print only the grade and found problems.",
        action="store_true"
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
            "Test target.\n"
            "    URL For web security test\n"
            "    Hostname:Port for SSL security test\n"
            "    File path for local mobile application test\n"
            "    Page of mobile app in application stores for published mobile application test\n"
            "    URL of mobile app for selfhosted mobile application test\n"
        ),
        metavar="TEST_TARGET",
        type=str
    )

    args = argparser.parse_args()

    if args.recheck and (args.api_key is None and args.api_keyfile is None):
        argparser.error("Please pass your API key to refresh the test.")

    if args.type == 'ssl' and not re.match('^[\w.]+:\d+$', args.target):
        argparser.error('Target format should be "hostname:port" for SSL security test.')

    if args.type == 'websec' and not '.' not in args.target:
        argparser.error('Target format should be URL for web security test.')

    if args.type == 'darkweb' and '.' not in args.target:
        argparser.error('Target format should be URL for dark web exposure test.')

    if args.type == 'mobile' and '.' not in args.target:
        argparser.error('Target format should be URL or local path for mobile app security test.')

    return args
