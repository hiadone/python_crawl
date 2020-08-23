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
		
		
		self.SITE_HOME = 'http://m.rudolphshop.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		#self.C_CATEGORY_VALUE = '#main_center_banner > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = [ ]
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-menupackage > div.xans-element-.xans-product.xans-product-normalpaging.paginate.typeList > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-normalmenu > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li > p > a'

		self.C_PRODUCT_VALUE = '#contents > div.xans-element-.xans-product.xans-product-menupackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product.typeThumb > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
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
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'span'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'icon'
		
		
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	
	def get_category_data(self, html):
		rtn = False
		
		#__LOG__.Trace(html)
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select('#screenOverlay > div > div.screen-overlay-content-top')
			#category_link_list = soup.select('#navPrdList')
		
		__LOG__.Trace('----------------------------------------------------------')
		for m_category_ctx in category_link_list :
			#__LOG__.Trace(m_category_ctx)
			try :
				idx = 0
				mid_category_list = m_category_ctx.find_all('h2')
				#__LOG__.Trace(len(mid_category_list))
				ul_list = m_category_ctx.find_all('ul', class_='overflow-x')
				for ul_ctx in ul_list :
					#__LOG__.Trace(ul_ctx)
					mid_category_name = mid_category_list[idx].get_text().strip()
					idx += 1
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						category_ctx = li_ctx.find('a')
						if( category_ctx != None ) :
							if(self.check_ignore_category( category_ctx ) ) :
								if('href' in category_ctx.attrs ) : 
									tmp_category_link = category_ctx.attrs['href']
									if(tmp_category_link.find('javascript') < 0 ) :
										if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

										category_link = tmp_category_link
										
										if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
										
										category_name = category_ctx.get_text().strip()
	
										if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
											self.CATEGORY_URL_HASH[category_link] = '%s|%s' % ( mid_category_name, category_name )
											if( config.__DEBUG__ ) :
												__LOG__.Trace('%s|%s : %s' % ( mid_category_name, category_name, category_link ) )

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
	
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			# 상품 카테고리
			#
			split_list = self.PAGE_URL_HASH[page_url].split('|')
			idx = 0
			for split_data in split_list :
				idx += 1
				if(idx == 1 ) : product_data.crw_category1 = split_data.strip()
				elif(idx == 2 ) : product_data.crw_category2 = split_data.strip()
				elif(idx == 3 ) : product_data.crw_category3 = split_data.strip()
				

			# 상품 이미지 확인
			div_list = product_ctx.find_all('div', class_='thumbnail')
			for div_ctx in div_list :
				a_link_list = product_ctx.find_all('a')
				for a_link_ctx in a_link_list :
					img_list = a_link_ctx.find_all('img')
					for img_ctx in img_list :
						if('src' in img_ctx.attrs ) :
							img_src = img_ctx.attrs['src'].strip()
							if( img_src != '' ) :
								img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
								if(product_data.product_img == '') : product_data.product_img = self.get_hangul_url_convert( img_link )

			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 
			

			name_div_list = product_ctx.find_all('strong', class_='name')

			for name_div_ctx in name_div_list :
				#
				# 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :				
					if('href' in product_link_ctx.attrs ) : 
						product_data.crw_name = product_link_ctx.get_text().strip()
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
						split_list = crw_post_url.split('/')
						if( product_data.crw_name == '') : product_data.crw_name = split_list[4].strip()
						product_data.crw_goods_code = split_list[5].strip()

				
			#
			# 가격 / 브랜드
			#

			div_list = product_ctx.find_all('div', class_='description')
			for div_ctx in div_list :
				span_list = div_ctx.find_all('span')
				for span_ctx in span_list :
					if('class' in span_ctx.attrs ) :
						class_name_list = span_ctx.attrs['class']
						if(len(class_name_list) == 1) and ( class_name_list[0].strip() == 'summary') : product_data.crw_brand1 = span_ctx.get_text().strip()
						
				li_list = div_ctx.find_all('li')
				for li_ctx in li_list :
					if('class' in li_ctx.attrs ) :
						class_name_list = li_ctx.attrs['class']
						if(len(class_name_list) == 1) and ( class_name_list[0].strip() == 'price') : product_data.crw_price = int( __UTIL__.get_only_digit( li_ctx.get_text().strip() ) )
						
			
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
						
			brand_list = soup.find_all('span', {'id':'brand'} )
			for brand_ctx in brand_list :
				a_link_ctx = brand_ctx.find('a')
				if('alt' in a_link_ctx.attrs) : product_data.d_crw_brand1 = a_link_ctx.attrs['alt'].strip()
				
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#prdDetailContentLazy', 'p', 'src' )
			if( len(detail_page_img) == 0 ) : detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#prdDetailContentLazy', 'p', 'ec-data-src' )
			
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
	

	
	
	