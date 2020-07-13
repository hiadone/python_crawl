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
		
		self.SITE_HOME = 'http://www.cocochien.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#left_menu > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''

		self.C_PAGE_VALUE = '#productClass > div.page-body > div.prd-list > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = '#productClass > div.page-body > div.prd-list > table > tbody > tr > td > div > div > a'
		self.C_PRODUCT_VALUE = '#productClass > div.page-body > div.prd-list > table > tbody > tr > td > div'
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
		
		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#left_menu > li > a'
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#left_menu > li > ul > li > a'
		
		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div > div.prd-detail'
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = 'p'
		

		self.SET_PRODUCT_DETAIL_DATA_TABLE = True
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = '#form1 > div > div.info > div.table-opt > table'
		
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
			# <div class="thumb salebox">
			# <a href="/shop/shopdetail.html?branduid=3534594&amp;xcode=003&amp;mcode=001&amp;scode=&amp;type=X&amp;sort=manual&amp;cur_code=003&amp;GfDT=aWt3UQ%3D%3D"><img class="MS_prod_img_m" src="/shopimages/cocochien/0030010000152.jpg?1581790516" alt="상품 섬네일"></a>
			# <input type="hidden" name="custom_price" value="0">
			# <input type="hidden" name="product_price" value="34500">
			# <div id="sale_bg" style="display: none;"><span class="sale_text"></span></div>
			# <div class="info_icon">
			# <span class="m_quickview"><a class="btn-overlay-show" href="javascript:viewdetail('003001000015', '1', '');"><img src="/design/cocochien/0746amelie/info_icon02.gif"></a></span>										<span class="m_option"><img src="/shopimages/cocochien/bt_opt_preview.gif" onclick="javascript:mk_prd_option_preview('3534594',event);"></span>									</div><!-- //info_icon -->
			# </div>
			####################################

			img_div_list = product_ctx.find_all('div', class_='thumb salebox')
			for img_div_ctx in img_div_list :
				product_link_list = img_div_ctx.find_all('a')
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
						
						
						
				for product_link_ctx in product_link_list :
					if('href' in product_link_ctx.attrs ) : 
						crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
						if(crw_post_url != '') :
							self.get_crw_goods_code( product_data, crw_post_url )
							self.get_category_value( product_data, crw_post_url )
							break
							
						

			####################################
			# 상품명 및 브랜드
			# <li class="dsc">앨리스튜튜</li>
			####################################
			name_strong_list = product_ctx.find_all('li', class_='dsc')
			for name_strong_ctx in name_strong_list :
				product_data.crw_name = name_strong_ctx.get_text().strip()
				#
				# 이름 앞에 브랜드명이 있음.
				# [스텔라&츄이] 츄이스 치킨 디너패티 
				if( 0 == product_data.crw_name.find('[')) :
					brand_list = product_data.crw_name.split(']')
					product_data.crw_brand1 = brand_list[0][1:].strip()
				
			

			####################################
			# 가격 / 품절 여부 확인
			#
			#<ul class="info">
			# <li class="dsc">네이비도트원피스(50%SALE)SM,XL주문가능</li>
			# <li class="subname"></li>
			# <li class="consumer">26,000원</li>										<li class="price">13,000원</li>
			# <li class="icon"><span class="MK-product-icons"></span></li>
			# </ul>
			#
			#---------- 품절시 --------------------
			# <ul class="info">
			#	<li class="dsc">마카롱나시원피스(50%SALE)</li>
			#	<li class="subname"></li>
			#	<li class="soldout">SOLD OUT</li>
			#	<li class="icon"><span class="MK-product-icons"></span></li>
			#	</ul>
			####################################
			
			div_list = product_ctx.find_all('ul')
			for div_ctx in div_list :
				sell_ctx = div_ctx.find('li', class_='price')
				consumer_ctx = div_ctx.find('li', class_='consumer')
				soldout_ctx = div_ctx.find('li', class_='soldout')
				if( soldout_ctx != None ) : product_data.crw_is_soldout = 1
					
				if( consumer_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( consumer_ctx.get_text().strip() ))

				if( sell_ctx != None ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( sell_ctx.get_text().strip() ))

			
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
	
	
	