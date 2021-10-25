#!/usr/bin/env python3

# TestPerf.py
# Author: Kristen Friday
# Date: September 22, 2021

import sys
import random
import string
import time
import HashTableClient


def time_outliers(client, sock):
    '''Measure fastest and slowest remove operations'''

    count = 0

    i_fastest = sys.maxsize
    i_slowest = 0
    r_fastest = sys.maxsize
    r_slowest = 0
    
    start = time.time_ns()

    # perform insert and remove operations for 3 seconds
    while time.time_ns() - start < 3000000000:
        # insert operations
        i_start = time.time_ns()
        new_key = (random.choice(string.ascii_letters) + \
                random.choice(string.ascii_letters)) * int((1+random.random()) * 3)
        response = client.insert(new_key, str(count), sock)
        i_end = time.time_ns()
        i_elap = i_end - i_start

        i_fastest = i_elap if i_fastest > i_elap else i_fastest
        i_slowest = i_elap if i_slowest < i_elap else i_slowest 
        
        # remove operations
        r_start = time.time_ns()
        response = client.remove(new_key, sock)
        r_end = time.time_ns()
        r_elap = r_end - r_start

        r_fastest = r_elap if r_fastest > r_elap else r_fastest
        r_slowest = r_elap if r_slowest < r_elap else r_slowest

        count += 2

    print("Outliers of Insert/Remove Operation:")
    print(f'Total Operations:   {count} operations\n')
    print(f"Fastest Insert:     {i_fastest} nanoseconds")
    print(f"Slowest Insert:     {i_slowest} nanoseconds") 
    print(f"Fastest Remove:     {r_fastest} nanoseconds")
    print(f"Slowest Remove:     {r_slowest} nanoseconds\n")


def get_cml_args():
    '''Get host and port number from command line'''

    if (len(sys.argv) != 3):
        print(f'Usage: ./TestPerf.py [HOST] [PORT]')
        return -1

    return (sys.argv[1], sys.argv[2])


def main():
    '''Runner function to test performance of each operation'''

    args = get_cml_args()
    if (args == -1):
        return 1

    host, port = args
    client = HashTableClient.HashTableClient()
    sock = client.connect_to_server(host, port)
    if not sock:
        print(f'ERROR: Could not connect to {host} at port {port}')
        return 1

    print("Processing requests...\n")
    time_outliers(client, sock)
    print("Done processing requests")


if __name__ == '__main__':
    main()
