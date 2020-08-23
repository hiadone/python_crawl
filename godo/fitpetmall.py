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
from godo.GodoMall import GodoMall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(GodoMall) :    

	def __init__(self) :
	
		GodoMall.__init__(self)
		
		
		self.SITE_HOME = 'https://www.fitpetmall.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		self.DETAIL_CATEGORY_ACTION = True
		self.C_DETAIL_CATEGORY_VALUE = '#contents > div > div > div.goods_list_item > div.list_item_category > ul > li > a'
		self.BASIC_DETAIL_CATEGORY_URL = self.SITE_HOME + '/goods/goods_list.php'
		self.C_DETAIL_CATEGORY_STRIP_STR = '..'
		
		
		
		self.C_CATEGORY_VALUE = '#header > div.PJ_head_3 > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['핏펫박스 문진 시작']
		self.C_CATEGORY_STRIP_STR = '..'

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#contents > div > div > div.goods_list_item > div.pagination > div > ul > li > a'
		self.C_PAGE_STRIP_STR = './'
		
		self.C_PAGE_IGNORE_STR = ['1','맨뒤','다음']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#contents > div > div > div.goods_list_item > div.goods_list > div > div > ul > li > div > div.PJ_good_table > div > div.item_tit_box > a'
		self.C_PRODUCT_VALUE = '#contents > div > div > div.goods_list_item > div.goods_list > div > div > ul > li > div'
		
		# 100원 이벤트 페이지의 물품리스트
		self.C_PRODUCT_VALUE_2 = '#banner_01 > div > div > div.goods_list_cont.goods_content_23 > div > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = '..'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#contents > div > div > div.goods_list_item > div.pagination > div > ul > li.btn_page.btn_page_last > a'
		
		self.PAGE_SPLIT_STR = '?page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
			
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME + '/goods/'
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		'''
		# 고도몰 추가 설정 부분
		'''
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = False

		self.SET_PRODUCT_DATA_CATEGORY_DIV_SELECTOR = 'div'
		
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_NAME = 'goods_list_item_tit'
		
		self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR = ''
		
		
		
		self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR = '#frmView > div > div > div.item_detail_list > dl'
		

		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#detail > div.detail_cont > div > div.txt-manual'
		
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = 'p'
	
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	
	