#! /usr/bin/env python3

import json
import logging
import yaml

from pathlib import PosixPath

def get_api_key(keyfile, service):
    """Get API key from file"""

    with open(keyfile, 'r') as file:
        for line in file:
            data = line.split(' ')
            for record in data:
                if record == service:
                    return data[-1]

    return None


def get_config(config_file: PosixPath):
    config = {}
    file_arr = str(config_file).split(".")
    ext = file_arr[len(file_arr) - 1]
    with open(config_file, 'r') as file:
        logging.info("Load settings from config file: %s" % config_file)
        if ext == 'json':
            config = json.load(file)
        elif ext == 'yaml':
            config = yaml.safe_load(file)

    return config
