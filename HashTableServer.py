#!/usr/bin/env python3

# HashTableServer.py
# Author: Kristen Friday
# Date: September 19, 2021

# Contains the server-side RPC main program
# Accepts a port #, creates a TCP socket, accepts connections, decodes
# messages, invokes proper operation, returns result to client

import sys
import socket
import json
import HashTable
import os
import select
import time


# host is all available interfaces
HOST = None
BYTES = 1024
TRXN_LOG = "table.txn"
CHECK_FILE = "table.ckpt"
MAX_TRXNS = 100
NAME_HOST = 'catalog.cse.nd.edu'
NAME_PORT = 9097


class HashTableServer:

    def __init__(self):
        '''Initialize a server object with a hash table in memory'''

        self.hash_table = HashTable.HashTable()
        self.client_socks = {}


    def process_cml_args(self):
        '''Process command line arguments (port number)'''

        if (len(sys.argv) < 2):
            print('Usage: HashTableServer.py [PROJECT]')
            return None

        return sys.argv[1]


    def create_TCP_connection(self):
        '''Create a TCP connection on specified port; return the socket'''

        for res in socket.getaddrinfo(HOST, 0, socket.AF_UNSPEC, socket.SOCK_STREAM,
                0, socket.AI_PASSIVE):
            family, sock_type, _, _, sockaddr = res

            serv_socket = socket.socket(family, sock_type)
            serv_socket.bind(sockaddr)
            serv_socket.listen()

            print(f'Server: Listening on port {serv_socket.getsockname()[1]}')

            return serv_socket


    def form_response(self, res_info):
        '''Package together a response to send back to client given a json object'''
        
        response = json.dumps(res_info)
        response = (str(len(response)) + "," + response).encode('utf-8')

        return response


    def respond_with_failure(self, err, status="Failure"):
        '''Package error message for server response'''

        result = f'ERROR: {err}'
        res = {
            "status": status,
            "result": result
        }

        return self.form_response(res)


    def call_req_op(self, req):
        '''Invoke the correct hash table operation based on request'''

        method = req["method"]

        if (method == "insert"):
            if (type(req["key"]) != str):
                raise TypeError
        
            try:
                json_str = json.dumps(req["value"])
                json.loads(json_str)
            except json.decoder.JSONDecodeError:
                raise TypeError

            result = self.hash_table.insert(req["key"], req["value"])

            # add to transaction log
            self.add_transaction(req)
        elif (method == "lookup"):
            if (type(req["key"]) != str):
                raise TypeError
            result = self.hash_table.lookup(req["key"])
        elif (method == "remove"):
            if (type(req["key"]) != str):
                raise TypeError
            result = self.hash_table.remove(req["key"])
            
            # add to transaction log
            self.add_transaction(req)
        elif (method == "scan"):
            if (type(req["regex"]) != str):
                raise TypeError
            result = self.hash_table.scan(req["regex"])
        else:
            raise KeyError

        res = {
            "status": "Success",
            "result": result
        }

        # create new checkpoint file after MAX_TRXNS entries
        if (self.hash_table.num_trxns > MAX_TRXNS):
            self.compact_trxns()

        return self.form_response(res)


    def decode_request(self, client_conn):
        '''Decode a request sent by client'''

        # wait for client requests
        try:
            data = client_conn.recv(BYTES).decode('utf-8')
        except ConnectionResetError:
            print(f"Server: ConnectionResetError {client_conn.getsockname()}")
            return False

        # break if no more requests
        if not data:
            return False

        try:
            # split data received at first comma to get total bytes
            total_bytes, req = data.split(',',1)
            total_bytes = int(total_bytes)
        except ValueError as err:
            client_conn.sendall(self.respond_with_failure(err, "Invalid Request"))
            return True

        # ensure that all data packets are received in request
        while total_bytes > len(req):
            req += client_conn.recv(BYTES).decode('utf-8')
     
        try:
            json_data = json.loads(req)
        except ValueError:
            client_conn.sendall(self.respond_with_failure("Failed to load JSON",
                "Invalid Request"))
            return True

        try:
            client_conn.sendall(self.call_req_op(json_data))
        except KeyError:
            client_conn.sendall(self.respond_with_failure("KeyError",
                "Invalid Request"))
        except TypeError:
            client_conn.sendall(self.respond_with_failure("TypeError",
                "Invalid Request"))

        return True


    def dump_checkpoint(self):
        '''Generate a checkpoint file for the current state of the hash map'''

        tmp_file = f'{CHECK_FILE}.tmp'
        with open(tmp_file, "w") as fh:
            for key, value in self.hash_table.dictionary.items():
                json_data = {
                    "key": key,
                    "value": value
                }
                fh.write(json.dumps(json_data))
                fh.write("\n")

            # flush and sync file to disk
            fh.flush()
            os.fsync(fh.fileno())

        # rename file to perform atomic writing of checkpoint file
        os.rename(tmp_file, CHECK_FILE)


    def add_transaction(self, trxn):
        '''Add to transaction log for operations that alter the state of the table'''

        if not os.path.exists(TRXN_LOG):
            fh = open(TRXN_LOG, "w+")
            fh.flush()
            os.fsync(fh.fileno())
            fh.close()
            self.hash_table.trxn_fh = open(TRXN_LOG, "r+")

        self.hash_table.trxn_fh.write(json.dumps(trxn))
        self.hash_table.trxn_fh.write("\n")
        
        # flush and sync file to disk
        self.hash_table.trxn_fh.flush()
        os.fsync(self.hash_table.trxn_fh.fileno())

        self.hash_table.num_trxns += 1


    def compact_trxns(self):
        '''Create a new checkpoint file after storing over 100 transactions'''

        self.dump_checkpoint()
        self.hash_table.num_trxns = 0

        try:
            self.hash_table.trxn_fh = None
            os.remove(TRXN_LOG)
        except OSError:
            print("Unable to delete transaction file")


    def read_checkpoint(self):
        '''Read checkpoint file to get current state of hash table and load trxns'''

        print("Restoring previous checkpoint...")

        if not os.path.exists(CHECK_FILE):
            with open(CHECK_FILE, "w") as fh:
                fh.flush()
                os.fsync(fh.fileno())

        if not os.path.exists(TRXN_LOG):
            with open(TRXN_LOG, "w") as fh:
                fh.flush()
                os.fsync(fh.fileno())
        
        # load current checkpoint state of hash table
        with open(CHECK_FILE, "r") as fh:
            for line in fh:
                data = json.loads(line)
                result = self.hash_table.insert(data["key"], data["value"])
        
        # replay transactions
        trxn_fh = open(TRXN_LOG, "r+")
        self.hash_table.trxn_fh = trxn_fh
        for line in trxn_fh:
            json_req = json.loads(line)
            self.call_req_op(json_req)
            self.hash_table.num_trxns += 1

        print("Previous checkpoint restored\n")


    def conn_to_name_serv(self):
        '''Create a UDP socket connection the name server'''
        
        for res in socket.getaddrinfo(NAME_HOST, NAME_PORT, socket.AF_UNSPEC,
                socket.SOCK_DGRAM, 0):
            family, sock_type, _, _, sockaddr = res

            name_socket = socket.socket(family, sock_type)

            print(f'Server: Connected to name server')

            return name_socket, sockaddr



    def update_name_serv(self, sock, addr, port, proj_name, owner):
        '''Send update to name server describing hash table service'''

        json_data = {
            "type": "hashtable",
            "owner": owner,
            "port": port,
            "project": proj_name
        }

        status = json.dumps(json_data)

        sock.sendto(status.encode('utf-8'), addr)


