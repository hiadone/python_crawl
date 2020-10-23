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
		
		#self.SITE_HOME = 'http://www.dermadog.co.kr/shop/shopbrand.html?type=X&xcode=001'
		
		self.SITE_HOME = 'http://www.dermadog.co.kr'
		
		self.ORG_SITE_HOME = 'http://www.dermadog.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#lnbWrap > ul > li > div > div > ul > li > a'
		#self.C_CATEGORY_VALUE = '#prdBrand > div.cate-wrap > div.class-list > ul > li > a'
		#self.C_CATEGORY_VALUE = '#lnbWrap > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['ABOUT US','EVENT','COMMUNITY','BOARD']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#prdBrand > div.item-wrap > div.item-page > a'	
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		
		self.C_PRODUCT_VALUE = '#prdBrand > div.item-wrap > div > dl'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#prdBrand > div.item-wrap > div.item-page > a.pager.last'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		'''
		# MakeShop 추가 설정 부분
		'''

		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#lnbWrap > ul > li > a'
		#self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#lnbWrap > ul > li > div > div > ul > li > a'
		#self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#prdBrand > div.cate-wrap > div.class-list > ul > li > a'
		#self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#prdBrand > div.cate-wrap > div.class-list > ul > li > ul > li > a'
		
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#lnbWrap > ul > li > div > div > ul > li > a'
		self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#prdBrand > div.cate-wrap > div.class-list > ul > li > a'
		
		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div > div.prd-detail > center > div'
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR_SECOND = '#productDetail > div > div'
		
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = ''
		

		self.SET_PRODUCT_DETAIL_DATA_TABLE = True
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = '#form1 > div > div.table-opt > table'
		
		
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
			# <dt class="thumb"><a href="/shop/shopdetail.html?branduid=10163894&amp;xcode=001&amp;mcode=005&amp;scode=003&amp;type=X&amp;sort=manual&amp;cur_code=001&amp;GfDT=bml9W1w%3D"><img class="MS_prod_img_m" src="/shopimages/dermadog/0010050000192.jpg?1591754112" alt="상품 섬네일" title="상품 섬네일"></a></dt>
			####################################

			img_div_list = product_ctx.find_all('dt', class_='thumb')
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

				product_link_ctx = img_div_ctx.find('a')
				if( product_link_ctx != None) :
					if('href' in product_link_ctx.attrs ) : 
						crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
						if(crw_post_url != '') :
							self.get_crw_goods_code( product_data, crw_post_url )
							self.get_category_value( product_data, crw_post_url )
						

			
			####################################
			# 상품명 및 브랜드
			#
			# <dd class="prd-info">
			# <ul>  
			# <li class="prd-brand"><span class="MK-product-icons"><img src="/shopimages/dermadog/prod_icons/4154?1591753540" class="MK-product-icon-2"></span></li>
			# <li class="prd-name"><a href="/shop/shopdetail.html?branduid=10163894&amp;xcode=001&amp;mcode=005&amp;scode=003&amp;type=X&amp;sort=manual&amp;cur_code=001&amp;GfDT=bml9W1w%3D">연어/스킨 헬스츄 15g</a></li>
			# </ul>
			# </dd>
			#
			####################################
			name_dd_list = product_ctx.find_all('dd', class_='prd-info')
			for name_dd_ctx in name_dd_list :
				name_ctx = name_dd_ctx.find('li', class_='prd-name')
				if( name_ctx != None) : product_data.crw_name = name_ctx.get_text().strip()
				
				brand_ctx = name_dd_ctx.find('li', class_='prd-brand')
				if( brand_ctx != None) : product_data.crw_brand1 = brand_ctx.get_text().strip()


			####################################
			# 가격 / 품절 여부 확인
			#
			#
			# <p class="price-info">
			# <strike>10,000</strike><br>
			# <span class="won">￦</span><span class="price">9,000</span>
			# </p>
			#
			#---- 품절시  -------
			#
			# <p class="price-info">
			# Sold Out
			# </p>
			#
			####################################
			
			div_list = product_ctx.find_all('p', class_='price-info')
			for div_ctx in div_list :
				price_str = div_ctx.get_text().strip()
				if(0 <= price_str.find('Out')) : product_data.crw_is_soldout = 1
				
				sell_ctx = div_ctx.find('span', class_='price')
				consumer_ctx = div_ctx.find('strike')
					
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
	
	
	