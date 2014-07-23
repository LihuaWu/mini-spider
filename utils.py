#!/usr/bin/python2
#coding:utf8

import ConfigParser
import urlparse
import urllib2
import urllib
import zlib
import functools
import os.path

import gevent
import gevent.queue
import pyquery
import lxml

import rewrite
import log

def parse_config_file(filename): 
	"""Read configuration file and return as a dict

	Keyword arguments:
	filename -- configuration filename
	"""
	config = ConfigParser.ConfigParser()
	config.read(filename)
	confs = {}

	for s in config.sections():
		conf = config.items(s,True)
		confs[s] = dict(conf)
	return confs


def read_file(filename):
	"""Read content from file and return a generator
	
	Keyword arguments:
	filename -- file's name

	Return values:
	line generator
	"""
	try:
		f = open(filename)
		while True:
			line = f.readline()
			if not line:
				break
			else:
				yield line
	finally:
		f.close()	


def get_url_response(url, header_dict = {}, post_dict = {},
	timeout = 0, use_gzip = False):
	"""
	get url request response info according to url

	Keyword arguments:
	url: URL to fetch
	header_dict: prepare header info for request 
	post_dict: prepare post data info for request
	timeout: timeout seconds limit to fetch url 
	use_gzip: use gzip to compress data for request

	Return values:
	file like object
	"""
	url = str(url)
	#load post data
	if len(post_dict) > 0:
		post_data = urllib.urlencode(post_dict)
		req = urllib2.Request(url, post_data)
		req.add_header('Content-Type', 'application/x-www-form-urlencoded')
	else:
		req = urllib2.Request(url)
	#load header data
	if len(header_dict) > 0:
		for k, v in header_dict.iteritems():
			req.add_header(k, v)
	default_header_dict = {
		'User-Agent' :'Mozilla/5.0',
		'Cache-Control' : 'no-cache',
		'Accept' : '*/*',
		'Connection' : 'Keep-Alive'}
	for k, v in default_header_dict.iteritems():
		req.add_header(k, v)

	#add gzip support
	if use_gzip:
		req.add_header('Accept-Encoding', 'gzip, deflate');

	if timeout > 0:
		response = urllib2.urlopen(req, timeout = timeout)
	else:
		response = urllib2.urlopen(req)
	return response


def get_html(url, header_dict = {}, post_dict = {},
			timeout = 0, use_gzip = False):
	"""
	fetch html page according to url

	Keyword arguments:
	url: URL to fetch
	header_dict: prepare header info for request 
	post_dict: prepare post data info for request
	timeout: timeout seconds limit to fetch url 
	use_gzip: use gzip to compress data for request

	Return values:
	html string
	"""
	response = get_url_response(url, header_dict, post_dict, timeout, use_gzip)

	html = response.read()

	resp_info = response.info()

	response.close()

	#gzip support
	if ("Content-Encoding" in resp_info and 
		resp_info['Content-Encoding'] == 'gzip'):
		html = zlib.decompress(html, 16 + zlib.MAX_WBITS) 
	return html


def save_and_fetch(url, pattern, path, timeout):
	"""
	download html page in terms of url.	
	save html with specific url pattern into file with url as file name.
	extract urls from the html page and return a generator.
	
	Keyword arguments:
	url: URL
	pattern: compiled url regular expression pattern
	timeout: timeout seconds to fetch html page
	
	Return values:
	url generator
	"""
	try:
		html = get_html(url, timeout = timeout)
	except urllib2.URLError as e:
		log.error("%s:%s" %(url, e.message))
		return
	except urllib2.HTTPError as e:
		log.error("%s:%s" %(url, e.message))
		return

	if pattern.match(url):
		filename = "%s%s" %(path, urllib.quote_plus(url))
		log.info('url: %s match target_url. store in file:%s.'
						%(url, filename))
		write_file(os.path.abspath(filename), html)

	for u in extract_urls(url, html):
		yield u


def write_file(filename, content):
	"""Write content into file
	Keyword arguments:
	filename  file's name
	content   content string to write to file
	""" 
	try:
		f = open(filename, 'w+') 
		f.write(content)
		f.close()
	except IOError as e:
		log.error(e.message)

def extract_urls(html):
	"""extract all link tags from html
	use filter strategies to filter tags which are not url

	Keyword arguments:
	html: html page content

	Return values:
	"""
	#search links
	d = pyquery.PyQuery(html)

	url_filter = ['javascript:;', '#jump']
	for i in d.find('a'):
		is_filtered = False
		for k, v in i.items():
			#filter by node key
			if k != "href":	
				continue
			#filter by node value
			for p in url_filter:
				if v.startswith(p):
					is_filtered = True
					break
			if is_filtered:
				continue
			yield v

if __name__ == '__main__':
	pass