def main():
    '''Runner function to spin up RPC server'''
    
    hash_server = HashTableServer()

    # get project name as command line argument
    project = hash_server.process_cml_args()
    if not project:
        return 1

    # load current state of hash table
    hash_server.read_checkpoint()

    try:
        serv_socket = hash_server.create_TCP_connection()
    except ConnectionResetError as err:
        return 1

    hash_server.client_socks[serv_socket.getsockname()] = serv_socket

    # connect socket to name server
    name_serv = hash_server.conn_to_name_serv()
    if not name_serv:
        print('Server: Could not connect to name server')
        return 1

    name_sock, name_addr = name_serv
    port_listen = serv_socket.getsockname()[1]

    # initially register in name server     
    hash_server.update_name_serv(name_sock, name_addr, port_listen, project, "kfriday")
    start = time.time()

    while True:
          
        # update name server every minute
        if (time.time() - start >= 60):
            hash_server.update_name_serv(name_sock, name_addr, port_listen, project, "kfriday")
            start = time.time()

        # check if any sockets are open; timeout after 60 seconds
        ready_socks, _, _ = select.select(hash_server.client_socks.values(), [], [], 60)
        for sock in ready_socks:
            if (sock == serv_socket):
                new_client, addr = serv_socket.accept()
                # set failure timeout to 30 seconds
                new_client.settimeout(30)

                # add client socket to dictionary
                hash_server.client_socks[addr] = new_client
                print(f'Server: Client connected: {addr}')
                continue

            try:
                sock_addr = sock.getpeername()
                if not hash_server.decode_request(sock):
                    # remove socket from dictionary
                    hash_server.client_socks.pop(sock_addr)
                    print(f'Server: Disconnecting {sock_addr}')
                    sock.close()
            except socket.error as err:
                sock.sendall(hash_server.respond_with_failure(err))

    serv_socket.close()
    name_sock.close()
    hash_server.hash_table.trxn_fh.close()

    return 0


if __name__ == '__main__':
    main()

