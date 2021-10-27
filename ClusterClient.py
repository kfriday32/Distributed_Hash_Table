#!/usr/bin/env python3

# ClusterClient.py
# Author: Kristen Friday
# Date: October 25, 2021

# Implements client clustering technique for the 4 operations

import socket
import json
import time
import http.client
import HashTableClient


class ClusterClient:

    def __init__(self, n, k, proj_name):
        '''Constructor for ClusterClient object'''

        self.n = n
        self.k = k
        self.project = proj_name
        self.servers = {}

        for i in range(n):
            serv_name = proj_name + "-" + str(i)
            new_client = HashTableClient.HashTableClient()
            new_client.locate_server(serv_name)

            if not new_client.server:
                print('Error: Could not locate project in name server')
                return 1

            self.servers[serv_name] = new_client


    def call_operation(self, client, message):
        '''Helper function to call operation with appropriate server'''

        host = client.server["name"]
        port = client.server["port"]
        sock = client.connect_to_server(host, port)
        if not sock:
            print(f'ERROR: Could not connect to {host} at port {port}')
            return 1

        return client.process_request(sock, message, 1)


    def insert(self, key, value):
        '''Client stub to support insert operations'''

        message = {
            "method": "insert",
            "key": key,
            "value": value
        }

        clients = self.find_clients(key)

        response = None
        for client in clients:
            response = self.call_operation(client, message)
            if (response["status"] == "Invalid Request"):
                break
            while (response["status"] == "Failure"):
                # sleep for 5 seconds and then retry
                time.sleep(5)
                response = self.call_operation(client, message)

        return response


    def lookup(self, key):
        '''Client stub to support lookup operations'''

        message = {
            "method": "lookup",
            "key": key,
        }
        
        clients = self.find_clients(key)
        
        response = None
        for client in clients:
            response = self.call_operation(client, message)
            if (response["status"] == "Invalid Request"):
                break
            while (response["status"] == "Failure"):
                # sleep for 5 seconds and then retry
                time.sleep(5)
                response = self.call_operation(client, message)

        return response
       

    def remove(self, key):
        '''Client stub to support remove operations'''

        message = {
            "method": "remove",
            "key": key
        }
        
        clients = self.find_clients(key)

        response = None
        for client in clients:
            response = self.call_operation(client, message)
            if (response["status"] == "Invalid Request"):
                break

        return response


    def scan(self, regex):
        '''Client stub to support scan operations'''

        message = {
            "method": "scan",
            "regex": regex,
        }

        for client in self.servers.values():
            print(self.call_operation(client, message))
        

    def hash_server(self, key):
        '''Function that returns a hash value for a given key'''

        return hash(key) % self.n


    def find_clients(self, key):
        '''Function that locates the HashTableClient object associated
        with the correct server'''

        clients = []
        server_num = self.hash_server(key)

        for i in range(self.k):
            server_num += i

            if (server_num >= self.n):
                server_num = 0

            serv_name = self.project + "-" + str(server_num)
            clients.append(self.servers[serv_name])

        return clients

