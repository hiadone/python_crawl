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

		
		self.SITE_HOME = 'http://youareapeach.co.kr/index_main.html'
		
		self.ORG_SITE_HOME = 'http://youareapeach.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''

		self.C_CATEGORY_VALUE = '#header > div > div > div > div > div.frame > div > div > ul > li > a'

		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#focusebox > ul > li > div > p > a'
		self.C_PRODUCT_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.ORG_SITE_HOME
		self.BASIC_PAGE_URL = self.ORG_SITE_HOME + '/product/list.html'
		self.BASIC_PRODUCT_URL = self.ORG_SITE_HOME
		self.BASIC_IMAGE_URL = self.ORG_SITE_HOME
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = 'a'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'prdImg'
		
		
		# 물품 SOLDOUT CSS selector 정의
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'promotion'
	
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
			self.set_product_category_third(product_data, soup)


			# 상품 이미지 확인
			# <a href="/product/detail.html?product_no=417&amp;cate_no=29&amp;display_group=1" name="anchorBoxName_417"><img src="//www.wefam.co.kr/web/product/medium/201704/417_shop1_670038.jpg?cmd=thumb&amp;width=300&amp;height=300" data-original="//www.wefam.co.kr/web/product/medium/201704/417_shop1_670038.jpg?cmd=thumb&amp;width=300&amp;height=300" id="eListPrdImage417_1" alt="" class="thumb" style="display: inline; opacity: 1;"></a>
			###########################
			
			self.set_product_image_first( product_data, product_ctx )
									
			
		
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 

			###########################
			# 상품명/URL
			###########################
			crw_post_url = self.set_product_name_url_second( product_data, product_ctx , 'strong', 'name')
			if(crw_post_url == '') : crw_post_url = self.set_product_name_url_second( product_data, product_ctx , 'p', 'name')
			
			##############################
			# 가격
			#

			##############################
			p_list = product_ctx.find_all('p')

			for p_ctx in p_list :
				if('class' in p_ctx.attrs) :
					class_name_list = p_ctx.attrs['class']
					value_str = p_ctx.get_text().strip()
					for class_name in class_name_list :
						if(class_name.strip() == 'custom') : 
							product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
							break
					
			p_list = product_ctx.find_all('strong', class_='price')
			for p_ctx in p_list :
					value_str = p_ctx.get_text().strip()
					if( product_data.crw_price_sale == 0 ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ))


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
			
			crw_brand = []
			
			'''
			#
			# <meta name="keywords" content="[상품검색어],[브랜드],[트렌드],[제조사]">
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : crw_brand.append( split_list[1].strip() )
			

			table_list = soup.select('#contents > div > div.xans-element-.xans-product.xans-product-detail > div.detailArea > div.infoArea > div.xans-element-.xans-product.xans-product-detaildesign > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('Product' , -1) != -1) : crw_brand.append( rtn_dict['Product'] )
			if(rtn_dict.get('Origin' , -1) != -1) : crw_brand.append( rtn_dict['Origin'] )
			'''
			
			self.set_detail_brand( product_data, crw_brand )

			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDetail > div.cont', '' )

			

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()

	