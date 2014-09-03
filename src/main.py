#!/usr/bin/env python

import argparse
import datetime
import sys

import engine
import server

#from reader import read_requests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Perform sequenced REST requests'
    )

    parser.add_argument(
        '--server',
        action='store_true',
        help='Run the server version'
    )
    parser.add_argument(
        '--port',
        type=int,
        nargs='?',
        help='Port on which server will be run (8888 is the default)'
    )
    parser.add_argument(
        'request',
        type=str,
        help='Request name to run',
        nargs='?'
    )
    parser.add_argument(
        'config',
        type=str,
        help='Config name to use',
        nargs='?'
    )

    args = parser.parse_args()

    if args.server:
        server.serve(port=args.port)
        sys.exit(0)

    request = args.request
    config = args.config

    if request is None or config is None:
        parser.error('request and config must be given together')

    engine.make_request(request, config)
