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
		
		self.SITE_HOME = 'http://www.naturalex.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#t_cate > a'
		self.C_CATEGORY_IGNORE_STR = []	
		self.C_CATEGORY_STRIP_STR = '..'

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''

		self.C_PAGE_VALUE = 'body > table > tr > td > table > tr > td.outline_side > div.indiv > form > table > tr > td > a'
		self.C_PAGE_STRIP_STR = './'
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		
		self.C_PRODUCT_VALUE = 'body > table > tr > td > table > tr > td.outline_side > div.indiv > form > table > tr > td > table > tr > td'
		self.C_PRODUCT_STRIP_STR = '..'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '?page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME + '/shop'
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		
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
			
			crw_post_url = ''
			
			####################################
			# 상품 카테고리 추출
			####################################
			category_list = soup.select('body > table > tr > td > table > tr > td.outline_side > div.indiv > form > table> tr > td > b > a')
			for category_ctx in category_list :
				crw_category = category_ctx.get_text().strip()
				break

		
			# 유효한 카테고리 체크
			if( self.check_ignore_category_text(crw_category) ) :
			
				product_data = ProductData()
				product_data.crw_category1 = crw_category
				
				
				####################################				
				# 상품 이미지 확인
				####################################

				img_ctx = product_ctx.find('img')
				if( img_ctx != None) :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()				
						
					if( img_src != '' ) :
						tmp_img_link = self.BASIC_IMAGE_URL + '/shop' + img_src
						img_link = tmp_img_link.replace('..','')
						product_data.product_img = self.get_hangul_url_convert( img_link )
						
						
				####################################
				# 품절여부 추출
				# <img src="/shop/data/skin/freemart/img/icon/good_icon_soldout.gif">
				####################################
				
				img_list = product_ctx.find('img')
				for img_ctx in img_list :
					img_src = ''
					if('src' in img_ctx.attrs ) : 
						img_src = img_ctx.attrs['src'].strip()
						if(0 <= img_src.find('soldout') ) : product_data.crw_is_soldout = 1
						
						
				
				####################################
				# 상품 링크 정보 및 상품명 / 상품코드
				####################################
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				is_product_name = True
				is_product_link = True
				
				product_link_list = product_ctx.find_all('a')
				for product_link_ctx in product_link_list :
					product_name = product_link_ctx.get_text().strip()
					
					# 첫번때 A link에 있는 Text
					if( is_product_name ) and ( product_name != '')  : 
						product_data.crw_name = product_name
						is_product_name = False
						
					if(is_product_link ) :
						if('href' in product_link_ctx.attrs ) : 	
							tmp_product_link = product_link_ctx.attrs['href'].strip()
							if( tmp_product_link.find('javascript') < 0) :
								if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
								crw_post_url = tmp_product_link

								if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

								split_list = crw_post_url.split('?goodsno=')
								sub_split_list = split_list[1].strip().split('&')
								product_data.crw_goods_code = sub_split_list[0].strip()
								is_product_link = False
					
						
				####################################
				# 가격
				####################################	
				div_list = product_ctx.find_all('div')
				for div_ctx in div_list :
					cost_ctx = div_ctx.find('b')
					if( cost_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( cost_ctx.get_text().strip() ) )

		
				
				
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
		
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	
	def get_product_detail_data(self, product_data, html):
		'''
		#
		#
		'''
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			table_list = soup.select('#goods_spec > form > table')
			
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			if( '브랜드' in  rtn_dict) : crw_brand.append(rtn_dict['브랜드'])
			elif( '제조사' in  rtn_dict) : crw_brand.append(rtn_dict['제조사'])
			
			self.set_detail_brand( product_data, crw_brand )

				
			# 제품 상세 설명 부분의 텍스트 및 이미지
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#contents > table > tr > td', 'p', 'src' )
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	