#! /usr/bin/env python3

# Standard libraries
import logging
import sys
import os


def init_logging(file_path, output_format):
    logging_handlers = []

    # Set log destination
    if file_path:
        logging_handlers.append(logging.FileHandler(filename=file_path))
    else:
        logging_handlers.append(logging.StreamHandler(sys.stdout))

    # Log level from enviroment
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

    # Disable logging if raw results
    if output_format in ['raw_json', 'pretty_json']:
        logging.disable(level=CRITICAL)

    # Init logging
    logging.basicConfig(
        handlers=logging_handlers,
        level=LOGLEVEL,
        format='%(message)s'
    )