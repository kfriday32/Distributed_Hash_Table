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
import hashlib
import sys


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
                sys.exit()

            self.servers[serv_name] = new_client


    def call_operation(self, client, message):
        '''Helper function to call operation with appropriate server'''

        host = client.server["name"]
        port = client.server["port"]

        try:
            sock = client.connect_to_server(host, port)
        except ConnectionRefusedError:
            message = f"Could not connect to {host} at port {port}"
            return {"status": "Failure",
                    "result": message}

        return client.process_request(sock, message)


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
            try:
                response = self.call_operation(client, message)
            except TypeError:
                response = {
                    "status": "Invalid Request",
                    "error": "TypeError"
                }
                break
            except ValueError:
                response = {
                    "status": "Invalid Request",
                    "error": "ValueError"
                }
                break
            except socket.error:
                response = {
                    "status": "Failure",
                    "error": "socket.error"
                }
            while (response["status"] == "Failure"):
                # sleep for 5 seconds and then retry
                time.sleep(5)
                client.locate_server(client.server["project"])
                response = self.call_operation(client, message)

        return response


    def lookup(self, key):
        '''Client stub to support lookup operations'''

        message = {
            "method": "lookup",
            "key": key,
        }
        
        clients = self.find_clients(key)
        
        key_errors = 0
        response = None
        while (1):
            for client in clients:
                try:
                    response = self.call_operation(client, message)
                except TypeError: 
                    return {
                        "status": "Invalid Request",
                        "error": "TypeError"
                    }
                except KeyError:
                    response = {
                        "status": "Success",
                        "error": "KeyError"
                    }
                    key_errors += 1
                except ValueError:
                    return {
                        "status": "Invalid Request",
                        "error": "ValueError"
                    }
                except socket.error:
                    response = {
                        "status": "Failure",
                        "error": "socket.error"
                    }
                if (response["status"] == "Success"):
                    return response
        
            if (key_errors == len(clients)):
                return response
            else:
                key_errors = 0

            # sleep for 5 seconds and then retry
            time.sleep(5)
            clients = self.find_clients(key)

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
            try: 
                response = self.call_operation(client, message)
            except TypeError: 
                return {
                    "status": "Invalid Request",
                    "error": "TypeError"
                }
            except KeyError:
                response = {
                    "status": "Success",
                    "error": "KeyError"
                }
            except ValueError:
                return {
                    "status": "Invalid Request",
                    "error": "ValueError"
                } 
            except socket.error:
                response = {
                    "status": "Failure",
                    "error": "socket.error"
                }
            while (response["status"] == "Failure"):
                # sleep for 5 seconds and then retry
                time.sleep(5)
                client.locate_server(client.server["project"])
                response = self.call_operation(client, message)

        return response


    def scan(self, regex):
        '''Client stub to support scan operations'''

        message = {
            "method": "scan",
            "regex": regex,
        }

        response = None
        results = {}
        for client in self.servers.values():
            try:
                response = self.call_operation(client, message)
            except TypeError: 
                return {
                    "status": "Invalid Request",
                    "error": "TypeError"
                }
            except ValueError:
                return {
                    "status": "Invalid Request",
                    "error": "ValueError"
                }
            except socket.error:
                response = {
                    "status": "Failure",
                    "error": "socket.error"
                }
            while (response["status"] == "Failure"):
                # sleep for 5 seconds and then retry
                time.sleep(5)
                clients = self.find_clients(key)
                response = self.call_operation(client, message)
            
            if (type(response["result"]) == str):
                return response
            
            for item in response["result"]:
                results[item[0]] = item

        response["result"] = list(results.values())

        return response
        

    def hash_server(self, key):
        '''Function that returns a hash value for a given key'''

        try:
            hash_digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
            hash_num = int(hash_digest, 16)

            return hash_num % self.n

        # return 0 for the server is key can't be hashed
        # will throw invalid request response later
        except AttributeError:
            return 0


    def find_clients(self, key):
        '''Function that locates the HashTableClient object associated
        with the correct server'''

        clients = []
        server_num = self.hash_server(key)

        for _ in range(self.k):

            if (server_num >= self.n):
                server_num = 0

            serv_name = self.project + "-" + str(server_num)
            clients.append(self.servers[serv_name])
            
            server_num += 1

        return clients

