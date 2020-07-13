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
from mall.Mall import Mall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)

		self.SITE_HOME = 'https://www.wconcept.co.kr/Life/001014'
		
		self.SITE_ORG_HOME = 'https://www.wconcept.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		self.C_CATEGORY_VALUE = '#container > div > div.filter_wrap > div.filter_con > ul.depth.depth4.category > li > p > button'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#container > div > ul.pagination > li > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
	
		self.C_PRODUCT_VALUE = '#container > div > div.thumbnail_list > ul > li'
		self.C_PRODUCT_STRIP_STR = '/Life/001014'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = '#container > div > ul.pagination > li.last > a'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		
	
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
			crw_brand = []
			
			detail_page_txt = []
			detail_page_img = []

			
			soup = bs4.BeautifulSoup(html, 'lxml')

			# html에서 json data를 얻어옴
			brand_ctx = soup.find('h2', class_='brand')
			if(brand_ctx != None) : crw_brand.append( brand_ctx.get_text().strip() )
			
			table_list = soup.select('#container > div > div > div.pdt_contents.detail > table')
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			if('제조자(수입자)' in rtn_dict ) : crw_brand.append( rtn_dict['제조자(수입자)'].strip() )
			if('제조국(원산지)' in rtn_dict ) : crw_brand.append( rtn_dict['제조국(원산지)'].strip() )
			
			self.set_detail_brand( product_data, crw_brand )
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#container > div > div > div.pdt_contents.detail > div.marketing', 'p', 'src' )
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	
	
	'''
	# Mall.py 내용을 사이트에 맞게 Overwrite 함
	# 카테고리 및 각 페이지에 대한 URL을 구하는 부분이 필요하지 않음.
	# AJAX로 product 리스트를 갖고 올수 있음
	'''


		
	def get_page_data(self, category_url, html):
		rtn = False
		
		self.set_param_page(html)
		
		page_link_list = []
		
		last_page_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( self.C_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : page_link_list = soup.select(self.C_PAGE_VALUE)
		
		__LOG__.Trace( category_url )
		
		# 각 페이지 링크에 대한 처리
		avaible_page_count = 0
		for page_ctx in page_link_list :
			try :
				if('data-page' in page_ctx.attrs ) : 
					page_num = page_ctx.attrs['data-page']
					page_link = '%s%s%s' % ( category_url, self.PAGE_SPLIT_STR, page_num  )
					
					if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
						self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
						if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )
						rtn = True
						
			except Exception as ex:
				__LOG__.Error(ex)
				pass
				
		if(self.PAGE_LAST_LINK) :
			if( self.C_LAST_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : last_page_link_list = soup.select(self.C_LAST_PAGE_VALUE)
		
			# 맨끝 페이지 링크에 대한 처리
			last_num = 1
			for last_page_ctx in last_page_link_list :
				try :
					if('data-page' in last_page_ctx.attrs ) : 
						last_num = int(last_page_ctx.attrs['data-page']) + 1

				except Exception as ex:
					__LOG__.Error(ex)
					pass
			
			for page_num in range(1, last_num) :
				page_link = '%s%s%d' % ( category_url, self.PAGE_SPLIT_STR, page_num  )
					
				if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
					self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
					if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )
			
		
		return rtn , avaible_page_count
	
	

	def process_page(self, category_url):
	
		rtn = False
		resptext = ''
		avaible_page_count = 0
		
		try :
			
			if( config.__DEBUG__ ) :
				__LOG__.Trace('page : %s' % ( category_url ) )
				
			time.sleep(self.WAIT_TIME)
			URL = category_url
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn, avaible_page_count = self.get_page_data( category_url, resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn

		
		
	def get_category_data(self, html):
		rtn = False
		
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : category_link_list = soup.select(self.C_CATEGORY_VALUE)


		for category_ctx in category_link_list :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('data-depthcd' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['data-depthcd']
						category_link = '%s?ccd=3_%s' % (self.BASIC_CATEGORY_URL , tmp_category_link )
						category_name = category_ctx.get_text().strip()
						if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
							self.CATEGORY_URL_HASH[category_link] = category_name
							if( config.__DEBUG__ ) :
								__LOG__.Trace('%s : %s' % ( category_name, category_link ) )

							rtn = True

			except Exception as ex:
				__LOG__.Error(ex)
				pass
		

		
		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
	
	
	
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	def get_category_value(self, product_data, page_url, soup ) :
	
		if(self.PAGE_URL_HASH.get( page_url , -1) != -1) : 
			split_list = self.PAGE_URL_HASH[page_url].split('(')
			product_data.crw_category1 = split_list[0].strip()
			
		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			self.get_category_value( product_data, page_url, soup )
	
					
			####################################
			# 브랜드 추출	
			#
			# <div class="brand">SALLYS LAW</div>
			####################################
			brand_div_list = product_ctx.find_all('div', class_='brand')
			for brand_ctx in brand_div_list :
				product_data.crw_brand1 = brand_ctx.get_text().strip()
				
			####################################				
			# 상품 이미지 확인
			#
			# <div class="img">
			# <img src="//image.wconcept.co.kr/productimg/image/img1/96/300972496.jpg?RS=300" alt="">
			# </div>
			####################################
			img_div_list = product_ctx.find_all('div', class_='img')
			for img_div_ctx in img_div_list :
				img_list = img_div_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
					
					split_list = img_src.split('?')
					img_src = split_list[0].strip()
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )

			'''				
			####################################
			# 품절여부 추출
			####################################
			soldout_div_list = product_ctx.find_all('div', class_='item_icon_box')
			for soldout_div_ctx in soldout_div_list :
				img_list = soldout_div_ctx.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs ) :
						if(0 < img_ctx.attrs['src'].find('soldout') ) : product_data.crw_is_soldout = 1

			'''

			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <a href="/Product/300972496">
			# 
			####################################
			

			product_link_ctx = product_ctx.find('a')
			if( product_link_ctx != None ) :

				if('href' in product_link_ctx.attrs ) : 
					tmp_product_link = product_link_ctx.attrs['href'].strip()
					if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
					crw_post_url = tmp_product_link

					if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
				
					split_list = crw_post_url.split('/')
					product_data.crw_goods_code = split_list[4].strip()
					
				
			name_strong_list = product_ctx.find_all('div', class_='product ellipsis multiline')
			for name_strong_ctx in name_strong_list :
				product_data.crw_name = name_strong_ctx.get_text().strip()

			
			
			####################################
			# 가격
			#
			# <div class="price">
			# <span class="discount_price">74,400</span>
			# <span class="base_price">93,000</span>
			# <span class="discount_rate">20%</span>
			# </div>
			#
			####################################
			
			div_list = product_ctx.find_all('div', class_='price')
			for div_ctx in div_list :
				span_list = div_ctx.find_all('span')
				for span_ctx in span_list :
					if('class' in span_ctx.attrs ) :
						class_name_list = span_ctx.attrs['class']
						if(class_name_list[0] == 'base_price' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'discount_price' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
					
			
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

	
	
	
	