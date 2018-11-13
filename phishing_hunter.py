#!/usr/bin/python
# -*- coding: utf-8 -*-

####################
#      TO DO       #
####################
#Check "Index Of" and parse tree to get files

import urllib.request
import sys
import getopt
from urllib.parse import urlparse

if (sys.version_info < (3, 0)):
	print("")
	print("ERROR: Please, use Python3")
	print("command: apt-get install python3")
	print("")
	sys.exit()

try:
	import pip
except:
	call(["apt-get", "install", "python3-pip"])


def start(argv):
	if len(sys.argv) < 2:
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(argv, "u:")
	except getopt.GetoptError:
		usage()
		sys.exit()

	extensions = ['.zip', '.rar', '.7z']

	for opt, arg in opts:
		if opt == '-u':
			url = arg
		if opt == '-h':
			usage()
			sys.exit()

	test_char = 0
	s,n,p,pa,q,f = urlparse(url)

	for u in p:
		if u == '/':
			new_url = (n + p[:test_char])
			for y in extensions:
				try:
					kit = urllib.request.urlopen(new_url + y).read()
				except Exception as e:
					print(e)
			test_char += 1
		else:
			test_char += 1
		# if "index of" in urllib.request.urlopen(new_url).read():
		# 	print('Index Of Available')

def usage():
	print("\nUsage: phishing_hunter.py -u <url>\n")
	print("	-u  : full url of the phishing kit\n")
	print("	-h  : show this menu\n")

if __name__ == "__main__":
	try:
		start(sys.argv[1:])
	except KeyboardInterrupt:
		print("Search interrupted by user...")
		sys.exit()