#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- 상세페이지의 상세설명부분이 API 질의로 별도로 갖고 와야함.

변경내용
	- 2020-07-07 사이트 변경됨.
	
	
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
		
		
		self.SITE_HOME = 'https://www.purplestore.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#allCategoryContainer > div > ul > li > button'
		self.C_CATEGORY_IGNORE_STR = ['주식 전체','간식 전체','용품 전체']
		self.C_CATEGORY_STRIP_STR = '..'

		
		#self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_PAGE_TYPE = ''
		#self.C_PAGE_VALUE = '#contents > div > div > div > div.paging_no > div > a'
		#self.C_PAGE_STRIP_STR = '..'
		
		#self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		#self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		#self.C_PRODUCT_VALUE = 'body > li'				# 2020-07-07 삭제
		self.C_PRODUCT_VALUE = '#saleListContainer > li'	# 2020-07-07 변경
		self.C_PRODUCT_STRIP_STR = '..'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		#self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_LAST_PAGE_TYPE = ''
		
		#self.C_LAST_PAGE_VALUE = '#contents > div > div > div > div.paging_btn > div > a'
		
		#self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		#self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		
		#self.PAGE_LAST_LINK = True		# 페이지에서 맨끝 링크 존재 여부

		
		
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
					if('data-category-id' in category_ctx.attrs ) : 
						category_link = category_ctx.attrs['data-category-id']
						
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

		
	def process_category_list(self):

		__LOG__.Trace("********** process_category_list ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.CATEGORY_URL_HASH = None
			self.CATEGORY_URL_HASH = {}
		
			URL_LIST = ['https://www.purplestore.co.kr/?tab=category&pet-type=DOG','https://www.purplestore.co.kr/?tab=category&pet-type=CAT']
			
			for URL in URL_LIST :
				time.sleep(self.WAIT_TIME)

				header = self.get_header()
				
				resp = None
				resp = requests.get( URL, headers=header , verify=False)
				
				if(self.EUC_ENCODING != None) :
					if(self.EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 EUC-KR인코딩
				else :
					resp.encoding=None								# 'ISO-8859-1'일때 인코딩
				
				if( resp.status_code != 200 ) :
					__LOG__.Error(resp.status_code)
				else :
					resptext = resp.text
					rtn = self.get_category_data( resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_category_list Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
	
	def process_page_list(self):
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
			
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			brand_ctx = soup.find('span', class_='productInfo__brand')
			if(brand_ctx != None) : crw_brand.append( brand_ctx.get_text().strip() )
			
			div_list = soup.find_all('div', class_='productSubInfo__detail-table__row')
			for div_ctx in div_list :
				title_ctx = div_ctx.find('div', class_='title')
				value_ctx = div_ctx.find('div', class_='text')
				if(title_ctx != None) and (value_ctx != None) :
					title_name = title_ctx.get_text().strip()
					title_value = value_ctx.get_text().strip()
					if(0 <= title_name.find('제조사') ) or (0 <= title_name.find('제조국') ) or (0 <= title_name.find('브랜드')) or (0 <= title_name.find('원산지') ) : 
						split_list = title_value.split('/')
						for split_data in split_list :
							if( split_data.strip() != '' ) : crw_brand.append( split_data.strip() )
			self.set_detail_brand( product_data, crw_brand )
			

			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#detailTab', '', 'src' )
			
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
	
	def get_product_data(self, category_num, html):
		is_loop = True
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		#li_list = soup.select('body > li._salePageIndicator.blind')			# 2020-07-07 삭제
		li_list = soup.select('#saleListContainer > li._salePageIndicator.blind')			# 2020-07-07 변경
		for li_ctx in li_list :
			if('data-has-next' in li_ctx.attrs ) :
				if( li_ctx.attrs['data-has-next'] == 'False') : is_loop = False
					
		if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
		__LOG__.Trace('product list : %d' % len(product_link_list) )
		if(len(product_link_list) == 0 ) : is_loop = False				# 2020-07-07 추가 , product_link_list =0 일때 무한 loop 가 발생할수 있음.
		for product_ctx in product_link_list :
			self.set_product_data( category_num, soup, product_ctx )
		
		return is_loop
		
	
	def get_header_xhr(self, category_num ):
		referer_str = 'https://www.purplestore.co.kr/products/sales/list/?type=category&value=%s' % ( category_num )
		
		header = { 'Accept': '*/*' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cookie': self.COOKIE_STR , \
			'referer': referer_str , \
			'User-Agent': self.USER_AGENT,
			'X-Requested-With': 'XMLHttpRequest'} 

		return header
		
		
	def process_product(self, category_num):
	
		rtn = False
		resptext = ''
		
		try :
		
			if( config.__DEBUG__ ) : __LOG__.Trace('category_num : %s' % ( category_num ) )
			
			page = 1
			is_loop = True
			
			while(is_loop) :
				if(self.SHUTDOWN) : break				# 2020-07-07 추가
				time.sleep(self.WAIT_TIME)
				
				#URL = 'https://www.purplestore.co.kr/products/sales/list/?type=category&value=%s&ordering=new&page=%d&range=partial' % ( category_num, page )							# 2020-07-07 삭제/ URL 변경됨.
				URL = 'https://www.purplestore.co.kr/products/sales/list/ajax?type=category&value=%s&pet_type=ALL&ordering=new&range=all&page=%d&start_page=1' % ( category_num, page )	# 2020-07-07 변경
				if(config.__DEBUG__ ) : __LOG__.Trace( URL )
				
				page += 1
				header = self.get_header_xhr(category_num)
				
				resp = None
				resp = requests.get( URL, headers=header , verify=False)
				
				
				if(self.EUC_ENCODING != None) :
					if(self.EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 EUC-KR인코딩
				else :
					resp.encoding=None								# 'ISO-8859-1'일때 인코딩
				
				
				if( resp.status_code != 200 ) :
					__LOG__.Error(resp.status_code)
					is_loop = False
				else :
					resptext = resp.text
					is_loop = self.get_product_data( category_num, resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_product Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
		
		
	def process_product_list(self):

		__LOG__.Trace("********** process_product_list ***********")
		
		rtn = False
		resptext = ''
		
		self.PRODUCT_URL_HASH = None
		self.PRODUCT_URL_HASH = {}
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_PRODUCT_CASE )
			__LOG__.Trace( self.C_PRODUCT_VALUE )
			
		for category_num in self.CATEGORY_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			self.process_product( category_num )
		
		if(config.__DEBUG__) : __LOG__.Trace( '총 물품 수 : %d' % len(self.PRODUCT_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn
	
	
	def set_product_data(self , category_num, soup, product_ctx ) :
		
		# 
		#
		is_loop = True
		try :
			product_data = ProductData()
			crw_post_url = ''

			product_data.crw_category1 = self.CATEGORY_URL_HASH[category_num]
			
			
			####################################				
			# 상품 이미지 확인
			#
			# <div class="saleCard__area-img"><i class="saleCard__badge--new"><svg height="33" viewBox="0 0 33 33" width="33" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><circle cx="16.5" cy="16.5" fill="#3E0A7D" r="16" stroke="#FFF"></circle><path d="M15.38 19.37v-6.71h-1.33v6.71h1.33zm-7.01-1.23c.54-.187.99-.458 1.35-.815.36-.357.647-.768.86-1.235.2.433.475.813.825 1.14.35.327.782.577 1.295.75l.67-1.05a3.308 3.308 0 0 1-.965-.48c-.27-.2-.492-.427-.665-.68a2.796 2.796 0 0 1-.385-.82 3.242 3.242 0 0 1-.125-.89v-.9H9.89v.9c0 .307-.042.612-.125.915-.083.303-.215.59-.395.86A3.183 3.183 0 0 1 7.7 17.09l.67 1.05zm7.24 3.56v-1.05h-5.04v-1.92H9.25v2.97h6.36zm8.57-3.6v-2.22h1.22v-1.09h-1.22v-2.13h-1.32v5.44h1.32zm-6.7-.09c.527-.18.968-.44 1.325-.78s.635-.74.835-1.2c.193.393.458.738.795 1.035a3.49 3.49 0 0 0 1.235.685l.69-1.02a3.426 3.426 0 0 1-.935-.445 2.538 2.538 0 0 1-1.015-1.375c-.08-.267-.12-.54-.12-.82v-.94h-1.34v.83c0 .313-.04.622-.12.925-.08.303-.207.587-.38.85-.173.263-.397.5-.67.71-.273.21-.603.378-.99.505l.69 1.04zm3.69 3.85c.48 0 .912-.04 1.295-.12.383-.08.71-.197.98-.35.27-.153.477-.34.62-.56.143-.22.215-.47.215-.75s-.072-.528-.215-.745a1.774 1.774 0 0 0-.62-.555 3.376 3.376 0 0 0-.98-.35 6.365 6.365 0 0 0-1.295-.12c-.48 0-.913.04-1.3.12-.387.08-.715.197-.985.35-.27.153-.477.338-.62.555a1.32 1.32 0 0 0-.215.745c0 .28.072.53.215.75.143.22.35.407.62.56.27.153.598.27.985.35.387.08.82.12 1.3.12zm0-1.02c-.593 0-1.043-.062-1.35-.185-.307-.123-.46-.315-.46-.575 0-.253.153-.442.46-.565.307-.123.757-.185 1.35-.185.587 0 1.033.062 1.34.185.307.123.46.312.46.565 0 .26-.153.452-.46.575-.307.123-.753.185-1.34.185z" fill="#FFF" fill-rule="nonzero"></path></g></svg></i><div class="saleCard__area-badge"></div><img alt=" 주식캔 no.6 캥거루 200g" class="saleCard__img--no-bg" src="https://cdn.purplesto.re/media/store/sale/main_image/dogzfinefood_dog_B052DF21_thumb01.png"></div>
			####################################
			
			span_list = product_ctx.find_all('div', class_='saleCard__area-img')
			for span_ctx in span_list :
				img_list = span_ctx.find_all('img', class_='saleCard__img--no-bg')
				if(len(img_list) == 0) : img_list = span_ctx.find_all('img', class_='saleCard__img--concept')
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
			# <div class="saleCard__area-price"><p class="saleCard__price--new">Sold Out</p></div>
			####################################
			name_div_list = product_ctx.find_all('div', class_='saleCard__area-price')
			for name_div_ctx in name_div_list :			
				soldout_ctx = name_div_ctx.find('p', class_='saleCard__price--new')
				if( soldout_ctx != None) : 
					if( 0 <= soldout_ctx.get_text().find('Out')) : product_data.crw_is_soldout = 1
			
				
			####################################
			# 상품명 / 상품 링크 정보 / 상품번호 / 브랜드 / 가격
			#
			# <div class="saleCard__area-content"><a class="saleCard__link" href="/products/brands/65/"><p class="saleCard__brand">로투스</p></a> <a class="saleCard__link" href="/products/sales/1500/"><p class="saleCard__title">CAT 오븐베이크 그레인프리 닭고기 4종</p></a><p class="saleCard__area-tag _saleCardTagArea"><a class="saleCard__tag" href="/products/sales/list/?type=hashtag&amp;value=글루텐프리">#글루텐프리</a> <a class="saleCard__tag" href="/products/sales/list/?type=hashtag&amp;value=그레인프리">#그레인프리</a> <a class="saleCard__tag" href="/products/sales/list/?type=hashtag&amp;value=LID사료">#LID사료</a></p><a class="saleCard__link" href="/products/sales/1500/"><div class="saleCard__area-price"><ins class="saleCard__price--new"><span class="saleCard__price--discount">16%</span> 33,000원</ins> <del class="saleCard__price--old">37,000원</del></div><div class="saleCard__area-review"><div class="review-info__wrap"><i class="review-info__icon"><svg height="16" viewBox="0 0 16 16" width="16" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><path d="M6 9.95L2.292 12 3 7.658 0 4.584 4.146 3.95 6 0 7.854 3.95 12 4.584 9 7.658 9.708 12z" id="iconStarYellowA"></path></defs><g fill="none" fill-rule="evenodd" transform="translate(2 2)"><mask fill="#fff" id="iconStarYellowB"><use xlink:href="#iconStarYellowA"></use></mask><use fill="#000" fill-rule="nonzero" xlink:href="#iconStarYellowA"></use><path d="M-2 -2H14V14H-2z" fill="#FA0" mask="url(#iconStarYellowB)"></path></g></svg></i> <em class="review-info__score">5.0</em> <span class="review-info__count">상품평 4</span></div></div></a></div>
			####################################

			name_div_ctx = product_ctx.find('div', class_='saleCard__area-content')
			if( name_div_ctx != None) :
				link_list = name_div_ctx.find_all('a', class_='saleCard__link')
				for link_ctx in link_list :
					brand_ctx = link_ctx.find('p', class_='saleCard__brand')
					name_ctx = link_ctx.find('p', class_='saleCard__title')

					if(brand_ctx != None) : product_data.crw_brand1 = brand_ctx.get_text().strip()
					
					if(name_ctx != None) : 
						product_data.crw_name = name_ctx.get_text().strip()
						if('href' in link_ctx.attrs ) : 
							tmp_product_link = link_ctx.attrs['href'].strip()
							if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, link_ctx.attrs['href'].strip() )
							crw_post_url = tmp_product_link

							if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
						
							split_list = crw_post_url.split('/')
							product_data.crw_goods_code = split_list[5].strip()
	

			####################################
			# 가격
			#
			# <div class="saleCard__area-price"><ins class="saleCard__price--new"><span class="saleCard__price--discount">16%</span> 33,000원</ins> <del class="saleCard__price--old">37,000원</del></div>
			####################################

			price_list = product_ctx.find_all('div', class_='saleCard__area-price')
			for price_ctx in price_list :
				ins_ctx = price_ctx.find('ins', class_='saleCard__price--new')
				del_ctx = price_ctx.find('del', class_='saleCard__price--old')
				if(del_ctx != None) : 
					product_data.crw_price = int( __UTIL__.get_only_digit( del_ctx.get_text().strip() ) )
				if(ins_ctx != None) : 
					crw_price_sale = ins_ctx.get_text().strip()
					strip_str = ''
					strip_ctx = ins_ctx.find('span', class_='saleCard__price--discount')
					if(strip_ctx != None) : 
						len_strip_str = len( strip_ctx.get_text().strip() )
						product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale[len_strip_str:].strip() ) )
					else : product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale ) )


	

			if( crw_post_url != '' ) :
				if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
				
					self.set_product_data_sub( product_data, crw_post_url )

					#self.print_product_page_info( product_data ) 			
					self.process_product_api(product_data)


		except Exception as ex:
			__LOG__.Error('에러 : set_product_data')
			__LOG__.Error(ex)
			pass
			
		return is_loop	
		
	
		
	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()

	
	
	
	