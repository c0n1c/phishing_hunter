#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import zipfile
import os
import socket
import datetime
import hashlib
import resource
import pymongo
import time
import urllib.request
from multiprocessing.dummy import Pool
import queue
import threading
from configparser import ConfigParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs_phish.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
scrlog = logging.StreamHandler()
scrlog.setFormatter(logging.Formatter("[%(levelname)s] - (%(funcName)s) - %(message)s"))
logger.addHandler(scrlog)

headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/52.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Encoding": "gzip, deflate"
		}
limit = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/resource.getrlimit(resource.RLIMIT_STACK)[0])
today = datetime.datetime.now().strftime("%Y%m%d")
rootDir = 'Data/phishing/' + today

def read_config(option ,section='scheduler', filename='config.ini'):
	parser = ConfigParser()
	parser.read(filename)
	if parser.has_section(section):
		if parser.has_option(section, option):
			value = parser.get(section, option)
		else:
			raise Exception('{0} option not found in the {1} section'.format(option, section))
	else:
		raise Exception('{0} section not found in the {1} file'.format(section, filename))
	return value

def get_kit(id_phish, url):
	socket.setdefaulttimeout(5)
	page = set()
	dirList = []
	url = url.decode("utf-8")[:-1]
	extensions = ['.zip']#, '.7z', '.rar', '.xz', '.gz']
	test_char = 0
	s,n,p,pa,q,f = urlparse(url)
	logger.info(str(url))

	try:
		for char in p:
			if char == '/' or char == '.':
				new_url = (n + p[:test_char])
				for extension in extensions:
					try:
						if not os.path.exists(rootDir + '/' + n):
							for dirName, subdirList, fileList in os.walk(rootDir):
								dirName = dirName.rsplit("/", 1)[1]
								dirList.append(dirName)
								if n not in dirList:
									os.makedirs(rootDir + '/' + n)
						urllib.request.urlretrieve('http://' + new_url + extension, rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension)
						try:
							with zipfile.ZipFile(rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension, "r") as z:
								z.extractall(rootDir + '/' + n + '/')
								db.phishing.update({"_id": id_phish}, {"$set": {"kit_name": new_url.rsplit('/', 1)[1] + extension, "kit_presence": "true", "frauder_checked": "false"}})
						except zipfile.BadZipFile as i:
							os.remove(rootDir + '/' + n + '/' + new_url.rsplit('/', 1)[1] + extension)
							logger.debug(i)
							pass
					except Exception as e:
						logger.debug(e)
						pass
				get_index('http://' + new_url)
				test_char += 1
			else:
				test_char += 1
		if not os.listdir(rootDir + '/' + n):
			os.rmdir(rootDir + '/' + n)
			db.phishing.update({"_id": id_phish}, {"$set": {"kit_presence": "false"}})
	except Exception as e:
		logger.warning(e)
		pass

def get_index(site):
	global page
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
							urllib.request.urlretrieve(site + links.attrs['href'], rootDir + '/' + n + '/' + links.attrs['href'])
	except Exception as e:
		logger.warning(e)
		pass

def phishing(db):
	try:
		logger.info("Launching phishing kit hunter...")
		global count
		if not os.path.exists(rootDir):
			os.makedirs(rootDir)
			logger.info("%s is created", rootDir)
		# phish_grab = mod_phish(db, logger, rootDir)
		phish_items = db.phishing.find({"kit_checked": "false"})
		logger.debug(phish_items)
		logger.info("%s URLs will be checked", phish_items.count())
		
		limit = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/resource.getrlimit(resource.RLIMIT_STACK)[0]/2)
		feed_list = []
		valid_list = []

		try:
			feed = open('feed.txt', 'r')
			for line in feed.readlines():
				line = line[:-1]
				feed_list.append(line)
			sample = int(len(feed_list)/limit)
			pool = Pool(limit)
			pool.map(get_kit, feed_list, sample)
			pool.close()
			pool.join()

		except Exception as e:
			print(e)
			pass

		# def worker():
		# 	while True:
		# 		try:
		# 			item = q.get()
		# 			result = get_kit(item["_id"], item["url"])
		# 			db.phishing.update({"_id": item["_id"]}, {"$set": {"kit_checked": "true"}})
		# 			q.task_done()
		# 			pass
		# 		except Exception as e:
		# 			logger.debug(e)
		# 			continue

		# threads = []
		# q = queue.Queue(maxsize=0)
		# num_threads = int(limit/100)
		# logger.info("%d threads", num_threads)

		# for x in range(num_threads):
		# 	t = threading.Thread(target=worker)
		# 	t.setDaemon(True)
		# 	t.start()

		# for item in phish_items:
		# 	q.put(item)

		# q.join()

	except Exception as e:
		logger.warning(e)

def start(argv):


def ioc_downloader(db):
	try:
		logger.info("Launching IOC downloader...")
		count = 0
		url = 'https://openphish.com/feed.txt'
		res = requests.get(url, timeout=10, stream=True, headers=headers)
		with open('feed.txt', "wb") as file:
			file.write(res.content)
		urls = open('feed.txt', 'rb')
		for result in urls:
			hash_url = hashlib.md5(result).hexdigest()
			if db.phishing.find({"url_hash": hash_url}).count() == 0:
				count += 1
				CurrentTimestamp = int(time.time())
				db.phishing.insert({"timestamp": CurrentTimestamp, "url_hash": hash_url, "url": result, "kit_checked": "false"})
		logger.info('%s new url(s) put in database', count)

	except Exception as e:
		logger.warning(e)

if __name__ == '__main__':

	# Connect to DB
	try:
		mongohost = read_config('host', 'mongodb')
		mongoport = read_config('port', 'mongodb')
		dbname = read_config('database', 'mongodb')

		connection = pymongo.MongoClient(mongohost, int(mongoport), serverSelectionTimeoutMS=1)
		connection.server_info()
		db = connection[dbname]
		logger.info('Connected to MongoDB')
	except pymongo.errors.ServerSelectionTimeoutError as e:
		logger.warning("Mongod is not started. Tape \"sudo mongod --fork --logpath /var/log/mongodb.log\" in a terminal")
		if not os.path.exists("/data/db"):
			os.makedirs("/data/db")
			logger.info('database created')
		logger.warning("Error %s", e)
		sys.exit()

	ioc_downloader(db)
	phishing(db)
