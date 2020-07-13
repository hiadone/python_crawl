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
		
		self.SITE_HOME = 'http://mytrianon.co.kr/shop/goods/goods_list.php?&category=003'
		
		self.SITE_ORG_HOME = 'http://mytrianon.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#menuLayer > tbody > tr > td > div > a'
		self.C_CATEGORY_IGNORE_STR = []				# 
		self.C_CATEGORY_STRIP_STR = '..'

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''

		
		self.C_PAGE_VALUE = '#s_container > div > div.indiv > form > table > tr > td > a'
		self.C_PAGE_STRIP_STR = './'
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		
		self.C_PRODUCT_VALUE = '#s_container > div > div.indiv > form > table > tr > td > table > tr > td > div.gallery'
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
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME # + '/shop/good/'
		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	def process_category_list(self):

		__LOG__.Trace("********** process_category_list ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.CATEGORY_URL_HASH = None
			self.CATEGORY_URL_HASH = {}
			self.CATEGORY_URL_HASH[self.SITE_HOME] = 'PET'
			
		except Exception as ex:
			__LOG__.Error( "process_category_list Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
	
	
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			
			####################################
			# 상품 카테고리 추출
			####################################
			product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
		
			'''
			# 브랜드 확인		
			brand_div_list = product_ctx.find_all('span', class_='item_brand')
			for brand_ctx in brand_div_list :
				brand_name = brand_ctx.get_text().strip()
				if( brand_name != '') : product_data.crw_brand1 = brand_name.replace('[','').replace(']','').strip()
			'''	
							
			####################################				
			# 상품 이미지 확인
			####################################
	
			img_div_list = product_ctx.find_all('div', class_='goodsimg')
			for img_div_ctx in img_div_list :
				img_list = img_div_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
					if(img_src.startswith('..')) : 
						tmp_img_src = '/shop%s' % img_src[2:]
						img_src = tmp_img_src
						
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )
			
			'''
			# 품절여부 확인
			soldout_div_list = product_ctx.find_all('div', class_='item_icon_box')
			for soldout_div_ctx in soldout_div_list :
				if(config.__DEBUG__) : __LOG__.Trace('품절여부 확인')
				img_list = soldout_div_ctx.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs ) :
						if(0 < img_ctx.attrs['src'].find('soldout') ) :product_data.crw_is_soldout = 1
					

			
			# 품절여부 확인
			soldout_div_list = product_ctx.find_all('div', class_='item_photo_box')
			for soldout_div_ctx in soldout_div_list :
				if(config.__DEBUG__) : __LOG__.Trace('품절여부 확인')
				img_list = soldout_div_ctx.find_all('strong', class_='item_soldout_bg')
				for img_ctx in img_list :
					product_data.crw_is_soldout = 1
			'''
			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			####################################
			name_div_list = product_ctx.find_all('div', class_='goods_m_name')

			for name_div_ctx in name_div_list :

				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :

					if('href' in product_link_ctx.attrs ) : 
						product_data.crw_name = product_link_ctx.get_text().strip()

							
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?goodsno=')
						sub_split_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = sub_split_list[0].strip()
						
					
			####################################
			# 가격
			####################################	
			div_list = product_ctx.find_all('div')
			for div_ctx in div_list :
				cost_ctx = div_ctx.find('b')
				strike_ctx = div_ctx.find('strike')
				if( cost_ctx != None ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( cost_ctx.get_text().strip() ) )
				if( strike_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( strike_ctx.get_text().strip() ) )
							
			
			
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
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#contents', 'p', 'src' )
			
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
	
	
	
	