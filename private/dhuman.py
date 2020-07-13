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

		self.SITE_HOME = 'http://www.dhuman.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		self.C_CATEGORY_VALUE = '#gnb > div > ul.gnb > li > a.gnbDep1'
		self.C_CATEGORY_IGNORE_STR = ['듀먼 후기','이벤트/혜택','브랜드 스토리']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		#self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_PAGE_TYPE = ''
		#self.C_PAGE_VALUE = '#container > div > ul.pagination > li > a'
		#self.C_PAGE_STRIP_STR = '../'
		
		#self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		#self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#contents > div > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		#self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_LAST_PAGE_TYPE = ''
		#self.C_LAST_PAGE_VALUE = '#container > div > ul.pagination > li.last > a'
		
		#self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		#self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		#self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		
	'''
	#
	#
	#
	'''
	
	def get_category_data(self, html):
		rtn = False
		
		self.set_param_category(html)
		
		category_link_list = []
		category_link_list_2 = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)

		for category_ctx in category_link_list :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

						category_link = tmp_category_link
						
						if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
						
						category_name = category_ctx.get_text().strip()
						if( category_link.find('#showMenu') < 0 ) :		
							# 메뉴보이기는 삭제..- 메뉴이름이 없어서 URL을 직접 체크
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
		
	
	#def set_param_product(self, html) :
	#	__LOG__.Trace(html)
	
	def process_page(self, category_url):
	
		rtn = False
		
		try :

			# 첫 페이지를 추가함.
			self.PAGE_URL_HASH[category_url] = self.CATEGORY_URL_HASH[category_url]
			rtn = True
			
		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
		
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
			
			dl_list = soup.select('#contents > div.prdtDtlSum > div.prdtDtlSumRight > div.pdInfoArea > div.prdtInfoWrap > dl')
			rtn_dict = self.get_value_in_dl_dtdd(dl_list)
			if('제조사/원산지' in rtn_dict ) : 
				if( rtn_dict['제조사/원산지'].find('상세설명') < 0 ) : crw_brand.append( rtn_dict['제조사/원산지'].strip() )
			if('브랜드' in rtn_dict ) : 
				if( rtn_dict['브랜드'].find('상세설명') < 0 ) : crw_brand.append( rtn_dict['브랜드'].strip() )

			self.set_detail_brand( product_data, crw_brand )
			
			
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#detailInfo > div.prdtDtlCont > div', 'p', 'src' )
			
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
			
			
			product_data.crw_category1 = self.PAGE_URL_HASH[ page_url ]
	
			'''	
			####################################
			# 브랜드 추출	
			####################################
			brand_div_list = product_ctx.find_all('div', class_='brand')
			for brand_ctx in brand_div_list :
				product_data.crw_brand1 = brand_ctx.get_text().strip()
			'''
			
			####################################				
			# 상품 이미지 확인 / 품절여부 추출
			#
			# <a href="/view/product/G0OS8PKL0KAHNCUJ/YSJRQFSCH" class="itemImg" title="[맛보기초특가!] 체험팩 8종 8팩">
			# <img src="http://www.dhuman.co.kr/static-root/prdct/2020/05/13/bd1f6f76032f48329e927e9f7e727fe7.jpg" alt="[맛보기초특가!] 체험팩 8종 8팩" class="" loading="lazy">
			# <span class="discountThumb">
			# <span class="discount"><strong>50</strong>%</span>
			# </span>
			# <span class="packplayWrap">
			# <span class="pack_bg02"><span><strong class="pack_font">8</strong>팩</span></span>
			# </span>						
			# </a>
			#
			####################################
			img_div_list = product_ctx.find_all('a', class_='itemImg')
			for img_div_ctx in img_div_list :
				img_list = img_div_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )
						
				span_list = img_div_ctx.find_all('span')
				for span_ctx in span_list :
					soldout_str = span_ctx.get_text().strip()
					if( 0 <= soldout_str.find('품절')) : product_data.crw_is_soldout = 1


			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="itemTit">
			# <p class="name">
			# <a href="/view/product/G0OS8PKL0KAHNCUJ/YSJRQFSCH" title="[맛보기초특가!] 체험팩 8종 8팩">
			# [맛보기초특가!] 체험팩 8종 8팩 
			# </a>
			# </p>
			# <p class="cmnt">#휴먼그레이드 #신상체험팩</p>
			# </div>
			# 
			####################################
			
			name_div_list = product_ctx.find_all('div', class_='itemTit')
			for name_div_ctx in name_div_list :
				name_ctx = name_div_ctx.find('p', class_='name')
				if( name_ctx != None ) :
					name_link_ctx = name_ctx.find('a')
					if( name_link_ctx != None ) :
						if('href' in name_link_ctx.attrs ) : 
							product_data.crw_name = name_link_ctx.get_text().strip()
							tmp_product_link = name_link_ctx.attrs['href'].strip()
							if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, name_link_ctx.attrs['href'].strip() )
							crw_post_url = tmp_product_link

							if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
							split_list = crw_post_url.split('/')
							product_data.crw_goods_code = split_list[6].strip()


			
			
			####################################
			# 가격
			#
			# <div class="priceWrap">
			# <span class="primecost"><strong>19,900</strong></span>
			# <span class="price"><strong>9,900</strong>원</span>
			# </div>
			####################################
			
			div_list = product_ctx.find_all('div', class_='priceWrap')
			for div_ctx in div_list :
				span_list = div_ctx.find_all('span')
				for span_ctx in span_list :
					if('class' in span_ctx.attrs ) :
						class_name_list = span_ctx.attrs['class']
						if(class_name_list[0] == 'primecost' ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'price' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ))
					
			
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

	
	
	
	