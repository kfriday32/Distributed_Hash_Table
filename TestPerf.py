#!/usr/bin/env python3

# TestPerf.py
# Author: Kristen Friday
# Date: October 31, 2021

import sys
import random
import string
import time
import ClusterClient


def time_insert(client):
    '''Measure latency and bandwith of insert operation'''

    count = 0
    start = time.time_ns()

    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        new_key = (random.choice(string.ascii_letters) + \
                random.choice(string.ascii_letters)) * int((1+random.random()) * 3)
        response = client.insert(str(count), new_key)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start

    
    print("Performance of Insert Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_lookup(client):
    '''Measure latency and bandwith of lookup operation'''

    count = 0
    start = time.time_ns()

    # lookup all items in the dictionary
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        response = client.lookup(str(count))
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start
    
    print("Performance of Lookup Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_scan(client):
    '''Measure latency and bandwith of scan operation'''

    count = 0
    start = time.time_ns()

    # scan dictionary for regex
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        regex = r'.*'
        response = client.scan(regex)
        op_end = time.time_ns()
        op_elap = op_end - op_start
        count += 1

    elapsed = time.time_ns() - start
    
    print("Performance of Scan Operation:")
    print(f"Elapsed Time:          {elapsed / (10 ** 9)} seconds")
    print(f"Total Operations:      {count} operations")
    print(f"Bandwith (ops/sec):    {count / (elapsed / (10 ** 9)):.0f} ops/second")
    print(f"Latency (avg time/op): {elapsed / count:.0f} nanoseconds/op\n")


def time_remove(client):
    '''Measure latency and bandwith of remove operation'''

    count = 0
    start = time.time_ns()

    # remove all items in the dictionary
    while time.time_ns() - start < 3000000000: 
        op_start = time.time_ns()
        response = client.remove(str(count))
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
    '''Get project name from command line'''

    if (len(sys.argv) != 4):
        print(f'Usage: ./TestPerf.py [NAME] [N] [K]')
        return None

    return sys.argv[1:]


def main():
    '''Runner function to test performance of each operation'''

    args = get_cml_args()
    if not args:
        return 1

    project, n, k = args
    n = int(n)
    k = int(k)

    cluster_client = ClusterClient.ClusterClient(n, k, project)

    print("Processing requests...\n")
    time_insert(cluster_client)
    time_lookup(cluster_client)
    time_scan(cluster_client)
    time_remove(cluster_client)
    print("Done processing requests")


if __name__ == '__main__':
    main()
