#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import zipfile
import os
import socket
import datetime
import hashlib
import resource
from multiprocessing.dummy import Pool
from .grabber import Grabber

class mod_phish(Grabber):
	def __init__(self, db, logger, rootDir):
		self.db = db
		self.logger = logger
		self.rootDir = rootDir
		
	def get_kit(self, id_phish, url):
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate"
		}
		socket.setdefaulttimeout(5)
		page = set()
		dirList = []
		extensions = ['.zip']#, '.7z', '.rar', '.xz', '.gz']
		test_char = 0
		s,n,p,pa,q,f = urlparse(url)

		try:
			for char in p:
				if char == '/' or char == '.':
					new_url = (n + p[:test_char])
					for extension in extensions:
						try:
							if not os.path.exists(self.rootDir + '/' + n):
								for dirName, subdirList, fileList in os.walk(self.rootDir):
									dirName = dirName.rsplit("/", 1)[1]
									dirList.append(dirName)
									if n not in dirList:
										os.makedirs(self.rootDir + '/' + n)
							urllib.request.urlretrieve('http://' + new_url + extension, self.rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension)
							try:
								with zipfile.ZipFile(self.rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension, "r") as z:
									z.extractall(self.rootDir + '/' + n + '/')
									self.db.phishing.update({"_id": id_phish}, {"$set": {"kit_name": new_url.rsplit('/', 1)[1] + extension, "kit_presence": "true", "frauder_checked": "false"}})
							except zipfile.BadZipFile as i:
								os.remove(self.rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension)
								self.logger.debug(i)
								pass
						except Exception as e:
							self.logger.debug(e)
							pass
					self.get_index('http://' + new_url)
					test_char += 1
				else:
					test_char += 1
			if not os.listdir(self.rootDir + '/' + n):
				os.rmdir(self.rootDir + '/' + n)
				self.db.phishing.update({"_id": id_phish}, {"$set": {"kit_presence": "false"}})
		except Exception as e:
			self.logger.debug(e)
			pass

	def get_index(self, site):
		global page
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate"
		}

		try:
			conn = urllib.request.Request(site, None, headers)
			raw = urllib.request.urlopen(conn, timeout=2)
			bsObj = BeautifulSoup(raw, "html5lib")
			form = bsObj.find('title').getText()
			if 'Index of' in form:
				for links in bsObj.findAll('a', href=True):
					if 'href' in links.attrs:
						if links.attrs['href'] not in page:
							if '.' not in links.attrs['href']:
								newPage = links.attrs['href']
								page.add(newPage)
								get_index(site + '/' + newPage)
							else:
								urllib.request.urlretrieve(site + links.attrs['href'], self.rootDir + '/' + n + '/' + links.attrs['href'])
		except Exception as e:
			self.logger.debug(e)
			pass
