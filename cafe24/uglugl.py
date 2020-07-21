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
		
		
		self.SITE_HOME = 'http://uglugl.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		#self.C_CATEGORY_VALUE = '#categorymenu > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['친환경 스팀','친환경 제주','친환경 간식','친환경 용품']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#-common > div > div > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#-common > div > div > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > div > div.description > div.name > a'
		self.C_PRODUCT_VALUE = '#-common > div > div > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#-common > div > div > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
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
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'icon'
		
		
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	
	def process_category_list(self):
		self.process_sub_category_list()
		
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
			self.set_product_category_first(product_data, soup)

			
			# 상품 이미지 확인
			self.set_product_image_fourth( product_data, product_ctx )
			
		
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 

			
			name_div_list = product_ctx.find_all('div', class_='name')

			for name_div_ctx in name_div_list :
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
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

				
			self.set_product_price_brand_first(product_data, product_ctx )

			
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

			
			detail_page_txt = []
			detail_page_img = []

			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : product_data.d_crw_brand1 = split_list[1].strip()
			

			table_list = soup.select('#productinfo > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('브랜드' , -1) != -1) :
				product_data.d_crw_brand1 = rtn_dict['브랜드']
				
			# 제품 상세 부분
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#prdDetail > div.cont.productdetail', 'p', 'ec-data-src' )

			#__LOG__.Trace( detail_page_txt )
			#__LOG__.Trace( detail_page_img )
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	
	#app.set_cookie()
	#app.set_user_agent()
	#product_data = ProductData()
	#app.process_product_detail( 'http://uglugl.com/product/detail.html?product_no=148&cate_no=69&display_group=1', product_data)
	
	
	