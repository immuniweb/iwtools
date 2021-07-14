#! /usr/bin/env python3

def get_api_key(keyfile, service):
    """Get API key from file"""

    keys = {}
    with open(keyfile, 'r') as file:
        for line in file:
            data = line.split(' ')
            for record in data:
                if record == service:
                    return data[-1]

    return None