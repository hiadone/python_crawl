#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항 
	- 상품 URL 이 상품리스트의 링크 정보에 onclick attrs안에 javascript로 숨겨져 있음.
	
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
from mall.Mall import Mall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)

		self.SITE_HOME = 'http://www.montraum.com/common/process/shopmain.asp?iniCategory=2&thisCategory=22'
		
		self.SITE_ORG_HOME = 'http://www.montraum.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		#self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		#self.C_CATEGORY_TYPE = ''
		
		#self.C_CATEGORY_VALUE = '#gnb > div > ul.gnb > li > a.gnbDep1'
		#self.C_CATEGORY_IGNORE_STR = ['듀먼 후기','이벤트/혜택','브랜드 스토리']
		#self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#page-item-list > div.items > div.pagination1.only-pc > span > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#page-item-list > div.items > div.item-list-type3 > div'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		
	'''
	#
	#
	#
	'''
	def process_page_list(self):

		__LOG__.Trace("********** process_page_list ***********")
		
		self.PAGE_URL_HASH = None
		self.PAGE_URL_HASH = {}
		self.PAGE_URL_HASH[self.SITE_HOME] = 'Mars'
		
		if(config.__DEBUG__) : __LOG__.Trace( '페이지 수 : %d' % len(self.PAGE_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return True
		
		
	def process_category_list(self ) :
		return True
		
	
	
		
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	def get_product_detail_data(self, product_data, html):
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []

			
			soup = bs4.BeautifulSoup(html, 'lxml')

			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#page-item-view > div.contents-wrapper.pc-width.item-detail > div > div.tab-content > div.content1', '', 'src' )
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	

	
	
	
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			product_data.crw_category1 = self.PAGE_URL_HASH[ page_url ]
	

			####################################
			# 브랜드 추출	
			####################################

			product_data.crw_brand1 = product_data.crw_category1

			
			####################################				
			# 상품 이미지 확인
			#
			# <img class="item-image" src="/_vir0001/product_img/P1449_20200421AM94623_2.jpg" alt="img1">
			####################################

			img_list = product_ctx.find_all('img', class_='item-image')
			for img_ctx in img_list :
				img_src = ''
				if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
				elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
					
				if( img_src != '' ) :
					img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
					product_data.product_img = self.get_hangul_url_convert( img_link )
			
			

			####################################
			# 상품 링크 정보 및 상품코드
			#
			# <div class="item" style="cursor:pointer" onclick="goHref(1449,'P1449_20200421AM94623_2.jpg')">
			####################################
			
			if('onclick' in product_ctx.attrs ) :
				onclick_str = product_ctx.attrs['onclick'].strip()
				split_data = onclick_str.split('goHref(')
				sub_split_data = split_data[1].split(',')
				product_data.crw_goods_code = sub_split_data[0].strip()
				crw_post_url = 'http://www.montraum.com/common/process/shopview.asp?thisCategory=22&pack_content_id=' + product_data.crw_goods_code
			
			
			####################################
			# 상품명 / 품절여부
			#
			# <p class="item-description" id="iconID1449" name="iconID1449">데일리관리 세트<br> (돈모 브러쉬+플러쉬 콤)</p>
			#
			# ---------- 품절시 -----------------------
			# <p class="item-description" id="iconID1095" name="iconID1095">트레이닝패드 L 120매 (30매 x 4개)<img src="/_vir0001/process/partImages/icon_soldout.gif" align="absmiddle">&nbsp;<img src="/_vir0001/process/partImages/icon_soldout.gif" align="absmiddle">&nbsp;<img src="/_vir0001/process/partImages/icon_soldout.gif" align="absmiddle">&nbsp;<img src="/_vir0001/process/partImages/icon_soldout.gif" align="absmiddle">&nbsp;</p>
			####################################
			name_div_list = product_ctx.find_all('p', class_='item-description')
			for name_div_ctx in name_div_list :
				product_data.crw_name = name_div_ctx.get_text().replace('\n',' ').strip()
				
				# 품절여부
				soldout_img_list = name_div_ctx.find_all('img')
				for soldout_img in soldout_img_list :
					if('src' in soldout_img.attrs ) :
						if( 0 <= soldout_img.attrs['src'].find('soldout') ) : product_data.crw_is_soldout = 1
	
	
			
			####################################
			# 가격
			#
			# <p class="item-price">
			# <span class="list-price" id="ori_count1449" name="ori_count1449">74,000</span> <span class="now-price" id="promotion_ID1449" name="promotion_ID1449">40,900</span>
			# </p>
			####################################
			
			div_list = product_ctx.find_all('p', class_='item-price')
			for div_ctx in div_list :
				span_list = div_ctx.find_all('span')
				for span_ctx in span_list :
					if('class' in span_ctx.attrs ) :
						class_name_list = span_ctx.attrs['class']

						if(class_name_list[0] == 'list-price' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'now-price' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
					
			
			if( crw_post_url != '' ) :
				if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
				
					self.set_product_data_sub( product_data, crw_post_url )

					#self.print_product_page_info( product_data ) 			
					self.process_product_api(product_data)
										
				rtn = True


		except Exception as ex:
			__LOG__.Error('에러 : set_product_data')
			__LOG__.Error(ex)
			pass
			
		return True	
		
	
	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()

	
	
	
	