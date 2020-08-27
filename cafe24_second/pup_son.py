#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
		- 애견용품 카테고리만 수집함. ( http://pup-son.com/product/list.html?cate_no=24 )

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
		
		
		self.SITE_HOME = 'http://pup-son.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#-category > div > ul > li > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#-contents > div > div.xans-element-.xans-product.xans-product-normalpaging.-paging-package > p > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

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
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = 'div'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = '-image'
		
		
		# 물품 SOLDOUT CSS selector 정의
		# 
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = '-icons'
		
		
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	def web_get_category_data_second(self, html):
		rtn = False
		
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)
		
		__LOG__.Trace('web category : %d' % len(category_link_list) )
		if( len(category_link_list) == 0) : __LOG__.Trace( html )
		
		for category_ctx in category_link_list :
			try :
				category_name = category_ctx.get_text().strip()
	
				if(category_name == '애견용품') :
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(tmp_category_link.find('javascript') < 0 ) :
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

							category_link = tmp_category_link
							
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')


							if( self.WEB_CATEGORY_NAME_HASH.get( category_link , -1) == -1) : 
								self.WEB_CATEGORY_NAME_HASH[category_name] = category_link
								if( config.__DEBUG__ ) :
									__LOG__.Trace('WEB 카테고리 %s : %s' % ( category_name, category_link ) )

								rtn = True


			except Exception as ex:
				__LOG__.Error(ex)
				pass

		if(config.__DEBUG__) : __LOG__.Trace( 'WEB 카테고리 수 : %d' % len(self.WEB_CATEGORY_NAME_HASH))
		
		return rtn
		
		
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

			###########################
			# 상품 이미지 확인
			#
			###########################
			self.set_product_image_fourth( product_data, product_ctx )

			# 품절여부 확인
			#
			self.set_product_soldout_first(product_data, product_ctx ) 
						

			###########################
			# 상품명/URL
			###########################
			
			crw_post_url = self.set_product_name_url_first( product_data, product_ctx , 'div', '-name')
			
			
			##############################
			# 가격
			# <div class="xans-element- xans-product xans-product-listitem -detail"><p rel="판매가" class=" xans-record-"><span class="title displaynone"><span style="font-size:12px;color:#008BCC;font-weight:bold;">판매가</span> :</span> <span class="-real"><span style="font-size:12px;color:#008BCC;font-weight:bold;">8,000원</span><span id="span_product_tax_type_text" style=""> </span></span></p>
			# <p rel="원산지" class=" xans-record-"><span class="title displaynone"><span style="font-size:12px;color:#555555;">원산지</span> :</span> <span class="-real"><span style="font-size:12px;color:#555555;">중국 yolan oem</span></span></p>
			# </div>
			##############################
			p_list = product_ctx.find_all('p')
			for p_ctx in p_list :
				if('rel' in p_ctx.attrs) :
					title_name = p_ctx.attrs['rel']
					split_list = p_ctx.get_text().strip().split(':')
					sub_split_list = split_list[1].strip().split('(')
					value_str = sub_split_list[0].strip()
					if( 0 == title_name.find( '브랜드')) : product_data.crw_brand1 = value_str
					elif( 0 == title_name.find( '원산지')) : product_data.crw_brand2 = value_str
					elif( 0 == title_name.find( '소비자가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif( 0 == title_name.find( '판매가')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ))
			
			
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
			
			'''
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : crw_brand.append( split_list[1].strip() )
			'''

			table_list = soup.select('#-contents > div > div.xans-element-.xans-product.xans-product-detail.-product-detail-item.-box > ul > li.-right > div > table')
			
			#rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'td', 'td')
			rtn_dict = self.get_value_in_table(table_list, '기본 정보', 'td', 'td', 1)
			if(rtn_dict.get('BRAND' , -1) != -1) : crw_brand.append( rtn_dict['BRAND'] )
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			if(rtn_dict.get('Origin' , -1) != -1) : crw_brand.append( rtn_dict['Origin'] )

			
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
	
	
	
	