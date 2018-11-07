#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

import binascii
import socket
import sys

from TrafficConstants import SERVER_HOST, SERVER_PORT


def initializeServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ((SERVER_HOST, SERVER_PORT))
    sock.bind(server_address)
    sock.listen(1)
    return sock


def listenForData(sock, runOnlyOnce=False):
    while True:
        try:
            print "Waiting for a connection"
            connection, client_address = sock.accept()
            while True:
                try:
                    data = connection.recv(500)
                    if data:
                        print "Recieved: '%s'" % binascii.hexlify(data)
                    else:
                        connection.close()
                        if runOnlyOnce:
                            connection.close()
                            sys.exit(0)
                        else:
                            break
                finally:
                    pass
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    sock = initializeServer()
    listenForData(sock)
