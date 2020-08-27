#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	
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


		self.SITE_HOME = 'http://www.bowwowmill.com'
				
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#left_menu > li > a'
		self.C_CATEGORY_IGNORE_STR = ['login', 'join us ', 'my page',  'delivery', 'bookmark',  'bowwow_mill', '게시판',  '개인결제창', 'cs center',  'bank info', '주문시 필독사항' , '파티룸예약']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#sub_contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#sub_contents > div.xans-element-.xans-product.xans-product-listnormal.itemlist > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''

		self.C_LAST_PAGE_VALUE = '#sub_contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
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
		self.C_PRODUCT_IMG_SELECTOR = 'img'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'thumb'
		
		
		# 물품 SOLDOUT CSS selector 정의
		# 
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'prdicon'
		
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
		#if( len(category_link_list) == 0) : __LOG__.Trace( html )
		
		for category_ctx in category_link_list :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(tmp_category_link.find('javascript') < 0 ) :
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )
							
							#category_link = self.get_hangul_url_convert( tmp_category_link )
							category_link = tmp_category_link
							
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
							category_name = category_ctx.get_text().strip()
							if( self.WEB_CATEGORY_NAME_HASH.get( category_link , -1) == -1) : 
								self.WEB_CATEGORY_NAME_HASH[category_name] = category_link
								if( category_name == '케이크&머핀') : self.WEB_CATEGORY_NAME_HASH['케이크 & 머핀'] = category_link
								
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
			self.set_product_image_second( product_data, product_ctx )

			# 품절여부 확인
			#
			self.set_product_soldout_first(product_data, product_ctx ) 


			###########################
			# 상품명/URL
			###########################
			
			crw_post_url = self.set_product_name_url_fourth( product_data, product_ctx , 'p', 'name')
			if(crw_post_url == '') : crw_post_url = self.set_product_name_url_fourth( product_data, product_ctx , 'strong', 'name')
			
			##############################
			# 가격
			#
			##############################
			self.set_product_price_brand_second(product_data, product_ctx)

				
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
			
			table_list = soup.select('#sub_contents > div.xans-element-.xans-product.xans-product-detail > div > div.detailArea > div.infoArea > div.xans-element-.xans-product.xans-product-detaildesign > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('BRAND' , -1) != -1) : crw_brand.append( rtn_dict['BRAND'] )
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			if(rtn_dict.get('Origin' , -1) != -1) : crw_brand.append( rtn_dict['Origin'] )
			
			
			self.set_detail_brand( product_data, crw_brand )
			
			
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
	
	
	
	