#!/usr/bin/env python3

# TestPerf.py
# Author: Kristen Friday
# Date: September 5, 2021

import sys
import random
import string
import time
import HashTableClient


def time_insert(client, sock):
    '''Measure latency and bandwith of insert operation'''

    count = 0
    start = time.time_ns()

    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        new_key = (random.choice(string.ascii_letters) + \
                random.choice(string.ascii_letters)) * int((1+random.random()) * 3)
        response = client.insert(str(count), new_key, sock)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start

    
    print("Performance of Insert Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_lookup(client, sock):
    '''Measure latency and bandwith of lookup operation'''

    count = 0
    start = time.time_ns()

    # lookup all items in the dictionary
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        response = client.lookup(str(count), sock)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start
    
    print("Performance of Lookup Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_scan(client, sock):
    '''Measure latency and bandwith of scan operation'''

    count = 0
    start = time.time_ns()

    # scan dictionary for regex
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        regex = r'.*'
        response = client.scan(regex, sock)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start
    
    print("Performance of Scan Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_remove(client, sock):
    '''Measure latency and bandwith of remove operation'''

    count = 0
    start = time.time_ns()

    # remove all items in the dictionary
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        response = client.remove(str(count), sock)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start
    
    print("Performance of Remove Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def get_cml_args():
    '''Get host and port number from command line'''

    if (len(sys.argv) != 2):
        print(f'Usage: ./TestPerf.py [PROJECT]')
        return None

    return sys.argv[1]


def main():
    '''Runner function to test performance of each operation'''

    project = get_cml_args()
    if not project:
        return 1

    client = HashTableClient.HashTableClient()
    server = client.locate_server(project)
    if not server:
        print('Error: Could not locate project in name server')
        return 1

    host = server["address"]
    port = server["port"]

    sock = client.connect_to_server(host, port)
    if not sock:
        print(f'ERROR: Could not connect to {host} at port {port}')
        return 1

    print("Processing requests...\n")
    time_insert(client, sock)
    time_lookup(client, sock)
    time_scan(client, sock)
    time_remove(client, sock)
    print("Done processing requests")


if __name__ == '__main__':
    main()
