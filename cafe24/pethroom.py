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
from cafe24.Cafe24 import Cafe24


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(Cafe24) :    

	def __init__(self) :
	
		Cafe24.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://pethroom.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#navPrdList > div > ul > li > a'
		#self.C_CATEGORY_VALUE = '#navPrdList > div > h2 > a'
		#self.C_CATEGORY_IGNORE_STR = ['MY PET','ALL PRODUCTS','BEST & STEADY N',' NEW PRODUCT N','SPECIAL SET']
		self.C_CATEGORY_IGNORE_STR = ['FOR DOG','FOR CAT']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''

		
		self.C_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.ec-base-product > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME + '/product/list.html'
		self.BASIC_PRODUCT_URL = self.SITE_HOME
		self.BASIC_IMAGE_URL = self.SITE_HOME
		
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = 'div'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'prdImg'
		
		
		# 물품 SOLDOUT CSS selector 정의
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'promotion'
	
	
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''
	
	def get_category_data(self, html):
		rtn = False
		
		#__LOG__.Trace(html)
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select('#navPrdList > div.menuMid')
			#category_link_list = soup.select('#navPrdList')
		
		__LOG__.Trace('----------------------------------------------------------')
		for m_category_ctx in category_link_list :
			#__LOG__.Trace(m_category_ctx)
			try :
				idx = 0
				mid_category_list = m_category_ctx.find_all('h2')
				#__LOG__.Trace(len(mid_category_list))
				ul_list = m_category_ctx.find_all('ul', class_='snav_list')
				for ul_ctx in ul_list :
					#__LOG__.Trace(ul_ctx)
					mid_category_name = mid_category_list[idx].get_text().strip()
					idx += 1
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						category_ctx = li_ctx.find('a')
						if( category_ctx != None ) :
							if(self.check_ignore_category( category_ctx ) ) :
								if('href' in category_ctx.attrs ) : 
									tmp_category_link = category_ctx.attrs['href']
									if(tmp_category_link.find('javascript') < 0 ) :
										if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

										category_link = tmp_category_link
										
										if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
										
										category_name = category_ctx.get_text().strip()
										span_category_name = ''
										span_ctx = category_ctx.find('span')
										if(span_ctx != None) :
											span_category_name = span_ctx.get_text().strip()
											__LOG__.Trace(span_category_name)
											if(span_category_name != '') : 
												replace_span_category_name = ' %s' % ( span_category_name )
												tmp_category_name = category_name.replace(span_category_name, replace_span_category_name )
												category_name = tmp_category_name
												
										if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
											self.CATEGORY_URL_HASH[category_link] = '%s|%s' % ( mid_category_name, category_name )
											if( config.__DEBUG__ ) :
												__LOG__.Trace('%s|%s : %s' % ( mid_category_name, category_name, category_link ) )

											rtn = True


			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		
		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn

	
	def get_product_data(self, page_url, html):
		rtn = False
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		
		if(0 < page_url.find('detail.html?product_no') ) :
			# 카테고리에 일반 
			self.set_product_data_second( page_url, soup )
		else :
		
			if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
			__LOG__.Trace('product list : %d' % len(product_link_list) )
			for product_ctx in product_link_list :
				self.set_product_data( page_url, soup, product_ctx )
		
		
		return rtn
		
		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	def set_product_data_second(self , page_url, soup ) :
		
		# 
		#
		try :
			product_data = ProductData()
			
			crw_post_url = page_url
			split_list = crw_post_url.split('?product_no=')
			crw_goods_code_list = split_list[1].strip().split('&')
			product_data.crw_goods_code = crw_goods_code_list[0].strip()
						
						
			# 상품 카테고리
			#

			product_data.crw_category1 = 'PRODUCT'
			split_list = self.PAGE_URL_HASH[page_url].split('|')
			idx = 0
			for split_data in split_list :
				idx += 1
				if(idx == 1 ) : product_data.crw_category2 = split_data.strip()
				elif(idx == 2 ) : product_data.crw_category3 = split_data.strip()
				

			# 상품 이미지 확인

			img_list = soup.find_all('img', class_='BigImage')
			for img_ctx in img_list :
				if('src' in img_ctx.attrs ) :
					img_src = img_ctx.attrs['src'].strip()
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )
						
						
			p_list = soup.find_all('p', class_='prd_model')
			for p_ctx in p_list :
				if(product_data.crw_name == '' ) : product_data.crw_name = p_ctx.get_text().strip()
						
		
			# 품절여부 확인
			sold_out_ctx = soup.find('span', {'id':'btnReserve'})
			if(sold_out_ctx != None) :
				if('class' in sold_out_ctx.attrs) :
					if('displaynone' != sold_out_ctx.attrs['class'][0] ) : product_data.crw_is_soldout = 1
				else : 
					product_data.crw_is_soldout = 1

			
			# 가격
			price_list = soup.find_all('div', class_='info_price')
			for price_ctx in price_list :
				sell_ctx = price_ctx.find('span', class_='sell')
				customer_ctx = price_ctx.find('span', class_='customer')
				if(sell_ctx != None) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( sell_ctx.get_text().strip() ))
				if(customer_ctx != None) : product_data.crw_price = int( __UTIL__.get_only_digit( customer_ctx.get_text().strip() ))

			
			
			if( crw_post_url != '' ) :
				self.set_product_url_hash( product_data, crw_post_url) 
				rtn = True



		except Exception as ex:
			__LOG__.Error('에러 : set_product_data')
			__LOG__.Error(ex)
			pass
			
		return True	
		
		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			# 상품 카테고리
			#
			#self.set_product_category_first(product_data, soup)
			#__LOG__.Trace( self.PAGE_URL_HASH[page_url] )
			self.set_product_category_third(product_data, soup)
			split_list = self.PAGE_URL_HASH[page_url].split('|')
			idx = 0
			for split_data in split_list :
				idx += 1
				if(idx == 1 ) : product_data.crw_category2 = split_data.strip()
				elif(idx == 2 ) : product_data.crw_category3 = split_data.strip()
				

			# 상품 이미지 확인
			self.set_product_image_fourth(product_data, product_ctx )
			
		
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 

			crw_post_url = self.set_product_name_url_second( product_data, product_ctx , 'div', 'description')
			
			self.set_product_price_brand_second(product_data, product_ctx )
			
			
			if( crw_post_url != '' ) :
				self.set_product_url_hash( product_data, crw_post_url) 
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
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDetail > div.cont', '' )


		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	