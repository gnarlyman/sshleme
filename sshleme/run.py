import sys
import os
import asyncio
import argparse
import csv
import importlib

from .lib import ConcurrentExecutor


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', dest='module', help='module to import', required=False, default='tasks')
    parser.add_argument('-r', dest='func_to_run', help='function to run', required=True)
    parser.add_argument('-c', dest='concur_count', type=int, help='how many connections to make (default: 50)', default=50)

    subparsers = parser.add_subparsers(title='commands', dest='command')

    hosts_parser = subparsers.add_parser('hosts', help=(
        'Process list of hosts.\n'
        'Each host will be passed though the task function.'
    ))

    hosts_parser.add_argument('-f', dest='hosts_path', help='list of hosts', required=True)

    csv_parser = subparsers.add_parser('csv', help=(
        'Process a csv.\n'
        'All items in a csv row will be available '
        'to the task function in the client object.'
    ))

    csv_parser.add_argument('-f', dest='csv_path', help='csv file', required=True)
    csv_parser.add_argument('-c', dest='host_column_name', help='csv column to use as host', required=True)

    return parser.parse_args()


def main():
    args = get_args()

    # add executing folder to sys.path so we can import the user's module
    sys.path.append(os.getcwd())
    try:
        module = importlib.import_module(args.module)
    except ImportError:
        print(f'failed to import \'{args.module}\'')
        sys.exit()

    func_to_run = getattr(module, args.func_to_run)

    loop = asyncio.get_event_loop()

    executor = ConcurrentExecutor(concurrent=args.concur_count)

    if args.command == 'hosts':
        ip_list = list(map(lambda ip: ip.strip(), open(args.hosts_path).readlines()))
        loop.run_until_complete(executor.run_func_on_hosts(ip_list, func_to_run))

    elif args.command == 'csv':
        with open(args.csv_path) as f:
            rows = [row for row in csv.DictReader(f)]

        loop.run_until_complete(executor.run_func_on_rows(rows, args.host_column_name, func_to_run))


if __name__ == '__main__':
    main()
