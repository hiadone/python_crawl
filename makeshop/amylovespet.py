#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

- 특이 사항

2020.06.08
  물품리스트의 HTML 형식이 잘못된 상태임.
  CSS SELECTOR 를 물품리스트 검출시, 비정상 상태로 물품리스트가 1개 또는 0개로 나옴.
  물품리스트를 갖고 오는 부분의 별도로 만듬.
  
  영향 받는 함수
  1) get_product_data()
  2) set_product_data()
  

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

		self.SITE_HOME = 'http://www.amylovespet.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#header > div > ul.category.hovermenu > li > a'
		self.C_CATEGORY_VALUE_2 = '#header > div > ul.category.hovermenu > li > div > ul > li > a'
		
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		#self.C_PAGE_VALUE = '#content > div > div.item-page.ec-base-paginate > ol > li > a'	
		#self.C_PAGE_VALUE_2 = '#content > div.item-page.ec-base-paginate > ol > li > a'
		
		#self.C_PAGE_VALUE = 'body > div > div > div > div > div > ol > li > a'	
		#self.C_PAGE_VALUE_2 = 'body > div > div > div > div > ol > li > a'
		
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		
		#self.C_PRODUCT_VALUE = '#content > div > div.ec-base-product > ul.prdList.grid4 > li'
		
		
		self.C_PRODUCT_VALUE = '#content > div > div.ec-base-product'
		self.C_PRODUCT_VALUE_2 = '#content > div.ec-base-product'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		
		
		#self.C_LAST_PAGE_VALUE = '#content > div > div.item-page.ec-base-paginate > a.last'
		#self.C_LAST_PAGE_VALUE_2 = '#content > div.item-page.ec-base-paginate > a.last'
		
		#self.C_LAST_PAGE_VALUE = 'body > div > div > div > div > div > a'
		#self.C_LAST_PAGE_VALUE_2 = 'body > div > div > div > div > a'
		
		#self.C_LAST_PAGE_VALUE = '#content > div > div > a.last'
		#self.C_LAST_PAGE_VALUE_2 = '#content > div > a.last'


		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		'''
		# MakeShop 추가 설정 부분
		'''

		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = '#header > div > ul.category.hovermenu > li > a'
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = '#header > div > ul.category.hovermenu > li > div > ul > li > a'
		#self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#content > div > div > ul > li > a'
		self.SET_CATEGORY_DATA_S_CODE_SELECTOR = '#content > div.xans-product-menupackage > ul > li > a'
		self.SET_CATEGORY_DATA_S_CODE_SELECTOR_2 = '#content > div > div > ul > li > a'
		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = '#productDetail > div > div.prd-detail'
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = 'p'
		

		self.SET_PRODUCT_DETAIL_DATA_TABLE = False
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = ''
		
		
	'''
	######################################################################
	#
	# MakeShop.py 대체
	#
	######################################################################
	'''
	
	def set_param_page(self, html ) :
		# self.SCODE_HASH : 최하위 카테고리명 dict dict key는 xcode,mcode 조합 ( xxx-mmm-sss )
		#
		try :
			soup = bs4.BeautifulSoup(html, 'lxml')
			scode_link_list = []

			menuCategory_ctx = soup.find('ul', class_='menuCategory' )
			if( menuCategory_ctx != None ) : scode_link_list = menuCategory_ctx.find_all('a')
				
			
			for scode_link_ctx in scode_link_list :
				#__LOG__.Trace( scode_link_ctx )
				if('href' in scode_link_ctx.attrs) :
					link_str = scode_link_ctx.attrs['href']
					if(0 < link_str.find('&scode=')) :

						xcode_key , mcode_key , scode_key = self.get_xcode_mcode_scode( link_str )
						if(scode_key != '' ) :
							split_list = scode_link_ctx.get_text().strip().split('(')
							scode_name = split_list[0].strip()
							key = '%s-%s-%s' % ( xcode_key, mcode_key, scode_key  )
							if(self.SCODE_HASH.get(key, -1) == -1 ) : self.SCODE_HASH[key] = scode_name
			
			#for key in self.SCODE_HASH.keys() :
			#	__LOG__.Trace('S_CODE - %s : %s' % (key, self.SCODE_HASH[key]) )
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return True
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''	
	def get_page_data(self, category_url, html):
		rtn = False
		
		self.set_param_page(html)
		
		page_link_list = []
		
		last_page_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( self.C_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : 
			page_part_ctx = soup.find('div', class_='item-page ec-base-paginate')
			if(page_part_ctx != None) :
				page_link_list = page_part_ctx.find_all('li')

		__LOG__.Trace('page_link_list : %d ' % len(page_link_list) )
		
		if(self.PAGE_LAST_LINK) :
			if( self.C_LAST_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : 
				last_page_link_list = soup.find_all('a', class_='last')
		
			# 맨끝 페이지 링크에 대한 처리
			__LOG__.Trace('last_page_link_list : %d ' % len(last_page_link_list) )

			for last_page_ctx in last_page_link_list :
				try :
					
					if('href' in last_page_ctx.attrs ) : 
						page_link = last_page_ctx.attrs['href']
						if(0 != page_link.find('http')) : page_link = '%s%s' % ( self.BASIC_PAGE_URL, last_page_ctx.attrs['href'] )
						
						if(0 < page_link.find( self.PAGE_SPLIT_STR )) : self.get_page_url_split( page_link , True )

				except Exception as ex:
					__LOG__.Error(ex)
					pass
		
		# 각 페이지 링크에 대한 처리
		avaible_page_count = 0
		for page_link_ctx in page_link_list :
			try :
				page_ctx = page_link_ctx.find('a')
				if(page_ctx != None) :
					if(self.check_ignore_page( page_ctx ) ) :
						if('href' in page_ctx.attrs ) : 
							avaible_page_count += 1
							tmp_page_link = page_ctx.attrs['href']
							if(0 != tmp_page_link.find('http')) : 
								if( 0 == tmp_page_link.find('?page=') ) :			
									# 페이지 링크 정보가 '?page=' 로 시작되어 질때, 카테고리 URL을 추가해준다.
									tmp_page_link = '%s%s' % ( category_url, page_ctx.attrs['href'] )
								else : 
									tmp_page_link = '%s%s' % ( self.BASIC_PAGE_URL, page_ctx.attrs['href'] )
							
							page_link = tmp_page_link

							if(self.C_PAGE_STRIP_STR != '') : page_link = tmp_page_link.replace( self.C_PAGE_STRIP_STR,'')
							if( page_link.find('javascript') < 0 ) :
								if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
									if( self.DETAIL_CATEGORY_ACTION ) : self.PAGE_URL_HASH[page_link] = self.DETAIL_CATEGORY_URL_HASH[category_url]
									else : self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
									#self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
									if(self.PAGE_FIRST_URL == '' ) : self.get_page_url_split( page_link , False )
									rtn = True
									if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )

			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		
		
		return rtn , avaible_page_count
		
		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	def get_product_data(self, page_url, html):
		rtn = False
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
			
		if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : 
			product_link_list = soup.select(self.C_PRODUCT_VALUE)
			if( len(product_link_list) == 0 ) : product_link_list = soup.select(self.C_PRODUCT_VALUE_2)
			
		__LOG__.Trace('product list : %d' % len(product_link_list) )
		for product_ctx in product_link_list :
			
			ul_list = product_ctx.find_all('ul',class_='prdList grid4')
			for ul_ctx in ul_list :
				li_ctx = ul_ctx.find('li')
				if(li_ctx != None) : 
					img_list = li_ctx.find_all('div', class_='thumbnail' )
					name_list = li_ctx.find_all('strong', class_='name' )
					price_list = li_ctx.find_all('li', class_='price' )
					idx = 0
					for img_ctx in img_list :
						self.set_product_data( page_url, soup, img_ctx, name_list[idx], price_list[idx] )
						idx += 1
	
		
		return rtn
		
		
	def set_product_data(self , page_url, soup, img_ctx, name_ctx, price_ctx ) :
		
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
			# <a href="/shop/shopdetail.html?branduid=624477&amp;xcode=032&amp;mcode=002&amp;scode=&amp;type=X&amp;sort=manual&amp;cur_code=032&amp;GfDT=Z213UQ%3D%3D"><img class="MS_prod_img_s" src="/shopimages/lovespet/0320020000533.gif?1590117644" alt=""></a>
			#
			####################################


			img_list = img_ctx.find_all('img')
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
			# 상품명 및 브랜드
			#
			# <strong class="name"><a href="/shop/shopdetail.html?branduid=624477&amp;xcode=032&amp;mcode=002&amp;scode=&amp;type=X&amp;sort=manual&amp;cur_code=032&amp;GfDT=Z213UQ%3D%3D">도기스타 쿨하네스 ( S ~ XL )</a></strong>
			####################################

			product_data.crw_name = name_ctx.get_text().strip()
			product_link_ctx = name_ctx.find('a')
			if( product_link_ctx != None) :
				if('href' in product_link_ctx.attrs ) : 
					crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
					if(crw_post_url != '') :
						self.get_crw_goods_code( product_data, crw_post_url )
						self.get_category_value( product_data, crw_post_url )



			####################################
			# 가격 / 품절 여부 확인
			#
			# <li class="price">
			# <p class="price02"><strike>₩24,000</strike></p>
			# <p class="price03">₩24,000</p>
			# </li>
			#
			# ---- 품절시 ------
			# <li class="price">
			# <div class="sold">[품절상품]</div>
			# </li>
			####################################
			
			sell_ctx = price_ctx.find('p', class_='price03')
			consumer_ctx = price_ctx.find('p', class_='price02')
			soldout_ctx = price_ctx.find('div', class_='sold')
			if( soldout_ctx != None ) : product_data.crw_is_soldout = 1
				
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
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	
	
	