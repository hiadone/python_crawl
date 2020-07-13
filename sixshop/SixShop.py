# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

- SixShop 은 상품리스트에서는 API를 사용하여 , 리스트를 갖고 옴
  API 의 Key 값이 수시로 변경되는 값으로 판단되어,
  Selenium 을 통해서 Chrome headless 가상브라우저를 띄워 데이터를 추출한다.
  
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

from selenium.webdriver.common.by import By
# WebDriverWait Selenium 2.4.0 
from selenium.webdriver.support.ui import WebDriverWait
# expected_conditions Selenium 2.26.0 
from selenium.webdriver.support import expected_conditions as EC

import log as Log;  Log.Init()
from app import config
from app import define_mall as __DEFINE__
from util import Util as __UTIL__

from model.ProductData import ProductData
from mall.Mall import Mall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class SixShop(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)
		
		self.SITE_ORG_HOME = ''		# 처음 접속하는 사이트 URL
	
	
		
	def get_category_data_default_sixshop(self, html):
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
			if(self.C_CATEGORY_VALUE_2.strip() != '') : category_link_list_2 = soup.select(self.C_CATEGORY_VALUE_2)

		for category_ctx in category_link_list :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('productlistfilter' in category_ctx.attrs ) : 
						category_link = category_ctx.attrs['productlistfilter']						
						category_name = category_ctx.get_text().strip()
						if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
							self.CATEGORY_URL_HASH[category_link] = category_name
							if( config.__DEBUG__ ) :
								__LOG__.Trace('%s : %s' % ( category_name, category_link ) )

							rtn = True

			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		for category_ctx in category_link_list_2 :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('productlistfilter' in category_ctx.attrs ) : 
						category_link = category_ctx.attrs['productlistfilter']
						category_name = category_ctx.get_text().strip()
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


		
	'''
	######################################################################
	#
	# 카테고리별 페이지 URL을 추출할 필요가 없음.
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''	
	def process_page_list(self) :
	
		return True
		
	'''
	######################################################################
	#
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''
	
	def get_product_data(self, category_key, html):
		self.get_product_data_default_sixshop( category_key, html )
		
	def process_product(self, category_key):
		self.process_product_default_sixshop( category_key )
	
	def get_product_data_default_sixshop(self, category_key, html):
		rtn = True
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		div_list = soup.find_all('div')
		for div_ctx in div_list :
			if('class' in div_ctx.attrs) :
				calss_name_list = div_ctx.attrs['class']
				if(calss_name_list[0] == 'productListWrapper') :
					div_str = div_ctx.get_text().strip()
					if(0 <= div_str.find('카테고리')) and (0 < div_str.find('상품')) and (0 < div_str.find('없습')) : 
						rtn = False
						break
		if(rtn) :
			if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
			
			if(config.__DEBUG__) : __LOG__.Trace('product list : %d' % len(product_link_list) )
			for product_ctx in product_link_list :
				self.set_product_data( category_key, soup, product_ctx )
		
		
		return rtn
		
	def process_product_default_sixshop(self, category_key):
	
		rtn = False
		resptext = ''
		
		try :
			page = 1
			is_loop = True
			while(is_loop) :
				try :
					if(self.SHUTDOWN) : break
					page_url = '%s?productListPage=%d&productListFilter=%s' % ( self.BASIC_PAGE_URL, page, category_key)
					page += 1
					__LOG__.Trace('page : %s' % ( page_url ) )
						
					time.sleep(self.WAIT_TIME)
					self.browser.get(page_url)

					title = WebDriverWait(self.browser, self.WAIT_TIME*10) \
						.until(EC.presence_of_element_located((By.CLASS_NAME, "thumbDiv")))
						
					time.sleep(2)
					resptext = self.browser.page_source
					is_loop = self.get_product_data( category_key, resptext )
				except :
					is_loop = False
					pass
			
		except Exception as ex:
			__LOG__.Error( "process_product Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
	
	'''
	######################################################################
	#
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''
	def get_product_data_second_sixshop(self, category_key, html):
		rtn = True
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
		
		if(config.__DEBUG__) : __LOG__.Trace('product list : %d' % len(product_link_list) )
		for product_ctx in product_link_list :
			self.set_product_data( category_key, soup, product_ctx )
		
		
		return rtn
		
		
	def process_product_second_sixshop(self, category_key):
	
		rtn = False
		resptext = ''
		
		try :

			page_url = category_key
			__LOG__.Trace('page : %s' % ( page_url ) )
				
			time.sleep(self.WAIT_TIME)
			self.browser.get(page_url)

			title = WebDriverWait(self.browser, self.WAIT_TIME*10) \
				.until(EC.presence_of_element_located((By.CLASS_NAME, "thumbDiv")))
				
			time.sleep(2)
			resptext = self.browser.page_source
			is_loop = self.get_product_data( category_key, resptext )
			
			
		except Exception as ex:
			__LOG__.Error( "process_product Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn	
		
	def process_product_list(self):

		__LOG__.Trace("********** process_product_list ***********")
		
		rtn = False
		resptext = ''
		try :
			self.browser_init(self.SITE_HOME)
			
			self.PRODUCT_URL_HASH = None
			self.PRODUCT_URL_HASH = {}
			if( config.__DEBUG__ ) :
				__LOG__.Trace( self.C_PRODUCT_CASE )
				__LOG__.Trace( self.C_PRODUCT_VALUE )
				
			for category_key in self.CATEGORY_URL_HASH.keys() :
				if(self.SHUTDOWN) : break
				self.process_product( category_key )
				
			self.quit()
			
		except :
			pass
		finally :
			self.quit()
			
		if(config.__DEBUG__) : __LOG__.Trace( '총 물품 수 : %d' % len(self.PRODUCT_URL_HASH))
		
		__LOG__.Trace("*************************************************")	
		
		return rtn

		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	
	def get_category_value(self, product_data, category_key, soup ) :
	
		if(self.CATEGORY_URL_HASH.get( category_key , -1) != -1) : product_data.crw_category1 = self.CATEGORY_URL_HASH[category_key]

	
	
	def set_product_data(self , category_key, soup, product_ctx ) :
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			
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
			img_div_list = product_ctx.find_all('div', class_='thumb img')
			for img_div_ctx in img_div_list :
				if('style' in img_div_ctx.attrs ) :
					tmp_img_src = img_div_ctx.attrs['style'].strip()
					split_list = tmp_img_src.split(':url(')
					img_src = split_list[1].replace(')','')
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )

							
			
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
				if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
				
					self.set_product_data_sub( product_data, crw_post_url )
			
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
	# 
	#
	#
	######################################################################
	'''
	def get_detail_brand_data(self, product_data, html):
		#
		#
		# 상세페이지 부분에서 브랜드 데이터 갖고 오기
		#
		#<script type='application/ld+json'>{"@context":"http:\/\/schema.org","@type":"Product","name":"Raglan T-shirt #mint","image":["https:\/\/cdn.imweb.me\/thumbnail\/20200512\/6ca1480c2e3ad.jpg"],"description":"\ucc38\uace0\uc0ac\ud56d\uc81c\ud488\uc758 \uc0c9\uc0c1\uc740 \uc2e4\ub0b4 \ubc0f \uc2e4\uc678\uc5d0\uc11c \ucc28\uc774\uac00 \uc788\uc744 \uc218 \uc788\uc2b5\ub2c8\ub2e4.\ub098\ub098 NANA \ucc29\uc6a9\uc0ac\uc774\uc988 - M\ub85c\ub2c8 RONI \ucc29\uc6a9\uc0ac\uc774\uc988 - M\uc0c1\ud488 \uc0ac\uc774\uc988\ud45c\uc0ac\uc774\uc988\ub294 \uce21\uc815 \ubc29\ubc95\uc5d0 \ub530\ub77c &plusmn;1-2cm \uc624\ucc28\uac00 ... ","brand":{"@type":"Brand","name":"Hipaw"},"offers":{"@type":"Offer","price":32000,"priceCurrency":"KRW","url":"http:\/\/hipaw.co.kr\/shop_view\/?idx=28","availability":"http:\/\/schema.org\/InStock"},"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0000","reviewCount":"3"}}</script>
		crw_brand = []
		
		# html에서 json data를 얻어옴
		jsondata = self.get_json_data_innerhtml(html, '<script type="application/ld+json">', '</script>')
		for key in jsondata :
			if('brand' in jsondata) : 
				crw_brand.append( jsondata['brand'].strip() )
				break

		self.set_detail_brand( product_data, crw_brand )

	


	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''	
	def get_product_detail_data(self, product_data, html):
		self.get_product_detail_data_sixshop( product_data, html, '#productDescriptionDetailPage', 'p', 'src')
	
	def get_product_detail_data_sixshop(self, product_data, html, content_selector, text_sub_selector, img_attr, img_selector='img'):
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []
			
			self.get_detail_brand_data(product_data, html)
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			#detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#productDescriptionDetailPage', 'p', 'src' )
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, content_selector, text_sub_selector, img_attr, img_selector )
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	