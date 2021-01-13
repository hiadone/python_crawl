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
from sixshop.SixShop import SixShop


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(SixShop) :    

	def __init__(self) :
	
		SixShop.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://pethod.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		#self.C_CATEGORY_VALUE = '#siteHeader > div.row.row-main.desktop > div.column.header-left > nav > ul > li.menu-navi.menu-main.pageMenu > a'
		self.C_CATEGORY_VALUE = '#siteHeader > div.row.row-main.desktop > div.column.header-right > div.headerMenuList.desktop.site-element > ul > li.menu-navi.menu-main.pageMenu.subMenu-exist > div.subMenuNaviListDiv > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['ONLY YOU','News','Review','Q&A','주문제작']
		self.C_CATEGORY_STRIP_STR = ''

		
		'''
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'	# 페이지 selector 가 없어서 임의로 지정함
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		'''
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		
				
		self.C_PRODUCT_VALUE = '#displayCanvas > div > div > section.section > div > div > div > div > div'
		self.C_PRODUCT_STRIP_STR = ''
		
		'''
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부
		'''
		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		
	
	'''
	######################################################################
	#
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''
	def get_product_data(self, category_key, html):
		self.get_product_data_second_sixshop( category_key, html )
		
	def process_product(self, category_key):
		self.process_product_second_sixshop( category_key )
	
	def set_product_data(self , category_key, soup, product_ctx ) :
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			self.reset_product_category(product_data)
			
			####################################
			# 상품 카테고리 추출
			####################################
			
			self.get_category_value( product_data, category_key, soup )
			
			

			####################################				
			# 상품 이미지 확인
			#
			# <div class="thumb img" imgsrc="/uploadedFiles/46606/product/image_1573609552547.jpeg" style="width:100%;background-image:url(https://contents.sixshop.com/thumbnails/uploadedFiles/46606/product/image_1573609552547_1000.jpeg)"></div>
			#
			####################################
			img_div_list = product_ctx.find_all('img', class_='thumb img')

			for img_div_ctx in img_div_list :				
				if('src' in img_div_ctx.attrs ) :
					tmp_img_src = img_div_ctx.attrs['src'].strip()
					# split_list = tmp_img_src.split(':url(')
					img_src = tmp_img_src
					
					if( img_src != '' ) :						
						#img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_src )

							
			
			####################################
			# 품절여부 추출
			#
			# <div class="soldOutBadge badge"><span>Sold Out</span></div>
			#
			####################################
			soldout_div_list = product_ctx.find_all('div', class_='soldOutBadge badge')
			for soldout_div_ctx in soldout_div_list :
				product_data.crw_is_soldout = 1
			
			# 가격 부분에 sold out 문구가 있는 경우
			price_div_list = product_ctx.find_all('div', class_='shopProduct price')
			for price_ctx in price_div_list :
				soldout_str = price_ctx.get_text().strip()
				if(0 <= soldout_str.lower().find('sold')) and (0 < soldout_str.lower().find('out')) : product_data.crw_is_soldout = 1
			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="shopProductWrapper badgeUse" data-productno="1008345"><a href="/product/Chu"><div class="thumbDiv"><div class="thumb img" imgsrc="/uploadedFiles/46606/product/image_1573609552547.jpeg" style="width:100%;background-image:url(https://contents.sixshop.com/thumbnails/uploadedFiles/46606/product/image_1573609552547_1000.jpeg)"></div><div class="shopProductBackground"></div><div class="badgeWrapper"><div class="soldOutBadge badge"><span>Sold Out</span></div></div></div><div class="shopProductNameAndPriceDiv"><div class="shopProductNameAndPriceContent"><div class="shopProductNameAndPrice"><div class="shopProduct productName">멜로니코코 풉백</div><div class="shopProduct price"><span class="productPriceSpan">20,000원</span></div></div></div></div></a></div>
			#
			####################################
			
			if('data-productno' in product_ctx.attrs ) : product_data.crw_goods_code = product_ctx.attrs['data-productno']
			
			product_link_ctx = product_ctx.find('a')
			if( product_link_ctx != None) :
				if('href' in product_link_ctx.attrs ) : 					
					tmp_product_link = product_link_ctx.attrs['href'].strip()
					if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
					crw_post_url = tmp_product_link

					if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

							
			name_div_list = product_ctx.find_all('div', class_='shopProduct productName')
			
			for name_div_ctx in name_div_list :
				product_data.crw_name = name_div_ctx.get_text().strip()
				
			
			####################################
			# 가격
			#
			# <span class="productPriceSpan">20,000원</span>
			#
			# <div class="shopProduct price"><span class="productDiscountPriceSpan">16,200원 </span><span class="productPriceWithDiscountSpan">18,000원</span></div>
			####################################			
			price_div_list = product_ctx.find_all('div', class_='shopProduct price')

			for price_ctx in price_div_list :	
				span_list = price_ctx.find_all('span')
				for span_ctx in span_list :
					if('class' in span_ctx.attrs ) :
						class_name_list = span_ctx.attrs['class']
						if(class_name_list[0] == 'productPriceSpan' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'productDiscountPriceSpan' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
						elif(class_name_list[0] == 'productPriceWithDiscountSpan' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
					

			
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
	
	
	