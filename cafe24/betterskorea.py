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

		self.SITE_HOME = 'http://www.betterskorea.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#-category > div > ul > li > div > ul > div.-category-all.gnb-category > div > ul > li.-categorylist-cover.xans-record- > a'
		
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#-contents > div > div.xans-element-.xans-product.xans-product-normalpaging.-paging-package > p > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1','다음','맨뒤']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		
		#-contents > div > div.xans-element-.xans-product.xans-product-normalpackage.-prodlist-package.-prodlist-list > div.xans-element-.xans-product.xans-product-listnormal.-prodlist.-prod4 > ul > li
		self.C_PRODUCT_VALUE = '#-contents > div > div.xans-element-.xans-product.xans-product-normalpackage.-prodlist-package.-prodlist-list > div.xans-element-.xans-product.xans-product-listnormal.-prodlist.-prod4 > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''

		self.C_LAST_PAGE_VALUE = '#-contents > div > div.xans-element-.xans-product.xans-product-normalpaging.-paging-package > a'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME + '/product/list.html'
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		# betterskorea 에서만 사용하는 CAFE24 API KEY 추가한 부분
		self.CAFE24_AP_KEY = 'iJf0852OYiGZTznb7gXaEG'
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = ''
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = ''
		
		
		# 물품 SOLDOUT CSS selector 정의
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = '-icons'
		
		
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
			self.set_product_category_second(page_url, product_data, soup)
			#self.set_product_category_third(product_data, soup)

			# 상품 이미지 확인
			img_link_list = product_ctx.find_all('a')
			for img_link_ctx in img_link_list :
				if('name' in img_link_ctx.attrs) :
					if(0 <= img_link_ctx.attrs['name'].find('anchorBoxName')) :
						img_ctx = img_link_ctx.find('img')
						if( img_ctx != None) : 
							if('src' in img_ctx.attrs ) :
								img_src = img_ctx.attrs['src'].strip()
								if( img_src != '' ) :
									img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
									if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )
		
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 

			name_div_list = product_ctx.find_all('div', class_='-name')
			
			for name_div_ctx in name_div_list :
				product_link_ctx = name_div_ctx.find('a')
				span_list = name_div_ctx.find_all('span', class_='-real')
				for span_ctx in span_list :
					name_value = span_ctx.get_text().strip()
					if(0 != name_value.find('상품명') ) and (0 != name_value.find(':') ) : product_data.crw_name = name_value
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#

				if(product_link_ctx != None) :
					if('href' in product_link_ctx.attrs ) : 
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
						split_list = crw_post_url.split('?product_no=')
						crw_goods_code_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = crw_goods_code_list[0].strip()
						
				
			p_list = product_ctx.find_all('p')
			for p_ctx in p_list :
				if('rel' in p_ctx.attrs) :
					title_name =  p_ctx.attrs['rel']
					span_ctx = p_ctx.find('span', class_='-real')
					if(span_ctx != None) :
						price_ctx = span_ctx.find('span')
						if(price_ctx != None) : 
							if(title_name == '판매가') : product_data.crw_price = int( __UTIL__.get_only_digit( price_ctx.get_text().strip() ) )
							if(title_name == '할인판매가') : product_data.crw_price_sale = int( __UTIL__.get_only_digit( price_ctx.get_text().strip() ) )
							if(title_name == '[브랜드]') : product_data.crw_brand1 = price_ctx.get_text().strip()
			
			
			
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

			table_list = soup.select('#-contents > div.-size > div.xans-element-.xans-product.xans-product-detail.-product-detail-item.-box > ul > li.-right > div > table')			
			rtn_dict = self.get_value_in_table(table_list, '', 'th', 'td', 0)
			if(rtn_dict.get('브랜드' , -1) != -1) :
				product_data.d_crw_brand1 = rtn_dict['브랜드']
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
		

	def get_product_detail_data_second(self, product_data, cafe24_data):
		rtn = False
		try :
			detail_page_txt = []
			detail_page_img = []

			detail_page_img = self.get_image_data_innerhtml(cafe24_data.description)
			
			detail_page_txt = self.get_text_data_innerhtml(cafe24_data.description)
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	'''
	#
	# Mall.py 파일의 함수를 Overwrite 한 함수들
	# Cafe24 api 를 사용하여 제품내용을 갖고 옴.
	#
	# product_url = http://www.betterskorea.com/product/detail.html?product_no=5359&cate_no=883&display_group=1
	'''
	def process_product_detail(self, product_url, product_data):
	
		rtn = False
		resptext = ''
		
		try :
			__LOG__.Trace('------------------------------------------------')
			if( config.__DEBUG__ ) : __LOG__.Trace('product : %s' % ( product_url ) )

			time.sleep(self.WAIT_TIME)
			
			URL = product_url
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header , verify=False) 
			if(self.EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 인코딩
			
			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_product_detail_data( product_data, resptext )
				
				# 상세페이지를 API로 불러오는 부분
				self.process_product_detail_second(product_url, product_data)
				
				# API 작업
				self.process_product_detail_api(product_data)
				
		except Exception as ex:
			__LOG__.Error( "process_product_detail Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		self.PRODUCT_URL_HASH[product_url] = product_data
		
		return rtn
		
	def process_product_detail_second(self, product_url, product_data):
		
		rtn = False
		resptext = ''
		
		try :

			if( config.__DEBUG__ ) : __LOG__.Trace('product : %s' % ( product_url ) )
			
			split_list = product_url.split('product_no=')
			product_id_list = split_list[1].split('&')
			product_id = product_id_list[0]
			
			cafe24_data = self.send_cafe24_api_products_v2(self.CAFE24_AP_KEY, self.SITE_HOME, product_id, product_url , self.COOKIE_STR, self.USER_AGENT )
			if(cafe24_data != None) : 
				rtn = self.get_product_detail_data_second( product_data, cafe24_data )
			
		except Exception as ex:
			__LOG__.Error( "process_product_detail_second Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		
		return rtn
		
		
		

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	