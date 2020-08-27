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
from cafe24.Cafe24 import Cafe24


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(Cafe24) :    

	def __init__(self) :
	
		Cafe24.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'http://bridge.dog'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#top_category > div.inner2 > div > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#with_100 > div.xans-element-.xans-product.xans-product-normalpaging > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#with_100 > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > div > div.description.item_list > p > a'
		#self.C_PRODUCT_VALUE = '#with_100 > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > div'
		self.C_PRODUCT_VALUE = '#with_100 > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = '#with_100 > div.xans-element-.xans-product.xans-product-normalpaging > p > a'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME + '/product/list.html'
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = 'div'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'thumbnail'
		
		
		# 물품 SOLDOUT CSS selector 정의
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'pro_icon'
		
	
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	
	def process_category_list(self):
		self.process_category_list_second()
		
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
			
			
			
			# 상품 카테고리
			#
			#self.set_product_category_first(product_data, soup)
			self.set_product_category_second(page_url, product_data, soup)

			# 상품 이미지 확인
			self.set_product_image_fourth(product_data, product_ctx )
			
		
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 

			
			name_div_list = product_ctx.find_all('div')

			for name_div_ctx in name_div_list :
				class_name_list = name_div_ctx.attrs['class']
				if(class_name_list[0] == 'description' ) :
					#
					# 상품 링크 정보 및 상품명 / 상품코드
					#
					name_strong_list = name_div_ctx.find_all('p', class_='name')
					if(len(name_strong_list) == 0 ) : name_strong_list = name_div_ctx.find_all('strong', class_='name')
					
					for name_strong_ctx in name_strong_list :
						product_link_list = name_strong_ctx.find_all('a')
						for product_link_ctx in product_link_list :
		
							if('href' in product_link_ctx.attrs ) : 
								span_list = product_link_ctx.find_all('span')
								for span_ctx in span_list :
									name_value = span_ctx.get_text().strip()
									
									if(0 != name_value.find('상품명') ) and (0 != name_value.find(':') ) : product_data.crw_name = name_value
									
								tmp_product_link = product_link_ctx.attrs['href'].strip()
								if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
								crw_post_url = tmp_product_link

								if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
								
								split_list = crw_post_url.split('?product_no=')
								crw_goods_code_list = split_list[1].strip().split('&')
								product_data.crw_goods_code = crw_goods_code_list[0].strip()

				
					#
					# 가격
					#
					li_list = name_div_ctx.find_all('li', class_='price_all')
					for li_ctx in li_list :
						if(config.__DEBUG__) : __LOG__.Trace('가격 체크')
						span_list = li_ctx.find_all('span')
						for span_ctx in span_list :
							class_name_list = span_ctx.attrs['class']
							
							#
							# 구분되는 물품이 없음..
							#if(class_name_list[0] == 'strike' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
							#elif(class_name_list[0] == 'pri' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
							if(class_name_list[0] == 'pri' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
					

			
			if( crw_post_url != '' ) :
				self.set_product_url_hash( product_data, crw_post_url) 
				rtn = True


		except Exception as ex:
			__LOG__.Error('에러 : set_product_data')
			__LOG__.Error(ex)
			pass
			
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

			soup = bs4.BeautifulSoup(html, 'lxml')
			
			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#contents > div.xans-element-.xans-product.xans-product-detail > div.cont.center', '' )

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()

	
	