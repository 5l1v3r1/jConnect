#!/usr/bin/env python

# -*- coding: utf-8 -*-
import urllib2
import os, sys, time
import argparse
import tempfile
from smb.SMBHandler import SMBHandler
from smb.SMBConnection import SMBConnection
import signal, time

# Console colors
W = '\033[1;0m'   # white 
R = '\033[1;31m'  # red
G = '\033[1;32m'  # green
O = '\033[1;33m'  # orange
B = '\033[1;34m'  # blue
Y = '\033[1;93m'  # yellow
P = '\033[1;35m'  # purple
C = '\033[1;36m'  # cyan
GR = '\033[1;37m'  # gray

current_path = os.path.dirname(os.path.realpath(__file__))
separate = "/" # use for linux
host = "http://j3ssiej.co.nf"
version = '1.0'
DEAULT_TIMEOUT = 2

# list_target = []
list_open = []
argv = {
	'target' : '',
	'port' : '',
	'output' : '',
	'raw_input' : ''
}

def banner():
	os.system("clear")
	print ("""{1}
	                                   
	   _ _____                     _   
	  |_|     |___ ___ ___ ___ ___| |_ 
	  | |   --| . |   |   | -_|  _|  _|
{0}	 _| |_____|___|_|_|_|_|___|___|_|  
	|___| {1}version:{2} {4}                             

	{1} Contact: {2}{3}{1}
	""".format(C, G, P, host, version))

def cowsay():
	os.system("clear")
	print ("""{1}
	  -----------------------------
	< You didn't say the {2}MAGIC WORD{1} >
	  ----------------------------- 
	         \   ^__^
	          \  (oo)\_______
	             (__)\       )\/
	             	\||----w |
	                 ||     ||
	""".format(C, G, P))

def present():
	dash = '|/-\\'
	dot = ['.', '..', '...', '....']
	for i in range(4):
		os.system("clear")
		banner()
		print("        {0}[{1}{2}{0}] Starting jShodan version {3} [{1}{2}{0}]  ".format(G, R, dash[i], version))
		time.sleep(0.1)
	banner()



def main():
	for i in range(3):
		present()
	cowsay()

	print("{}".format(P))
	parser = argparse.ArgumentParser()
	parser.add_argument('--target' , action='store', dest='TARGET', help='Enter IP or range of IP of target')
	parser.add_argument('--port', action='store', dest='PORT', help='Enter port of target')
	parser.add_argument('--write', action='store', dest='OUTPUT', help='Enter name of output')
	parser.add_argument('--raw_input', action='store', dest='RAW_INPUT', help='Enter name of target file')
	parser.add_argument('--version', action='version', version='%(prog)s {}'.format(version))
	results = parser.parse_args()

	if len(sys.argv) == 1:
		print("""{1}
Usage: jConnect.py [-h] [--target IP] [--port PORT] [--write OUTPUT] [--raw_input RAW_INPUT] [--version]
{0}
Example: $python jConnect.py --target="14.171.21.132/24" --port="445" --write="test"
	 
	 $python jConnect.py --raw_input="data.txt" --port="445" --write="data"
		  {2}""".format(G, B, W))
		exit(0)

	argv['target'] = str(results.TARGET)
	argv['port'] = str(results.PORT)
	argv['output'] = str(results.OUTPUT)
	argv['raw_input'] = str(results.RAW_INPUT)

	list_target = handle_input(argv)
	smb = jSmb(list_target,argv)
	print("{}".format(W))

def handle_input(argv):
	list_target = []
	if argv['raw_input'] == 'None':
		print('{}'.format(P)+ '=' * 80 + GR)
		command = 'masscan {0} -p{1} -oL {2}'.format(argv['target'], argv['port'], argv['output'])
		os.system(command)
		print('{}'.format(P)+ '=' * 80)
		with open(argv['output']) as f:
			list_data = f.readlines()
			list_data.remove('#masscan\n')
			list_data.remove('# end\n')

			for i in xrange(len(list_data)):
				list_target.append(list_data[i].split(' ')[3])
		return list_target
	else:
		with open(argv['raw_input']) as f:
			list_data = f.readlines()
			list_data = [ip.strip() for ip in list_data]
			list_target = [ip.replace('\n','') for ip in list_data]
		return list_target


class TimedOutExc(Exception):
    def __init__(self, value = "Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)

def TimedOutFn(f, timeout, *args, **kwargs):
    def handler(signum, frame):
        raise TimedOutExc()
    
    old = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = f(*args, **kwargs)
    finally:
        signal.signal(signal.SIGALRM, old)
    signal.alarm(0)
    return result

def timed_out(timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()
        
        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        
        new_f.func_name = f.func_name
        return new_f

    return decorate


class jSmb(object):
	"""docstring for jSmb"""
	def __init__(self, list_target, argv):
		self.list_target = list_target
		self.service = argv['port']
		self.filename = argv['output']
		self.check_smb()
		self.export_output()

	def check_smb(self):
		for ip in self.list_target:
			try:
				self.connect_smb(ip)
			except TimedOutExc:
				print("{2}[{4}]{3} {0} {1} ==> {2}Authenthication required. ".format(ip, W, R, C, self.service))

	@timed_out(DEAULT_TIMEOUT)
	def connect_smb(self, ip):
		try:
			conn = SMBConnection('guest', '', '', '', use_ntlm_v2 = True)
			assert conn.connect(ip, 445)
			conn.close()
			print("{2}[{4}]{3} {0} {1} ==> {2}Target seems to can access. ".format(ip, W, G, C, self.service))
			list_open.append(ip)

		except:
			print("{2}[{4}]{3} {0} {1} ==> {2}Authenthication required. ".format(ip, W, R, C, self.service))


	def export_output(self):
		print('{}'.format(P)+ '=' * 60)
		with open('output' + separate + self.filename, "w+") as o:
			for ip in list_open:
				o.write(ip + '\n')
		print("{0}[{1}*{0}] Check output in: {2}{3} ".format(G, R, B, current_path + separate + 'output' + separate + self.filename))
		print('{}'.format(P)+ '=' * 60)




if __name__ == '__main__':
	main()