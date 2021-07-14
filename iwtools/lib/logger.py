#! /usr/bin/env python3

# Standard libraries
import logging
import sys


def init_logging(file_path, output_format):
    logging_handlers = []

    # Set log destination
    if file_path:
        logging_handlers.append(logging.FileHandler(filename=file_path))
    else:
        logging_handlers.append(logging.StreamHandler(sys.stdout))

    # Disable logging if raw results
    if output_format == 'raw_json':
        logging.disable()

    # Init logging
    logging.basicConfig(
        handlers=logging_handlers,
        level=logging.INFO,
        format='%(message)s'
    )