#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user
'''
import json
import time
import random
import os, datetime,re, signal
from datetime import date, timedelta

import bs4
import queue
import sys
import warnings
import requests
import datetime
from urllib import parse

import log as Log;  Log.Init()
from app import config
from app import define_mall as __DEFINE__
from util import Util as __UTIL__

from model.ProductData import ProductData
from imweb.ImWeb import ImWeb


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(ImWeb) :    

	def __init__(self) :
	
		ImWeb.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://hipaw.co.kr/apparel/'
		
		self.SITE_ORG_HOME = 'https://hipaw.co.kr'
		
		
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		
		#self.C_CATEGORY_VALUE = 'body > div > div > div > div.owl-stage-outer > div > div > div > div > div > div > div > h5 > span > a'
		self.C_CATEGORY_VALUE = 'body > div > main > div > div > div > div > div > div > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		self.C_PAGE_VALUE = 'body > div > main > div > div > div > div > div > div > nav > ul > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = 'body > div > main > div > div > div > div > div > div > div > div > div > div.shop-item._shop_item'
		
		self.C_PRODUCT_VALUE = 'body > div > main > div > div > div > div > div > div > div > div > div > div.shop-item._shop_item'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
	
	
		
	
		
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''	
	
	def get_category_value(self, product_data, page_url, soup ) :
		try :
			split_list = page_url.split('/')
			product_data.crw_category1 = split_list[3].strip()
		except :
			pass
			
		return True
		
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	