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
from makeshop.MakeShop import MakeShop


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(MakeShop) :    

	def __init__(self) :
	
		MakeShop.__init__(self)
		
		self.EUC_ENCODING = True

		self.SITE_HOME = 'http://www.puppygallery.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''

		self.C_CATEGORY_VALUE = '#lnb > div > table > tr > td > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#content > div > a'	
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#content > article > div > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		'''
		# MakeShop 추가 설정 부분
		'''

		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#lnb > div > table > tr > td > a'
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#category_nav > ul > li > span > a'
		
		#self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#category_nav > ul > li > span > a'

		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div > div.prd-detail'
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = 'p'
		

		self.SET_PRODUCT_DETAIL_DATA_TABLE = True
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = '#form1 > div > div.table-opt > table'
		
		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	def set_param_page(self, html) :
		try :

			soup = bs4.BeautifulSoup(html, 'lxml')
			mcode_link_list = soup.select( self.SET_CATEGORY_DATA_M_CODE_SELECTOR )
			
			for mcode_link_ctx in mcode_link_list :
				if('href' in mcode_link_ctx.attrs) :
					link_str = mcode_link_ctx.attrs['href']
					if(0 < link_str.find('mcode=')) :
						
						xcode_key , mcode_key = self.get_xcode_mcode( link_str )
						
						mcode_name = mcode_link_ctx.get_text().strip()
						key = '%s-%s' % ( xcode_key, mcode_key )
						self.MCODE_HASH[key] = mcode_name
						

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return True
		
		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			
			#for key in self.MCODE_HASH.keys() :
			#	__LOG__.Trace('%s : %s' % (key, self.MCODE_HASH[key] ))
				
			product_data = ProductData()
			crw_post_url = ''
			
			
			####################################				
			# 상품 이미지 확인
			# 상품 링크 정보 및 상품코드
			# 카테고리
			#
			# <p class="item-img"><img class="MS_prod_img_m" src="/shopimages/pupgallery/0060010000232.jpg?1557908161" alt="데님 브이하네스[인디고,라이트블루,핑크]"></p>
			####################################

			img_div_list = product_ctx.find_all('p', class_='item-img')
			for img_div_ctx in img_div_list :
				img_list = img_div_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('src' in img_ctx.attrs ) : 
						split_list = img_ctx.attrs['src'].strip().split('?')
						img_src = split_list[0].strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )
						break

			####################################				
			# 상품 링크 정보
			# 상품코드 / 카테고리
			#
			# <a href="/shop/shopdetail.html?branduid=2177018&amp;xcode=006&amp;mcode=001&amp;scode=&amp;type=X&amp;sort=manual&amp;cur_code=006&amp;GfDT=aGZ3UQ%3D%3D">
			#
			####################################

			product_link_ctx = product_ctx.find('a')
			if( product_link_ctx != None) :
				if('href' in product_link_ctx.attrs ) : 
					crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
					if(crw_post_url != '') :
						self.get_crw_goods_code( product_data, crw_post_url )
						self.get_category_value( product_data, crw_post_url )

							
			####################################
			# 상품명
			# <span class="name"><span class="MK-product-icons"></span> 데님 브이하네스[인디고,라이트블루,핑크]</span>
			####################################
			
			name_strong_ctx = product_ctx.find('span', class_='name')
			if( name_strong_ctx != None) :
				crw_name = name_strong_ctx.get_text().strip()
				if(0 < crw_name.find('(품절)') ) : 
					product_data.crw_is_soldout = 1
					tmp_crw_name = crw_name.replace('(품절)','').strip()
					crw_name = tmp_crw_name
					
				product_data.crw_name = crw_name

				
			

			####################################
			# 가격 확인 - 2가지 타입이 있음.
			#
			#------------------------------------------------------------
			#<p class="item-info">
			#<span class="name"><span class="MK-product-icons"></span> 데님 브이하네스[인디고,라이트블루,핑크]</span>  
			#<span class="subname">퍼피갤러리 데님 강아지브이하네스(xs~3xl) 가슴줄 하네스</span>
			#<!--할인율 표시시작-->
			#<span class="//&quot;abcd//&quot;"><b>20,000원</b></span>
			#<!--할인율 끝-->                                    </p>
			#------------------------------------------------------------
			# <div>
			# <span><strike>24,000원</strike>&nbsp;&nbsp;→</span>
			#<span class="abcd"><b>19,200원<span class="prod_dis_info">[20%↓]</span></b></span>
			# </div>
			####################################

			# 첫번째 타입 가격
			div_list = product_ctx.find_all('p', class_='item-info')
			for div_ctx in div_list :
				span_ctx = div_ctx.find('span', class_='//"abcd//"')
				if(span_ctx != None ) :	product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
			
			# 두번째 타입 가격
			if(product_data.crw_price_sale == 0 ) :
				div_list = product_ctx.find_all('div')
				for div_ctx in div_list :
					span_list = div_ctx.find_all('span')
					crw_price_sale = ''
					prod_dis_info = ''
					for span_ctx in span_list :
						if('class' in span_ctx ) :
							class_name_list = span_ctx['class']
							if(class_name_list[0] == '//"abcd//"') : crw_price_sale = span_ctx.get_text().strip()
							elif(class_name_list[0] == 'prod_dis_info"') : prod_dis_info = span_ctx.get_text().strip()
						else :
							strike_ctx = span_ctx.find('strike')
							if( strike_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( strike_ctx.get_text().strip() ))

					if(prod_dis_info == '') : 
						product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale ))
					else :
						price_pos = len(crw_price_sale) - len(prod_dis_info)
						product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale[:price_pos] ))
				
				
				
			
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
	
	
	