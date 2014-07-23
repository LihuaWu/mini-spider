#!/usr/bin/python2
#coding:utf8

import logging
import logging.config
import sys

read_config_file = lambda x : logging.config.fileConfig(x)

dummy = lambda x:None

is_logging = False
logger = None
log_levels = ['info', 'error', 'warning', 'debug', 'critical']

for lvl in log_levels: 
	setattr(sys.modules[__name__], lvl, dummy) 

def install(log_name):
	is_logging = True
	logger = logging.getLogger(log_name)
	for lvl in log_levels: 
		setattr(sys.modules[__name__], lvl, getattr(logger, lvl)) 

def uninstall():
	for lvl in log_levels: 
		setattr(sys.modules[__name__], lvl, dummy) 
