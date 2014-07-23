#!/usr/bin/python2
#coding:utf8

def url_js_rewrite(link):
	return link.split("=")[1].strip("\"")

def url_rewrite(link):
	"""Rewrite a link according rules and return a link

	Keyword arguments:
	link -- string

	Return values:
	link -- string
	"""
	rules = {'javascript:location.href':'url_js_rewrite'}
	for r in rules:
		if r in link:
			link = globals()[rules[r]](link)
			break
	return link

