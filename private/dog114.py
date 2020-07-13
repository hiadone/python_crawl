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

		self.SITE_HOME = 'https://dog114.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#cate > span > a
		
		self.C_CATEGORY_VALUE = '#cate > span > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		#layout_body > table > tr > td > table > tr > td > div > a
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#layout_body > table > tr > td > table > tr > td > div > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#layout_body > table > tr > td > div.designCategoryGoodsDisplay > table > tr > td'
		self.C_PRODUCT_STRIP_STR = ''
		
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

			table_list = soup.select('#goods_view > table > tr > td > form > table > tr > td > table')
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			for key in rtn_dict :
				if(0 <= key.find('제조사') ) or (0 <= key.find('브랜드') ) or (0 <= key.find('원천사') ) :
					__LOG__.Trace('%s : %s' % (key, rtn_dict[key] ))
					crw_brand.append( rtn_dict[key].strip() )
			#if('브랜드' in rtn_dict ) : crw_brand.append( rtn_dict['브랜드'].strip() )
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
			
			####################################
			# 상품 카테고리
			####################################
			div_list = soup.find_all('div', class_='category_depth clearbox')
			for div_ctx in div_list :
				li_list = div_ctx.find_all('li')
				for li_ctx in li_list :
					
					if('class' in li_ctx.attrs) :
						category_link = li_ctx.find('a')
						if( category_link != None ) : product_data.crw_category1 = category_link.get_text().strip()
	
			'''	
			####################################
			# 브랜드 추출	
			####################################
			'''

			
			####################################				
			# 상품 이미지 확인 / 상품 링크 정보 / 상품번호
			#
			# <a href="/goods/view?no=792" target="">
			# <img src="/data/goods/201606/792_18171332list2.jpg" width="130" onerror="this.src='/data/skin/0545blueface/images/common/noimage.gif';this.style.height='130px';">
			# </a>
			####################################
			
			span_list = product_ctx.find_all('span', class_='goodsDisplayImageWrap')
			for span_ctx in span_list :
				product_link_ctx = span_ctx.find('a')
				if( product_link_ctx != None ) :
					if('href' in product_link_ctx.attrs ) : 
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?no=')
						product_data.crw_goods_code = split_list[1].strip()
					
					img_list = product_link_ctx.find_all('img')
					for img_ctx in img_list :
						if('onerror' in img_ctx.attrs ) :
							img_src = ''
							if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
							elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
								
							if( img_src != '' ) :
								img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
								product_data.product_img = self.get_hangul_url_convert( img_link )
					

			####################################
			# 상품명
			#
			# <a href="/goods/view?no=792" target=""><span style="color:#4C4C4C;font-family:dotum;font-size:10pt;font-weight:normal;text-decoration:none;">버박 칼시데리스 칼슘영양제 (30정)</span></a>
			####################################
			name_div_list = product_ctx.find_all('a')
			for name_div_ctx in name_div_list :
				span_ctx = name_div_ctx.find('span')
				if(span_ctx != None) : product_data.crw_name = span_ctx.get_text().strip()
	
	
			
			####################################
			# 가격 / 품절여부
			#
			# <span style="color:#4C4C4C;font-family:dotum;font-size:10pt;font-weight:normal;text-decoration:line-through;">
			# 21,000
			# 원								</span>
			#
			#
			# <span style="color:#4C4C4C;font-family:dotum;font-size:10pt;font-weight:bold;text-decoration:none;">
			# 15,000
			# 원								</span>
			#
			# -------- 품절시 --------------
			# <td align="center">
			# <img src="/data/icon/goods_status/icon_list_soldout.gif">
			# </td>
			####################################
			
			div_list = product_ctx.find_all('td')
			for div_ctx in div_list :
				soldout_img_list = div_ctx.find_all('img')
				for soldout_ctx in soldout_img_list :
					if('src' in soldout_ctx.attrs ) :
						if( 0 <= soldout_ctx.attrs['src'].find('soldout') ) : product_data.crw_is_soldout = 1
						
				span_ctx = div_ctx.find('span')
				if(span_ctx != None) :
					span_str = span_ctx.get_text().strip()
					if('style' in span_ctx.attrs) :
						if(span_str != '') :
							if(span_str[0].isdigit() )  and (0 < span_str.find('원') ) : 
								if(0 < span_ctx.attrs['style'].find('text-decoration:line-through') ) : product_data.crw_price = int( __UTIL__.get_only_digit( span_str ) )
								if(0 < span_ctx.attrs['style'].find('text-decoration:none') ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_str ) )
					

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
					
			URL = 'https://dog114.kr/goods/view_contents?no=%s&setMode=pc&zoom=1' % ( product_data.crw_goods_code)
		
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

	
	
	
	