#!/usr/bin/env python3

# TestBasics.py
# Author: Kristen Friday
# Date: October 27, 2021


import sys
import json
import re
import ClusterClient


BYTES = 1024


def test_insert(client):
    '''Test RPC insertion method'''

    response = client.insert("Kristen", {"age": "20", "gender": "female"})
    print(response)
    response = client.insert("Kelly", {"age": "25", "gender": "female"})
    print(response)
    response = client.insert("Matt", {"age": "23", "gender": "male"})
    print(response)
    response = client.insert("Leigh", {"age": "57", "gender": "female"})
    print(response)
    response = client.insert("Bill", {"age": "58", "gender": "male"})
    print(response)
    response = client.insert("", "")
    print(response)
    response = client.insert(None, None)
    print(response)
    response = client.insert(1, {"age": "57", "gender": "female"})
    print(response)
    response = client.insert("Tim", {"age": 58, "gender": "male"})
    print(response)
    response = client.insert("Ted", 1)
    print(response)


def test_lookup(client):
    '''Test RPC lookup method'''
    
    response = client.lookup("Kristen")
    print(response)
    response = client.lookup("notInDictionary")
    print(response)
    response = client.lookup("Matt")
    print(response)
    response = client.lookup(None)
    print(response)
    response = client.lookup(1)
    print(response)
    

def test_remove(client):
    '''Test RPC remove method'''

    response = client.remove("Kristen")
    print(response)
    response = client.remove("not present")
    print(response)
    response = client.remove("Matt")
    print(response)
    response = client.remove(1)
    print(response)
    

def test_scan(client):
    '''Test RPC scan method'''

    regex = "^K.*"
    response = client.scan(regex)
    print(response)

    response = client.insert("Loon", {"age": 29, "gender": "male"})
    print(response)
    
    regex = ".*([a-z]).*"
    response = client.scan(regex)
    print(response)
    
    regex = ".*([a-z])\\1.*"
    response = client.scan(regex)

    regex = ".*[i].*"
    response = client.scan(regex)
    print(response)
   
    # invalid regex should raise exception
    regex = ".*("
    response = client.scan(regex)
    print(response)

    regex = None
    response = client.scan(regex)
    print(response)
    
    regex = "^.*"
    response = client.scan(regex)
    print(response)


def test_edge_cases(client):
    '''Test methods intermixed with each other'''

    response = client.insert("Sean", {"age": 40, "gender": "male"})
    print(response)
    response = client.lookup("Sean")
    print(response)
    
    regex = "^.*"
    response = client.scan(regex)
    print(response)

    response = client.remove("Sean")
    print(response)
    response = client.lookup("Sean")
    print(response)

    response = client.remove("Key not in dictionary")
    print(response)
    

def get_cml_args():

    if (len(sys.argv) != 4):
        print(f'Usage: ./TestBasics.py [PROJECT] [N] [K]')
        return None

    return sys.argv[1:]


def main():
    '''Runner function to test basic functionality'''

    args = get_cml_args()
    if not args:
        return 1

    proj_name, n, k = args
    n = int(n)
    k = int(k)

    cluster_client = ClusterClient.ClusterClient(n, k, proj_name)
    
    test_insert(cluster_client)
    test_lookup(cluster_client)
    test_remove(cluster_client)
    test_scan(cluster_client)
    #test_edge_cases(cluster_client)


if __name__ == '__main__':
    main()
