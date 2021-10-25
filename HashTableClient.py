#!/usr/bin/env python3

# HashTableClient.py
# Author: Kristen Friday
# Date: September 13, 2021

# Provides a method to connect to server host/port and a client-stub
# for each of the 4 operations (sends message; waits for response)

import socket
import json
import time
import http.client


BYTES = 1024
NAME_HOST = 'catalog.cse.nd.edu:9097'


class HashTableClient:

    def connect_to_server(self, host, port):
        '''Return a socket that connects client to host and port'''

        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, 
                socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            family, sock_type, _, _, sockaddr = res
            client_socket = socket.socket(family, sock_type)
            # throw error if request doesn't process in 30 seconds
            client_socket.connect(sockaddr)
            return client_socket


    def process_request(self, sock, message, retries):
        '''Send request to server and receive response back'''
       
        try:
            req_info = json.dumps(message)
        except ValueError as err:
            raise ValueError

        request = (str(len(req_info)) + "," + req_info).encode('utf-8')

        try:
            sock.sendall(request)
            data = sock.recv(BYTES).decode('utf-8')
            res_bytes, res = data.split(',', 1)
            while int(res_bytes) > len(res):
                res += sock.recv(BYTES).decode('utf-8')

            res_json = json.loads(res)

            # retry 5 times
            if res_json["status"] == "Failure" and retries < 5:
                retries += 1
                time.sleep(3)
                return self.process_request(sock, message, retries)

            return res_json

        except socket.error as err:
            raise err


    def insert(self, key, value, socket):
        '''Client stub to support insert operations'''

        message = {
            "method": "insert",
            "key": key,
            "value": value
        }

        return self.process_request(socket, message, 1)


    def lookup(self, key, socket):
        '''Client stub to support lookup operations'''

        message = {
            "method": "lookup",
            "key": key,
        }
        
        return self.process_request(socket, message, 1)


    def remove(self, key, socket):
        '''Client stub to support remove operations'''

        message = {
            "method": "remove",
            "key": key
        }
        
        return self.process_request(socket, message, 1)


    def scan(self, regex, socket):
        '''Client stub to support scan operations'''

        message = {
            "method": "scan",
            "regex": regex,
        }
        
        return self.process_request(socket, message, 1)


    def locate_server(self, proj_name):
        '''Make an HTTP request to the catalog server to locate hash table server'''

        http_conn = http.client.HTTPConnection(NAME_HOST)
        http_conn.request('get', '/query.json')
        response = http_conn.getresponse()
        data = response.read().decode('utf-8')
        json_data = json.loads(data)

        # find entry with type=hashtable and proj_name = server
        server = None
        update_time = None
        for entry in json_data:
            try:
                if (entry["project"] != proj_name or entry["type"] != "hashtable"):
                    continue

                # if server w/ same project name, choose the most recent
                if (update_time == None or update_time < entry["lastheardfrom"]):
                    server = entry
                    update_time = entry["lastheardfrom"]
            except KeyError:
                continue

        return server
