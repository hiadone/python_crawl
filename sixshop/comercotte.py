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
from sixshop.SixShop import SixShop


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(SixShop) :    

	def __init__(self) :
	
		SixShop.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://www.comercotte.com'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		self.C_CATEGORY_VALUE = '#siteHeader > div.row.row-main.desktop > div.column.header-center > nav > ul > li'
		#self.C_CATEGORY_VALUE = '#siteHeader > div.row.row-main.desktop > div.column.header-center > nav > ul > li > a'
		#self.C_CATEGORY_VALUE = '#siteHeader > div.row.row-main.desktop > div.column.header-center > nav > ul > li.menu-navi.menu-main.pageMenu.subMenu-exist > div.subMenuNaviListDiv > ul > li > a'
		#siteHeader > div.row.row-main.desktop > div.column.header-center > nav > ul > li > div.subMenuNaviListDiv > ul > li:nth-child(1) > a
		
		self.C_CATEGORY_IGNORE_STR = ['HOME','ABOUT','문의']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#contents > div > ol > li > a'			# 페이지 selector가 없어서 임의의 문자열 입력
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		
		
		#self.C_PRODUCT_VALUE = '#displayCanvas > div > div > section > div > div > div > div > div > a'
		self.C_PRODUCT_VALUE = '#displayCanvas > div > div > section > div > div > div > div > div'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
	'''
	######################################################################
	#
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''
	
	def get_category_data(self, html):
		rtn = False
		
		main_category_name = ''
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)


		for category_main_ctx in category_link_list :
			try :
				category_ctx = category_main_ctx.find('a', class_='menu-name')
				if(category_ctx != None) :
					if(self.check_ignore_category( category_ctx ) ) :
						if('href' in category_ctx.attrs ) : 
							tmp_category_link = category_ctx.attrs['href']
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )
							category_link = tmp_category_link
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
				
							main_category_name = category_ctx.get_text().strip()
							if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
								self.CATEGORY_URL_HASH[category_link] = main_category_name
								if( config.__DEBUG__ ) :
									__LOG__.Trace('%s : %s' % ( main_category_name, category_link ) )

								rtn = True
					
				ul_ctx = category_main_ctx.find('ul', class_='subMenuNaviList')
				if( ul_ctx != None) :
					a_link_list = ul_ctx.find_all('a', class_='menu-name')
					for sub_link_ctx in a_link_list :
						if('href' in sub_link_ctx.attrs ) : 
							tmp_category_link = sub_link_ctx.attrs['href']
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, sub_link_ctx.attrs['href'] )
							category_link = tmp_category_link
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
											
							sub_category_name = sub_link_ctx.get_text().strip()
							if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
								self.CATEGORY_URL_HASH[category_link] = '%s|%s' % ( main_category_name, sub_category_name )
								if( config.__DEBUG__ ) :
									__LOG__.Trace('%s|%s : %s' % ( main_category_name, sub_category_name , category_link ) )

			except Exception as ex:
				__LOG__.Error(ex)
				pass

		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
	
	def get_product_data(self, category_key, html):
		self.get_product_data_second_sixshop( category_key, html )
		
	def process_product(self, category_key):
		self.process_product_second_sixshop( category_key )
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	
	