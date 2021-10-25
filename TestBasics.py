#!/usr/bin/env python3

# TestBasics.py
# Author: Kristen Friday
# Date: September 5, 2021


import sys
import json
import re
import HashTableClient


BYTES = 1024


def test_insert(client, sock):
    '''Test RPC insertion method'''

    response = client.insert("Kristen", {"age": "20", "gender": "female"}, sock)
    print(response)
    response = client.insert("Kelly", {"age": "25", "gender": "female"}, sock)
    print(response)
    response = client.insert("Matt", {"age": "23", "gender": "male"}, sock)
    print(response)
    response = client.insert("Leigh", {"age": "57", "gender": "female"}, sock)
    print(response)
    response = client.insert("Bill", {"age": "58", "gender": "male"}, sock)
    print(response)
    response = client.insert("", "", sock)
    print(response)
    response = client.insert(None, None, sock)
    print(response)
    response = client.insert(1, {"age": "57", "gender": "female"}, sock)
    print(response)
    response = client.insert("Tim", {"age": 58, "gender": "male"}, sock)
    print(response)
    response = client.insert("Ted", 1, sock)
    print(response)


def test_lookup(client, sock):
    '''Test RPC lookup method'''
    
    response = client.lookup("Kristen", sock)
    print(response)
    response = client.lookup("notInDictionary", sock)
    print(response)
    response = client.lookup("Matt", sock)
    print(response)
    response = client.lookup(None, sock)
    print(response)
    response = client.lookup(1, sock)
    print(response)
    

def test_remove(client, sock):
    '''Test RPC remove method'''

    response = client.remove("Kristen", sock)
    print(response)
    response = client.remove("not present", sock)
    print(response)
    response = client.remove("Matt", sock)
    print(response)
    response = client.remove(1, sock)
    print(response)
    

def test_scan(client, sock):
    '''Test RPC scan method'''

    regex = "^K.*"
    response = client.scan(regex, sock)
    print(response)

    response = client.insert("Loon", {"age": 29, "gender": "male"}, sock)
    print(response)
    
    regex = ".*([a-z]).*"
    response = client.scan(regex, sock)
    print(response)
    
    regex = ".*([a-z])\\1.*"
    response = client.scan(regex, sock)

    regex = ".*[i].*"
    response = client.scan(regex, sock)
    print(response)
   
    # invalid regex should raise exception
    regex = ".*("
    response = client.scan(regex, sock)
    print(response)

    regex = None
    response = client.scan(regex, sock)
    print(response)


def test_edge_cases(client, sock):
    '''Test methods intermixed with each other'''

    response = client.insert("Sean", {"age": 40, "gender": "male"}, sock)
    print(response)
    response = client.lookup("Sean", sock)
    print(response)
    response = client.remove("Sean", sock)
    print(response)
    response = client.lookup("Sean", sock)
    print(response)

    response = client.remove("Key not in dictionary", sock)
    print(response)
    

def get_cml_args():

    if (len(sys.argv) != 2):
        print(f'Usage: ./TestBasics.py [PROJECT]')
        return None

    return sys.argv[1]


def main():
    '''Runner function to test basic functionality'''

    proj_name = get_cml_args()
    if not proj_name:
        return 1

    client = HashTableClient.HashTableClient()
    server = client.locate_server(proj_name)
    if not server:
        print('Error: Could not locate project in name server')
        return 1

    host = server["address"]
    port = server["port"]
    
    sock = client.connect_to_server(host, port)
    if not sock:
        print(f'ERROR: Could not connect to {host} at port {port}')
        return 1

    test_insert(client, sock)
    test_lookup(client, sock)
    test_remove(client, sock)
    test_scan(client, sock)
    test_edge_cases(client, sock)
    sock.close()


if __name__ == '__main__':
    main()
