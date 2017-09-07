# -*- coding:utf-8 -*-

import os
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bz2 import BZ2File as b2f
import logging
import logging.config

#配置日志
logging.config.fileConfig('log.conf')
file_log = logging.getLogger('wj')



class Wiki2Mongo(object):

	def __init__(self, mongo = None):
		self.col = mongo

	def wiki2mongo(self, path):
		"""
		遍历指定文件夹，找到.bz2文件逐个导入mongodb
		:param path: 存放维基的dump文件的目录
		:return: 
		"""
		for filename in os.listdir(path):
			if '.bz2' in filename:
				filepath = u'I:\维基\enwiki\enwiki-20170901-pages-articles\\'+filename
				self.parse(filepath)

	def parse(self, filepath):
		"""
		:param filepath: 单个.bz2文件的路径
		:return: 
		"""

		fp = b2f(filepath)
		file_log.info('开始解析文件：%s ' % filepath.encode('utf-8'))

		tree = ET.parse(fp)
		root = tree.getroot()
		ns = {'default': 'http://www.mediawiki.org/xml/export-0.10/'}

		# 遍历page标签，插入MongoDB，xml格式参照http://www.mediawiki.org/xml/export-0.10/
		for iterpage in tree.iter('{http://www.mediawiki.org/xml/export-0.10/}page'):
			doc = {'revision':{'contributor':{}}}
			doc['title'] = iterpage.findtext('./default:title', None, ns)
			doc['ns'] = iterpage.findtext('./default:ns', None, ns)
			doc['id'] = iterpage.findtext('./default:id', None, ns)
			try:
				doc['redirect'] = iterpage.find('./default:redirect', ns).atrrib
			except AttributeError:
				pass
			doc['revision']['id'] = iterpage.findtext('./default:revision/default:id', None, ns)
			doc['revision']['parentid'] = \
				iterpage.findtext('./default:revision/default:parentid', None, ns)
			doc['revision']['timestamp'] = \
				iterpage.findtext('./default:revision/default:timestamp', None, ns)
			doc['revision']['contributor']['username'] = \
				iterpage.findtext('./default:revision/default:contributor/default:username', None, ns)
			doc['revision']['contributor']['id'] = \
				iterpage.findtext('./default:revision/default:contributor/default:id', None, ns)
			doc['revision']['comment'] = \
				iterpage.findtext('./default:revision/default:comment', None, ns)
			doc['revision']['model'] = iterpage.findtext('./default:revision/default:model', None, ns)
			doc['revision']['format'] = iterpage.findtext('./default:revision/default:format', None, ns)
			doc['revision']['text'] = iterpage.findtext('./default:revision/default:text', None, ns)

			for t in range(5):
				try:
					self.col.insert(doc)
				except DuplicateKeyError:
					break
				except ConnectionFailure:
					if t == 4:
						logging.error('Disconnect! Insert page %s failed' % doc['id'])
					else:
						pass
				else:
					if int(doc['id']) % 1000 == 0:
						logging.info('insert page %s' % doc['id'])
					break
		file_log.info('解析文件：%s 成功' % filepath.encode('utf-8'))

if __name__ == "__main__":
	mongo = MongoClient('127.0.0.1:27017')['db']['cl']
	# wiki2mongo(file, mongo)
	w2m = Wiki2Mongo(mongo)
	w2m.wiki2mongo(u'I:\维基\enwiki\enwiki-20170901-pages-articles\enwiki-20170901-pages-articles1.xml-p10p30302')