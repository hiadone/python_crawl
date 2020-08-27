#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항 
	- 반려동물매트 카테고리의 상품만 데이터 추출

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

		self.SITE_HOME = 'http://www.ecofoam.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#lnb > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['층간소음방지매트','거실매트','스페셜매트','키즈아이템','플레이매트','샘플신청']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#prdBrand > div.item-wrap > ol > a'	
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#prdBrand > div.item-wrap > div.item-list.grid > dl'
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

		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#lnb > ul > li > a'
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#lnb > div > div > dl > dd > a'
		
		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div > div.prd-detail'
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = 'p'
		

		self.SET_PRODUCT_DETAIL_DATA_TABLE = False
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = ''
		
		
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
			
			
			####################################				
			# 상품 이미지 확인
			# 상품 링크 정보 및 상품코드
			# 카테고리
			# 
			# <dd class="prd-img"><img class="MS_prod_img_s" src="/shopimages/ecofoam/0450010000053.jpg?1527467204" alt="상품 섬네일" title="상품 섬네일"></dd>
			#
			#
			# <dl class="item grid-item opa70" style="position: absolute; left: 0px; top: 0px;">
			#<a href="/shop/shopdetail.html?branduid=841206&amp;xcode=046&amp;mcode=004&amp;scode=&amp;type=Y&amp;sort=manual&amp;cur_code=046&amp;GfDT=bW53UQ%3D%3D">
			#
			#
			####################################

			img_div_list = product_ctx.find_all('dd', class_='prd-img')
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


			product_link_ctx = product_ctx.find('a')
			if( product_link_ctx != None) :
				if('href' in product_link_ctx.attrs ) : 
					crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
					if(crw_post_url != '') :
						self.get_crw_goods_code( product_data, crw_post_url )
						self.get_category_value( product_data, crw_post_url )

						
			####################################
			# 상품명 및 브랜드
			#
			# <span class="prd-name ft_eb">도그자리 플랫<br></span>
			#
			# --- 품절시 상품명 ---
			# <span class="prd-name ft_eb">맘편한매트 소프트W<br>8세트(품절)</span>
			#
			# --- 브랜드 ---
			# <span class="prd-brand">도그자리</span>
			####################################
			
			name_strong_ctx = product_ctx.find('span', class_='prd-name ft_eb')
			if( name_strong_ctx != None) :
				crw_name = name_strong_ctx.get_text().strip()
				if(0 < crw_name.find('(품절)') ) : 
					product_data.crw_is_soldout = 1
					tmp_crw_name = crw_name.replace('(품절)','').strip()
					crw_name = tmp_crw_name
					
				product_data.crw_name = crw_name
				
			name_strong_ctx = product_ctx.find('span', class_='prd-brand')
			if( name_strong_ctx != None) :
				product_data.crw_brand1 = name_strong_ctx.get_text().strip()

				
			

			####################################
			# 가격
			#
			# <span class="prd-price-discount"><del>75,000</del></span>
			#
			# <span class="prd-discount ft_eb">52,000&nbsp;원</span>
			#
			####################################
			
			div_list = product_ctx.find_all('div', class_='prd-sub')
			for div_ctx in div_list :
				sell_ctx = div_ctx.find('span', class_='prd-discount ft_eb')
				consumer_ctx = div_ctx.find('span', class_='prd-price-discount')
					
				if( consumer_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( consumer_ctx.get_text().strip() ))

				if( sell_ctx != None ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( sell_ctx.get_text().strip() ))
			
			
			
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
	
	
	