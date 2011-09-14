#!/usr/bin/python          

import socket
import sys

HOST = '10.50.218.106'
PORT = 3000

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    sys.stderr.write("[ERROR] %s\n" % msg)
    sys.exit(1)
print 'Connected'

try:
    sock.connect((HOST, PORT))
except socket.error as msg: 
    sys.stderr.write("[ERROR] %s\n" % msg)
    sys.exit(2)

sock.send(b'INIT {ClassName USARBot.KR6} {Location .4, .4, 1.8}\r\n') 
data = sock.recv(4024)
print data

sock.send(b'GETGEO {Type Robot}\r\n') 
data = sock.recv(4024)
print data

raw_input('Press Enter to quit')
sock.close()
print 'Done.'
