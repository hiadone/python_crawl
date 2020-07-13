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
		
		
		self.SITE_HOME = 'https://www.howlpot.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#header > div.lnb_wrap > div > div.inner > div.category > div.shop_hover > div > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['전체보기']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#big_section > ul.paging > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#big_section > ul.prd_basic.col4 > li > div'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '?page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
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
			# 상품 카테고리 추출
			####################################
			div_list = soup.find_all( 'div' , class_='cntbody' )
			for div_ctx in div_list :				
				category_list = div_ctx.find_all( 'h2', class_='subtitle' )
				for category_ctx in category_list :
					product_data.crw_category1 = category_ctx.get_text().strip()
	

			'''			
			####################################
			# 브랜드 추출	
			####################################
			brand_div_list = product_ctx.find_all('span', class_='item_brand')
			for brand_ctx in brand_div_list :
				brand_name = brand_ctx.get_text().strip()
				if( brand_name != '') : product_data.crw_brand1 = brand_name.replace('[','').replace(']','').strip()
			'''
			
			####################################				
			# 상품 이미지 확인
			#
			# <div class="prdimg"><a href="https://www.howlpot.com/shop/detail.php?pno=41AE36ECB9B3EEE609D05B90C14222FB&amp;rURL=https%3A%2F%2Fwww.howlpot.com%2Fshop%2Fbig_section.php%3Fcno1%3D1037&amp;ctype=1&amp;cno1=1037"><img src="https://howlpotdesign.wisacdn.com/_data/product/d0dcc887757a47bd539823e77b7a3da6.jpg" width="292" height="292"></a></div>
			#
			####################################

			img_div_list = product_ctx.find_all('div', class_='prdimg')
			for img_div_ctx in img_div_list :
				img_list = img_div_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )


			####################################
			# 품절여부 추출
			# 품절시 <div class="box out"> 으로 표현됨
			#
			# <div class="box out">
			# <div class="no">03</div>
			# <div class="img">
			# 생략
			# </div>
			# <div class="info">
			# 생략
			# </div>
			# </div>
			#
			####################################
			
			if('class' in product_ctx.attrs ) :
				class_name_list = product_ctx.attrs['class']
				if( len(class_name_list) == 2 ) :
					if(class_name_list[1] == 'out') : product_data.crw_is_soldout = 1
	

			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="name">
			# <a href="https://www.howlpot.com/shop/detail.php?pno=41AE36ECB9B3EEE609D05B90C14222FB&amp;rURL=https%3A%2F%2Fwww.howlpot.com%2Fshop%2Fbig_section.php%3Fcno1%3D1037&amp;ctype=1&amp;cno1=1037">메모리폼_라이트 그레이</a>
			# <span class="wish"><a href="#" onclick="wishPartCartAjax(&quot;41AE36ECB9B3EEE609D05B90C14222FB&quot;, this); return false;">관심상품 담기</a></span>
			# </div>
			# 
			####################################
			name_strong_list = product_ctx.find_all('div', class_='name')
			for name_strong_ctx in name_strong_list :
				product_link_ctx = name_strong_ctx.find('a')
				if(product_link_ctx != None) :
					#__LOG__.Trace( product_link_ctx )
					if('href' in product_link_ctx.attrs ) : 
						product_data.crw_name = product_link_ctx.get_text().strip()

						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
						split_list = crw_post_url.split('?pno=')
						second_split_list = split_list[1].split('&')
						product_data.crw_goods_code = second_split_list[0].strip()
			

			####################################
			# 가격
			#
			# <div class="price">
			# <span class="sell"><span class="font">98,000</span></span>
			# </div>
			#
			####################################
			
			div_list = product_ctx.find_all('div', class_='price')
			for div_ctx in div_list :
				sell_ctx = div_ctx.find('span', class_='sell')
				consumer_ctx = div_ctx.find('span', class_='consumer')
				if( consumer_ctx != None ) : 
					product_data.crw_price = int( __UTIL__.get_only_digit( consumer_ctx.get_text().strip() ) )
					
				if( sell_ctx != None ) : 
					# 타임세일일때  뒷부분의 별도의 값이 붙어서, 값 이상 문제 해결법, 
					crw_price_sale = sell_ctx.get_text().strip().split('\n')
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale[0].strip() ))
					
			
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
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''

	def get_product_detail_data(self, product_data, html):
		rtn = False
		try :

			detail_page_txt = []
			detail_page_img = []
			
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			table_list = soup.select('#detail > form > div > div.info > table')
			
			crw_brand = []
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )	
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			
			self.set_detail_brand( product_data, crw_brand )
			
			# 제품 상세 부분

			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#detail > div > div.tabcnt_detail.tabcnt_detail0 > div.detail_info', '', 'src' )

			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	
	
	