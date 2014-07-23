#!/usr/bin/python2
#coding:utf8

import re
import optparse

import gevent.queue
import pybloomfilter

import utils
import log
import seed

def parse_args():
	"""Read and parse options from command line
	Initialize logging

	Return values:
	options: options and arguments parsed from command line
	confs: configuration file dictionary information
	"""
	usage = """usage: %prog [options]
To crawl pages from web in terms of special URL patterns."""

	parser = optparse.OptionParser(usage = usage, version = '%prog 1.0.0.0')	
	parser.add_option('-c', dest = 'filename',
						help = 'read config file', metavar = 'FILE')

	parser.add_option('-l', '--log', dest = 'log', action = 'store_true',
						help = 'start logging', default = False)

	options, args = parser.parse_args()
	if options.filename is None:
		print parser.format_help()
		parser.exit()
	else:
		confs = utils.parse_config_file(options.filename)
		if options.log:
			log.read_config_file(confs['log']['log_config_file'])
			log.install(confs['log']['log_name'])
		else:
			log.uninstall()	

		return options, confs


def main():
	_, confs = parse_args()

	#load spider.conf
	crawl_timeout = float(confs['spider']['crawl_timeout'])
	crawl_interval = float(confs['spider']['crawl_interval'])
	max_depth = int(confs['spider']['max_depth'])
	target_url = confs['spider']['target_url']
	store_page_dir = confs['spider']['store_page_dir']
	bf_file = confs["BloomFilter"]['bf_file']
	thread_num = int(confs['spider']['thread_count'])

	#bloom filter
	bf = pybloomfilter.BloomFilter(100000, 0.0001, bf_file)

	#initialize task queue from input seeds
	tasks = gevent.queue.Queue()
	for line in utils.read_file(confs['spider']['url_list_file']):
		line = line.strip()
		#logger.info('queue in url:%s' %line)
		log.info('queue in url:%s' %line)
		tasks.put_nowait(seed.Seed(0, line))

	#work thread function
	def worker(n):
		while not tasks.empty():
			depth, url = tasks.get()
			if depth > max_depth:
				log.info("worker%s url:%s exceed max depth %s." %(n, url, max_depth))
				continue
			if url in bf:
				log.info('worker%s url:%s already accessed' %(n, url))
			else:
				bf.add(url)
				log.info('worker%s fetching url:%s' %(n, url))
				url_list = utils.save_and_fetch(url, re.compile(target_url),
										store_page_dir,crawl_timeout)
				for u in url_list:
					tasks.put_nowait(seed.Seed(depth + 1, u))
					log.info('queue in url:%s' %u)
				gevent.sleep(crawl_interval)
		log.info('worker%s quit.' %n)

	#start work thread
	threads = [gevent.spawn(worker, i) for i in range(thread_num)]

	#wait all work threads quit elegantly. :)
	gevent.joinall(threads) 

if __name__ == '__main__':
	main()
	pass
