#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- 카테고리 없음
	- 품절여부 확인을 할수 없음

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


		self.SITE_HOME = 'http://m.louisdogboutique.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#self.C_CATEGORY_VALUE = '#cate_copy > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		#self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.paginate.typeList > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#m02 > li > div > ul > li'
		#self.C_PRODUCT_VALUE = '#contents > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product.typeThumb > ul > li'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''

		self.C_LAST_PAGE_VALUE = ''
		
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
		# <div class="icon"><img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/ico_product_soldout.gif" class="icon_img" alt="품절"> <img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/ico_product_recommended.gif" class="icon_img" alt="추천">  </div>
		#
		self.C_PRODUCT_SOLDOUT_SELECTOR = ''
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = ''
		
		
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	def process_category_list(self):
		return True
	
	def process_page_list(self):

		__LOG__.Trace("********** process_page_list ***********")
		
		rtn = False
		resptext = ''
		
		self.PAGE_URL_HASH = None
		self.PAGE_URL_HASH = {}
		self.PAGE_URL_HASH[self.SITE_HOME] = ''

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
			
			# 상품 카테고리
			#


			###########################
			# 상품 이미지 확인
			#
			###########################
			self.set_product_image_third( product_data, product_ctx )

			# 품절여부 확인
			#self.set_product_soldout_first(product_data, product_ctx ) 

			###########################
			# 상품명/URL
			###########################
			
			crw_post_url = self.set_product_name_url_fourth( product_data, product_ctx , 'strong', 'name')
			if(crw_post_url == '') : crw_post_url = self.set_product_name_url_fourth( product_data, product_ctx , 'p', 'name')
			
			##############################
			# 가격
			# <ul class="spec">
			# <li class="displaynone custom" style="text-decoration:line-through; font-size:11px;">원</li>      
			# <li class="price  ">84,000원 <span class="displaynone"></span>
			# </li>
			# <li class="price sale displaynone"></li>
			# <li class="icon"></li>
			# <li class="cart"></li>
			# <li class="color displaynone">
			# </li>
			# <li class="likeButton displaynone"><button type="button"><strong></strong></button></li>
			# </ul>
			##############################
			#self.set_product_price_brand_first(product_data, product_ctx)
			li_ctx_list = product_ctx.find_all('li', class_='price')
			for li_ctx in li_ctx_list :
				is_sale_price=False
				class_name_list = li_ctx.attrs['class']
				for class_name in class_name_list :
					if(class_name == 'sale') : is_sale_price = True
				
				split_list = li_ctx.get_text().split('(')
				price_value = int( __UTIL__.get_only_digit( split_list[0].strip() ) ) 
				
				if(is_sale_price ) : product_data.crw_price_sale = price_value
				else : product_data.crw_price = price_value

			
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
			####################################
			# 상품 기본 정보에서 브랜드 등을 추출
			####################################
		
			crw_brand = []
			
			
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : crw_brand.append( split_list[1].strip() )
			

			table_list = soup.select('#contents > div:nth-child(1) > div.prdInfo > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			
			
			self.set_detail_brand( product_data, crw_brand )
			
			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDetail', '' )
			
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	