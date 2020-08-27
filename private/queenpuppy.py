#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- 카테고리별 페이지가 없이 하나의 화면에 상품리스트를 디스플레이함.

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
		
		self.EUC_ENCODING = True
		
		self.SITE_HOME = 'http://www.queenpuppy.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#cate > span > a
		#header_wrap > div.box3 > div > div > div > div > div > ul > li > a
		#self.C_CATEGORY_VALUE = '#header_wrap > div.box3 > div > div > div > div > div > ul > li.title > a'
		#header_wrap > div.box3 > div > div > div > div > div > ul > li > a
		self.C_CATEGORY_VALUE = '#header_wrap > div.box3 > div > div > div > div > div > ul > li.item > a'
		self.C_CATEGORY_IGNORE_STR = ['이달의 한정할인']
		self.C_CATEGORY_STRIP_STR = ''

		
		#layout_body > table > tr > td > table > tr > td > div > a
		#self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_PAGE_TYPE = ''
		#self.C_PAGE_VALUE = '#layout_body > table > tr > td > table > tr > td > div > a'
		#self.C_PAGE_STRIP_STR = '../'
		
		#self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		#self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = 'body > div.body_wrap > div.content_wrap > div > div.product_wrap > div'
		self.C_PRODUCT_STRIP_STR = './'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		#self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_LAST_PAGE_TYPE = ''
		
		#self.C_LAST_PAGE_VALUE = ''
		
		#self.PAGE_SPLIT_STR = '?page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		#self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		#self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		

		
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	def process_page(self, category_url):
	
		rtn = False
		
		try :

			self.PAGE_URL_HASH[category_url] = self.CATEGORY_URL_HASH[category_url]
			
			if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( category_url ) )
			rtn = True

		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
	
	def get_product_detail_data(self, product_data, html):
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')

			div_list = soup.find_all('div', class_='info_line')
			
			for div_ctx in div_list :
				title_name = ''
				content_value = ''
				
				title_ctx = div_ctx.find('div', class_='tit')
				content_ctx = div_ctx.find('div', class_='content')
				if(title_ctx != None ) : title_name = title_ctx.get_text().strip()
				if(content_ctx != None ) : content_value = content_ctx.get_text().strip()
				
				if(0 <= title_name.find('제조사') ) or (0 <= title_name.find('브랜드') ) or (0 <= title_name.find('원산지') ) : crw_brand.append( content_value )

			self.set_detail_brand( product_data, crw_brand )
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#pd_detail0', '', 'src' )
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
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
			
			self.reset_product_category(product_data)
			
			category_ctx_list = soup.select('body > div.body_wrap > div.content_wrap > div.section_tit > div.close')
			
			for category_ctx in category_ctx_list :
				split_list = category_ctx.get_text().strip().split('>')
				idx = 0
				for split_data in split_list :
					idx += 1
					category_name = split_data.strip()
					if(idx == 2 ) : product_data.crw_category1 = category_name
					elif(idx == 3 ) : product_data.crw_category2 = category_name
					elif(idx == 4 ) : product_data.crw_category3 = category_name
				
			#split_list = self.PAGE_URL_HASH[page_url].split('(')
			#product_data.crw_category1 = split_list[0].replace('BEST','').strip()
			

			####################################
			# 브랜드 추출	
			#
			# <div class="line_sub">
			# 한국산				</div>
			####################################


			div_list = product_ctx.find_all('div', class_='line_sub')
			for div_ctx in div_list :
				brand_str = div_ctx.get_text().strip()
				product_data.crw_brand1 = brand_str

			
			####################################				
			# 상품 이미지 확인 / 상품 링크 정보 / 상품번호
			#
			# <div class="picture"><a href="./product.html?pd_code=A010489&amp;event_type=%C3%CA%C6%AF%B0%A1"><img src="http://queenpuppy.co.kr/shop/pd_img/A01/489/A010489_2.jpg"></a></div>
			####################################

			span_list = product_ctx.find_all('div', class_='picture')
			for span_ctx in span_list :
				product_link_ctx = span_ctx.find('a')
				if( product_link_ctx != None ) :
					if('href' in product_link_ctx.attrs ) : 
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						
						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
						split_list = crw_post_url.split('&event_type=')
						crw_post_url = split_list[0].strip()
						
						
						split_list = crw_post_url.split('?pd_code=')
						sub_split_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = sub_split_list[0]
					
					img_list = product_link_ctx.find_all('img')
					for img_ctx in img_list :
						img_src = ''
						if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
						elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
							
						if( img_src != '' ) :
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							product_data.product_img = self.get_hangul_url_convert( img_link )

				
			####################################
			# 상품명
			# 
			# <div class="name">
			# <div style="color:#fd705f; font-weight: bold; valign:top; height: 15px; padding-bottom: 3px;"></div>
			# <a href="./product.html?pd_code=A010489&amp;event_type=%C3%CA%C6%AF%B0%A1">
			# 건국유업 프로젝트 닥터케이 펫밀크 10개입										</a>
			# </div>
			####################################
			name_div_list = product_ctx.find_all('div', class_='name')
			for name_div_ctx in name_div_list :
				span_ctx = name_div_ctx.find('a')
				if(span_ctx != None) : 
					crw_name = span_ctx.get_text().strip()
					product_data.crw_name = crw_name
					if(0 < crw_name.find('[품절]') ) :
						product_data.crw_is_soldout = 1
						product_data.crw_name = crw_name.replace('[품절]','').strip()
 
	
	

			####################################
			# 가격
			#
			#
			# <div class="line_np">20,000원</div>
			# <div class="line_sp">
			# 12,000원
			# <span style="font-size: 0.8em; color: #666; vertical-align:bottom;">40%↓</span>									</div>
			####################################
			
			div_list = product_ctx.find_all('div', class_='line_np')
			for div_ctx in div_list :
				price_str = div_ctx.get_text().strip()
				product_data.crw_price = int( __UTIL__.get_only_digit( price_str ) )

			div_list = product_ctx.find_all('div', class_='line_sp')
			for div_ctx in div_list :
				price_str = div_ctx.get_text().strip()
				span_ctx = div_ctx.find('span')
				split_str = ''
				if(span_ctx != None) : split_str = span_ctx.get_text().strip()
				if( split_str == '') :
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( price_str.strip() ) )
				else :
					split_list = price_str.split( split_str )
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( split_list[0].strip() ) )			


			
			if( crw_post_url != '' ) :
				#if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
				
				self.set_product_data_sub( product_data, crw_post_url )		
				self.process_product_api(product_data)
										
				rtn = True


		except Exception as ex:
			__LOG__.Error('에러 : set_product_data')
			__LOG__.Error(ex)
			pass
			
		return True	
		
	

		
	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()

	
	
	
	