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
			
		self.SITE_HOME = 'https://www.bodeum.co.kr/html/shop/index.php'
		
		self.SITE_ORG_HOME = 'https://www.bodeum.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		#cate > span > a
		#header > div > div.hd-menu > div > ul > li > ol > li > a
		

		self.C_CATEGORY_VALUE = '#header > div > div.hd-menu > div > ul > li > ol > li > a'
		#self.C_CATEGORY_VALUE_2 = '#header > div > div.hd-menu > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#wrapper > div > div.content > div > div > div.paging > ol > li > a'
		self.C_PAGE_STRIP_STR = '../'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#wrapper > div > div.content > div > div > div.prd-list-wrap > div > div > div > div'
		self.C_PRODUCT_STRIP_STR = './'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#wrapper > div > div.content > div > div > div.paging > p.last > a'
		
		self.PAGE_SPLIT_STR = '&PageNumber='		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME + '/html/shop/'
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME + '/html/shop/list.php'
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME + '/html/shop/'
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
		

		
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	'''
	def process_page(self, category_url):
	
		rtn = False
		
		try :

			self.PAGE_URL_HASH[category_url] = self.CATEGORY_URL_HASH[category_url]
			
			if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( category_url ) )
			rtn = True

		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
	'''	
	
	def get_product_detail_data(self, product_data, html):
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')

			table_list = soup.select('#prdDetail2 > div > div.product-info.detail-prd-content.scrollStop > table')
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			for key in rtn_dict :
				if(0 <= key.find('제조자') ) or (0 <= key.find('제조국') ) or (0 <= key.find('브랜드') ) : crw_brand.append( rtn_dict[key].strip() )
			self.set_detail_brand( product_data, crw_brand )
			
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#prdDetail2 > div > div.detail-content', '', 'src' )
			
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
			
			self.reset_product_category(product_data)
			category_ctx_list = soup.select('#menu_inner')			
			for category_ctx in category_ctx_list :
				split_list = category_ctx.get_text().strip().split('>')
				idx = 0
				for a_ctx in split_list :
					idx += 1
					category_name = a_ctx.strip()
					if(idx == 2 ) : product_data.crw_category1 = category_name
					elif(idx == 3 ) : product_data.crw_category2 = category_name
					elif(idx == 4 ) : product_data.crw_category3 = category_name
					
			#product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
			
			############################
			# 품절여부
			############################
			soldout_ctx = product_ctx.find('span', class_='soldOut')
			if( soldout_ctx != None) : product_data.crw_is_soldout = 1
			
			####################################				
			# 상품 이미지 확인
			#
			# <div class="thumbnail">
			# <div class="centered">
			# <a href="prd_detail.php?idx=171&amp;part_idx=90"><img src="/data/goodsImages/1529056838_IMAGES1.jpg" data-pin-nopin="true"></a>
			# </div> 
			# </div>
			####################################

			span_list = product_ctx.find_all('div', class_='thumbnail')
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
			# 상품명 / 상품 링크 정보 / 상품번호
			#
			# <div class="title"><a href="prd_detail.php?idx=171&amp;part_idx=90"><!--[보듬]--> 보듬 10mm 폴딩 리드줄 (길이 조절 가능)</a></div>
			####################################
			name_div_list = product_ctx.find_all('div', class_='title')
			for name_div_ctx in name_div_list :
				span_ctx = name_div_ctx.find('a')
				if(span_ctx != None) : 
					if('href' in span_ctx.attrs ) : 
						tmp_product_link = span_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, span_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?idx=')
						sub_split_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = sub_split_list[0]
						
				
					split_list = span_ctx.get_text().strip().split(']')
					crw_name = split_list[0].strip()
					if(len(split_list) == 2) : 
						product_data.crw_brand1 = split_list[0].replace('[','').strip()
						crw_name = split_list[1].strip()
					product_data.crw_name = crw_name
	
	

			####################################
			# 가격
			#
			# <div class="priceWrap">
			# <div class="saleprice"><span>119,000</span>원</div>											
			# <div class="price"><strong>101,150</strong>원</div>
			# </div>
			####################################
			
			div_list = product_ctx.find_all('div', class_='priceWrap')
			for div_ctx in div_list :
				saleprice_ctx = div_ctx.find('div', class_='saleprice')
				price_ctx = div_ctx.find('div', class_='price')
				if( saleprice_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( saleprice_ctx.get_text().strip() ) )
				if( price_ctx != None ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( price_ctx.get_text().strip() ) )
	

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

	
	
	
	