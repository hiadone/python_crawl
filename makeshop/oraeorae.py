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
		
		self.DETAIL_CATEGORY_ACTION = True
		self.C_DETAIL_CATEGORY_VALUE = '#prdBrand > div.cate-wrap > div.class-list > ul > li > a'
		
		
		self.EUC_ENCODING = True
		
		self.SITE_HOME = 'http://www.oraeorae.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#self.C_CATEGORY_VALUE = '#hdWrap > div.gnb > ul > li > ul > li > a'
		self.C_CATEGORY_VALUE = '#hdWrap > div.gnb > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['고양이 야옹']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#prdBrand > div.item-wrap > div.item-page > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1','다음','맨뒤']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#prdBrand > div.item-wrap > div > dl'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = '#prdBrand > div.item-wrap > div.item-page > a'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		'''
		# MakeShop 추가 설정 부분
		'''
		
		
		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#hdWrap > div.gnb > ul > li > a'
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#hdWrap > div.gnb > ul > li > ul > li > a'
		self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#prdBrand > div.cate-wrap > div.class-list > ul > li > a'


		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div.page-body > div.prd-detail'
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
			# <dt class="thumb"><a href="/shop/shopdetail.html?branduid=803964&amp;xcode=035&amp;mcode=003&amp;scode=&amp;type=Y&amp;sort=manual&amp;cur_code=035&amp;GfDT=aGV%2BVA%3D%3D"><img class="MS_prod_img_s" src="/shopimages/aromnaom/0330290001733.jpg?1581494094"></a></dt>
			# 
			####################################

			img_div_list = product_ctx.find_all('dt', class_='thumb')
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
			#
			# <li class="prd-name">[애니케어] 면역을 위한 멀티파우더 <span class="MK-product-icons"></span></li>
			####################################
			name_strong_list = product_ctx.find_all('li', class_='prd-name')
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
			# <li class="prd-price">74,800원</li>
			#
			# ---- 품절시  -------
			# <li class="prd-price">                                                     
			# <span class="fc-red">품절</span>
            # </li>
			####################################
			
			div_list = product_ctx.find_all('ul')
			for div_ctx in div_list :
				sell_ctx = div_ctx.find('li', class_='prd-price')
				if( sell_ctx != None ) : 
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( sell_ctx.get_text().strip() ))
					soldout_ctx = div_ctx.find('span', class_='fc-red')
					if( soldout_ctx != None ) : product_data.crw_is_soldout = 1
						
					
					
			
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
	
	
	