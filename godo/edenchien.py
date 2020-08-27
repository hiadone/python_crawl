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
from godo.GodoMall import GodoMall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(GodoMall) :    

	def __init__(self) :
	
		GodoMall.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'http://www.edenchien.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#header > div.header_gnb > div.gnb > div.gnb_menu_box > ul > li > ul > li > a'
		self.C_CATEGORY_VALUE_2 = '#header > div.header_gnb > div.gnb > div.gnb_menu_box > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['에덴숑','주소','공지사항','Review','이벤트','구입금액별 선물','Q&A','교환 / 반품','위탁.사입.판매.문의', 'ABOUT', '모델견 신청', 'COMMUNITY' ]				# 
		self.C_CATEGORY_STRIP_STR = '..'

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''

		
		self.C_PAGE_VALUE = '#contents > div > div > div.goods_list_item > div.pagination > div > ul > li > a'
		self.C_PAGE_STRIP_STR = './'
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		#self.C_PRODUCT_VALUE = '#contents > div > div > div > div.goods_list > div > div > ul > li > div > div.item_info_cont > div.item_tit_box > a'
		self.C_PRODUCT_VALUE = '#contents > div > div > div.goods_list_item > div.goods_list > div > div > ul > li > div'
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
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = True

		self.SET_PRODUCT_DATA_CATEGORY_DIV_SELECTOR = 'div'
		
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_NAME = ''
		
		self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR = ''
		
		
		
		self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR = '#frmView > div > div > div.item_detail_list > dl'
		

		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#detail > div.detail_cont > div.txt-manual'
		
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = ''
	
	
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	