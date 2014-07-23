#!/usr/bin/python2
#coding:utf8

import unittest

import minispider.utils as mu

class TestUtils(unittest.TestCase):
	
	def setup(self):
		pass

	def test_extract_urls(self):
		url = "http://news.sina.com.cn/"
		html = open("sina_news").read()

		flag = True
		for i in mu.extract_urls(url, html):
			if "http" not in i:
				flag = False
				break
			elif len(i) < 10:
				flag = False
				break	
		self.assertTrue(flag)


if __name__ == '__main__':
	unittest.main()
