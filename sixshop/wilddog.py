#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 25.

@author: bobby.byun@netm.co.kr

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
from sixshop.SixShop import SixShop


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(SixShop) :    

	def __init__(self) :
	
		SixShop.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://www.wilddog.co.kr/shop'
		
		self.SITE_ORG_HOME = 'https://www.wilddog.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#displayCanvas > div > div > section > div > div > div.productListFilterCollection > div.productListFilterCollectionNavi > div.productListFilter-navi
		self.C_CATEGORY_VALUE = '#displayCanvas > div > div > section > div > div > div.productListFilterCollection > div.productListFilterCollectionNavi > div'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		'''
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'	# 페이지 selector 가 없어서 임의로 지정함
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		'''
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		
				
		self.C_PRODUCT_VALUE = '#displayCanvas > div > div > section.section > div > div > div > div > div'
		self.C_PRODUCT_STRIP_STR = ''
		
		'''
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부
		'''
		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		

		
	def get_category_data(self, html):
		self.get_category_data_default_sixshop(html)
	
		
		
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
