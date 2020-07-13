#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항

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
			
		self.SITE_HOME = 'http://shop.i-avec.com'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#gnb_1dul > li > a'
		self.C_CATEGORY_IGNORE_STR = ['렌탈 서비스']
		self.C_CATEGORY_STRIP_STR = ''

		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#sct > nav > span > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#sct > ul > li.sct_li'
		self.C_PRODUCT_STRIP_STR = './'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#sct > nav > span > a'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
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

			table_list = soup.select('#sit_ov > div.sit_info > table')
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			for key in rtn_dict :
				if(0 <= key.find('제조자') ) or (0 <= key.find('제조국') ) or (0 <= key.find('브랜드')) or (0 <= key.find('원산지') ) : crw_brand.append( rtn_dict[key].strip() )
			self.set_detail_brand( product_data, crw_brand )
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#sit_inf_explan', 'p', 'src' )
			
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
			
			#__LOG__.Trace( '--------------------------------------' )
			#__LOG__.Trace( product_ctx )
			
			product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
			
			
			####################################				
			# 상품 이미지 확인
			#
			# <div class="sct_img">
			# <a href="http://shop.i-avec.com/shop/item.php?it_id=1585815848">
			# <img src="http://shop.i-avec.com/data/item/1585815848/thumb-7KCE7ZW07IiY6riw_front_310x310.png" width="310" height="310" alt="아베크 전해수기 뿌조" title="">
			# </a>
			# <div class="sct_sns"><a href="https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Fshop.i-avec.com%2Fshop%2Fitem.php%3Fit_id%3D1585815848&amp;p=%EC%95%84%EB%B2%A0%ED%81%AC+%EC%A0%84%ED%95%B4%EC%88%98%EA%B8%B0+%EB%BF%8C%EC%A1%B0+%7C+%EC%95%84%EB%B2%A0%ED%81%AC+%ED%8E%AB%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%A3%B8-%ED%8E%AB+%EC%82%B4%EA%B7%A0+%ED%86%A0%ED%83%88+%EC%BC%80%EC%96%B4%EB%A3%B8" class="share-facebook" target="_blank"><img src="http://shop.i-avec.com/theme/basic/skin/shop/basic/img/facebook.png" alt="페이스북에 공유"></a><a href="https://twitter.com/share?url=http%3A%2F%2Fshop.i-avec.com%2Fshop%2Fitem.php%3Fit_id%3D1585815848&amp;text=%EC%95%84%EB%B2%A0%ED%81%AC+%EC%A0%84%ED%95%B4%EC%88%98%EA%B8%B0+%EB%BF%8C%EC%A1%B0+%7C+%EC%95%84%EB%B2%A0%ED%81%AC+%ED%8E%AB%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%A3%B8-%ED%8E%AB+%EC%82%B4%EA%B7%A0+%ED%86%A0%ED%83%88+%EC%BC%80%EC%96%B4%EB%A3%B8" class="share-twitter" target="_blank"><img src="http://shop.i-avec.com/theme/basic/skin/shop/basic/img/twitter.png" alt="트위터에 공유"></a><a href="https://plus.google.com/share?url=http%3A%2F%2Fshop.i-avec.com%2Fshop%2Fitem.php%3Fit_id%3D1585815848" class="share-googleplus" target="_blank"><img src="http://shop.i-avec.com/theme/basic/skin/shop/basic/img/gplus.png" alt="구글플러스에 공유"></a></div>
			# </div>
			#
			####################################
			
			span_list = product_ctx.find_all('div', class_='sct_img')
			for span_ctx in span_list :
				product_link_ctx = span_ctx.find('a')
				if( product_link_ctx != None ) :
					img_list = product_link_ctx.find_all('img')
					for img_ctx in img_list :
						img_src = ''
						if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
						elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
							
						if( img_src != '' ) :
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							product_data.product_img = self.get_hangul_url_convert( img_link )

			####################################
			# 품절여부
			#
			# <div class="sct_icon"><span class="sit_icon"><br><span class="shop_icon_soldout">Sold Out</span></span></div>
			####################################
			name_div_list = product_ctx.find_all('div', class_='sct_icon')
			for name_div_ctx in name_div_list :			
				soldout_ctx = name_div_ctx.find('span', class_='shop_icon_soldout')
				if( soldout_ctx != None) : product_data.crw_is_soldout = 1
				
				
			####################################
			# 상품명 / 상품 링크 정보 / 상품번호
			#
			# <div class="sct_txt"><a href="http://shop.i-avec.com/shop/item.php?it_id=1585815848">
			# 아베크 전해수기 뿌조
			# </a></div>
			####################################
			name_div_ctx = product_ctx.find('div', class_='sct_txt')
			if( name_div_ctx != None) :
				product_link_ctx = name_div_ctx.find('a')
				if( product_link_ctx != None ) :
					if('href' in product_link_ctx.attrs ) : 
						product_data.crw_name = product_link_ctx.get_text().strip()
						
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?it_id=')
						sub_split_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = sub_split_list[0]

	
	

			####################################
			# 가격
			#
			# <div class="sct_cost">
			# <span class="sct_discount">70,000원</span>
			# 62,900원
			#</div>
			####################################

			price_ctx = product_ctx.find('div', class_='sct_cost')
			if(price_ctx != None) : 
				price_discount_ctx = product_ctx.find('span', class_='sct_discount')
				if(price_discount_ctx != None) : 
					product_data.crw_price = int( __UTIL__.get_only_digit( price_discount_ctx.get_text().strip() ) )
					len_price_str = len(price_discount_ctx.get_text().strip())
					price_str = price_ctx.get_text().strip()
					crw_price_sale = price_str[len_price_str:].strip()
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale ) )
				else :
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( price_ctx.get_text().strip() ) )

	

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

	
	
	
	