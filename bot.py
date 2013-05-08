#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import re
import time
import codecs

class Sock(object):
    s = ''
    buf = ''

    def __init__(self, addr):
        self.s = socket.create_connection(addr)
        self.s.settimeout(3)

    def read(self):
        try:
            while '\n' not in self.buf:
                self.buf += bytes.decode(self.s.recv(128), 'utf-8')
            
            temp = self.buf.split('\r\n', 1)
            self.buf = temp[1]
            return temp[0]

        except socket.timeout:
            return ''

    def write(self, msg):
        self.s.send(bytearray(msg+'\r\n', 'utf-8'))

    def close(self, msg=''):
        if not msg == '':
            self.send(msg)

        self.s.shutdown(SHUT_RDWR)
        self.s.close()

def parse(msg):
    if not msg == '':
        temp = re.match(r'^(:([^ ]+) +)?([^ ]+)( (.*))?$', msg)

        if temp == None:
            print('ERROR - MALFORMED ANSWER: '+msg)
            return ()
        
        retval = [temp.group(2),temp.group(3)]
        temp = temp.group(5).split(':', 1)
        lastarg = ''

        if len(temp) > 1:
            lastarg = temp[1]
        
        temp = temp[0].split(' ')

        for i in temp:
            if not i == '':
                retval.append(i)

        if not lastarg == '':
            retval.append(lastarg)

        return tuple(retval)
    
    return ()

def act(tup):
    print(tup)

    if len(tup) > 0:
        sender = tup[0]
        command = tup[1]
        sendnick = ''
        res = ''

        if isinstance(sender, str):
            sendnick = sender.split('!', 1)[0]

        if command == '433':
            settings.NICK += '_'
            res = 'NICK '+settings.NICK
            act(parse(sock.read()))

        elif command == 'PING':
            res = 'PONG '+settings.UNAME

        elif command == 'PRIVMSG':
            addr = tup[2]
            msg = tup[3]

            if addr == settings.CHANNEL:
                if msg.startswith('\x01'):
                    msg = msg.replace('\x01', '')
                    msg = msg.replace('ACTION ', '* '+sendnick+' ', 1)
            
                else:
                    msg = sendnick+': '+msg
                    
                log(msg)
                
            if addr == settings.NICK:
                res = react(msg)

        elif command == 'JOIN':
            chan = tup[2]
            log(sendnick+" joined "+chan)

        elif command == 'PART':
            
            chan = tup[2]
            msg = tup[3]

            if msg == sendnick:
                msg=''

            log(sendnick+" left "+chan+" ("+msg+")")

        elif command == 'QUIT':
            msg = tup[2]
            log(sendnick+" has quit ("+msg+")")

        if not res == '':
            print(res)
            sock.write(res)

def log(line):
    clock = time.strftime('%H:%M')
    logfile.write(clock+' '+line+'\n')
    logfile.flush()

def react(command):
    return ''

import settings
logfile = codecs.open('log.'+settings.CHANNEL+time.strftime('.%y%m%d.%H%M'), 'a', 'utf-8')
sock = Sock((settings.HOST, settings.PORT))
hooks = ''

with codecs.open(settings.HOOKS, 'r', 'utf-8') as f:
    hooks = f.read()

sock.write('PASS '+settings.PASS)
act(parse(sock.read()))

sock.write('NICK '+settings.NICK)
act(parse(sock.read()))

sock.write('USER '+settings.UNAME+' localhost '+settings.HOST+' :'+settings.UNAME)
sock.write('JOIN '+settings.CHANNEL)

while True:
    line = sock.read()

    if not line == '':
        act(parse(line))
