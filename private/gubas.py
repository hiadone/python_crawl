#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- 상세페이지의 상세설명부분이 API 질의로 별도로 갖고 와야함.

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
			
		self.SITE_HOME = 'https://gubas.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#layout_topBar > div.wrap_inner.relative > ul > li > div > ul > li > div > ul > li > a'
		self.C_CATEGORY_VALUE_2 = '#layout_topBar > div.wrap_inner.relative > ul > li > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['50% 반값 할인!','단종 제품 할인','촬영용/B급상품']
		self.C_CATEGORY_STRIP_STR = ''

		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#layout_config_full > div.paging_navigation.mt0 > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#layout_config_full > div > div.displayTabContentsContainer.displayTabContentsA > ul > li > div'
		self.C_PRODUCT_STRIP_STR = './'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '?page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
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
	
	
		
	def get_product_detail_data(self, product_data, html):
		rtn = False
		try :
			
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')

			dl_list = soup.select('#goods_view > dl > dd > form > ul > li > div > dl')
			rtn_dict = self.get_value_in_dl_dtdd( dl_list)
			for key in rtn_dict :
				if(0 <= key.find('제조자') ) or (0 <= key.find('제조국') ) or (0 <= key.find('브랜드')) or (0 <= key.find('원산지') ) : crw_brand.append( rtn_dict[key].strip() )
			self.set_detail_brand( product_data, crw_brand )
			
			self.get_product_detail_data_sub(product_data )

			
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
			
			category_ctx_list = soup.select('#layout_config_full > div.category_depth.clearbox > ul')			
			for category_ctx in category_ctx_list :
				a_ctx_list = category_ctx.get_text().strip().split('>')
				idx = 0
				for a_ctx in a_ctx_list :
					idx += 1
					category_name = a_ctx.strip()
					if(idx == 2 ) : product_data.crw_category1 = category_name
					elif(idx == 3 ) : product_data.crw_category2 = category_name
					elif(idx == 4 ) : product_data.crw_category3 = category_name
					
			#product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
			
			
			####################################				
			# 상품 이미지 확인 / 상품 링크 정보 / 상품번호
			#
			# <a href="javascript:void(0)" onclick="display_goods_view('196','',this,'goods_view')"><span style="color:#000000;font-weight:normal;text-decoration:none;" class="goods_name">강아지 목줄/3M리드줄세트 <br>콤비네이션_베이지브라운</span></a>
			####################################

			span_list = product_ctx.find_all('div', class_='goodsDisplayImageWrap')
			for span_ctx in span_list :
				product_link_ctx = span_ctx.find('a')
				if( product_link_ctx != None ) :
					if('onclick' in product_link_ctx.attrs ) : 
						split_list = product_link_ctx.attrs['onclick'].split('display_goods_view(')
						sub_split_list = split_list[1].split(',')
						product_data.crw_goods_code = sub_split_list[0].replace("'","").strip()
						
						tmp_product_link = self.SITE_HOME + '/goods/view?no=' + product_data.crw_goods_code
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, span_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link
						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						
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
			# <span style="color:#000000;font-weight:normal;text-decoration:none;" class="goods_name">강아지 목줄 <br>콤비네이션_옐로우레드</span>
			####################################
			name_div_ctx = product_ctx.find('span', class_='goods_name')
			if( name_div_ctx != None) :
				product_data.crw_name = name_div_ctx.get_text().replace('\n',' ').strip()
	
	

			####################################
			# 가격
			#
			# <li>
			# <span class="price_txt">판매가</span>
			# <span style="color:#777777;font-weight:normal;text-decoration:line-through;" class="sale_price">
			# 15,000							</span>
			# </li>
			#
			####################################
			
			li_list = product_ctx.find_all('li')
			for li_ctx in li_list :
				title_ctx = li_ctx.find('span', class_='price_txt')
				value_ctx = li_ctx.find('span', class_='sale_price')
				if(title_ctx != None) and (value_ctx != None) :
					title_name = title_ctx.get_text().strip()
					title_value = value_ctx.get_text().strip()
					if( title_name == '판매가' ) : product_data.crw_price = int( __UTIL__.get_only_digit( title_value ) )
					elif( title_name == '이벤트가' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( title_value ) )
	

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
		
	'''	
	#################################################################################
	##
	##	상품 상세페이지의 내용을 갖고 오는 API
	##  return 값은 html 부분으로 넘겨준다.

	Request URL: https://dog114.kr/goods/view_contents?no=234&setMode=pc&zoom=1
	Request Method: GET
	Status Code: 200 OK
	Remote Address: 121.78.114.152:443
	Referrer Policy: no-referrer-when-downgrade
	Cache-Control: no-store, no-cache, must-revalidate
	Cache-Control: post-check=0, pre-check=0
	Connection: Keep-Alive
	Content-Encoding: gzip
	Content-Length: 245
	Content-Type: text/html; charset=UTF-8
	Date: Wed, 10 Jun 2020 07:37:00 GMT
	Expires: Mon, 26 Jul 1997 05:00:00 GMT
	Keep-Alive: timeout=5, max=94
	Last-Modified: Wed, 10 Jun 2020 07:37:00 GMT
	P3P: CP="ALL CURa ADMa DEVa TAIa OUR BUS IND PHY ONL UNI PUR FIN COM NAV INT DEM CNT STA POL HEA PRE LOC OTC"
	Pragma: no-cache
	Server: Apache
	Set-Cookie: mobileapp=N; expires=Thu, 10-Jun-2021 07:37:00 GMT; path=.firstmall.kr
	Vary: Accept-Encoding
	Accept: */*
	Accept-Encoding: gzip, deflate, br
	Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6
	Connection: keep-alive
	Cookie: mobileapp=N; PHPSESSID=f038940c3210da5411725e0667e84a55; visitorInfo=a%3A2%3A%7Bs%3A4%3A%22date%22%3Bs%3A10%3A%222020-06-10%22%3Bs%3A7%3A%22referer%22%3BN%3B%7D; today_view=a%3A3%3A%7Bi%3A0%3Bi%3A630%3Bi%3A1%3Bi%3A1129%3Bi%3A2%3Bi%3A234%3B%7D
	Host: dog114.kr
	Referer: https://dog114.kr/goods/view?no=234
	Sec-Fetch-Dest: empty
	Sec-Fetch-Mode: cors
	Sec-Fetch-Site: same-origin
	User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36
	X-Requested-With: XMLHttpRequest
	no: 234
	setMode: pc
	zoom: 1

	<p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><br></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><img class="txc-image" style="clear: none; float: none;" src="/data/editor/temp_13803546344354.jpg"></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><br></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><img class="txc-image" style="clear: none; float: none;" src="/data/editor/temp_13803546800986.jpg"></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><br></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><img class="txc-image" style="clear: none; float: none;" src="/data/editor/temp_13803546885006.jpg"></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><br></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><img class="txc-image" style="clear: none; float: none;" src="/data/editor/temp_13803546939599.jpg"></p><p style="text-align: center; color: rgb(0, 0, 0); line-height: 19px; font-family: 나눔고딕; font-size: 13px;"><br></p>
	#################################################################################
	'''

	def get_product_detail_data_sub_data(self, product_data, detail_html):
		rtn = False
		try :
			detail_page_txt = []
			detail_page_img = []
			
			innerhtml = '''<div>''' + detail_html + '''</div>'''
			detail_page_img = self.get_image_data_innerhtml(innerhtml)
			
			detail_page_txt = self.get_text_data_innerhtml(innerhtml)
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex :
			__LOG__.Error( "get_product_detail_data_sub_data - Error")
			__LOG__.Error( ex)
			pass
	
		
	def get_product_detail_data_sub(self, product_data ): 

		res =  None
		rtn = False
		

		try :
			site_home_list = self.SITE_HOME.replace('https://','').replace('http://','').split('/')
			site_home = site_home_list[0]
			
			header = { 'Accept': '*/*' , \
					'Accept-Encoding': 'gzip, deflate, br' , \
					'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
					'Connection': 'keep-alive' , \
					'Cookie': self.COOKIE_STR , \
					'Host': site_home , \
					'Referer': product_data.crw_post_url , \
					'User-Agent': self.USER_AGENT, \
					'X-Requested-With': 'XMLHttpRequest' } 
					
			URL = 'https://gubas.co.kr/goods/view_contents?no=%s&setMode=pc&zoom=1' % ( product_data.crw_goods_code)
		
			res = requests.get(URL, headers=header)
			if(res.status_code != 200) : __LOG__.Error( res.status_code )
			else: 
				self.get_product_detail_data_sub_data(product_data, res.text)

		except Exception as ex :
			__LOG__.Error( 'get_product_detail_data_sub' )
			__LOG__.Error( ex)
			pass

		
	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()

	
	
	
	