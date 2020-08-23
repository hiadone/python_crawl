#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이 사항
 - 물품리스트에 페이지 링크가 있는 것이 아닌, 더보기 버튼이 있음.
 - 더보기 버튼 클릭시, api 로 물품리스만 갖고 와서, 화면에 업데이트만 함.

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
		
		self.SITE_HOME = 'http://dfang.co.kr'

		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		

		self.C_CATEGORY_VALUE = '#one_cate > div > ul > li'

		
		self.C_CATEGORY_IGNORE_STR = ['리뷰','디팡TV']
		self.C_CATEGORY_STRIP_STR = ''

		
		
		#self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_PAGE_TYPE = ''
		#self.C_PAGE_VALUE = '#paging > div > ol > li > a'
		#self.C_PAGE_STRIP_STR = ''
		
		#self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		#self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#prd_place > ul > li'
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		#self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		#self.C_LAST_PAGE_TYPE = ''
		#self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		#self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_HOME
		self.BASIC_PAGE_URL = self.SITE_HOME
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
		
		#
		# dfang에서만 사용하는 값
		#
		self.CRW_CATEGORY_1 = ''
		self.CRW_CATEGORY_2 = ''
		self.CRW_CATEGORY_3 = ''
		

		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
	'''
	#
	#
	#
	'''	
	
	def get_category_data(self, html):
		rtn = False
		
		#__LOG__.Trace(html)
		self.set_param_category(html)
		
		category_link_list = []
		category_link_list_2 = []
		
		category_link_list_3 = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)
		
		__LOG__.Trace('----------------------------------------------------------')
		for li_ctx in category_link_list :
			try :
				#__LOG__.Trace(category_ctx)

				if(self.check_ignore_category( li_ctx ) ) :
					main_category_name = ''
					category_ctx = li_ctx.find('a')
					if( category_ctx != None ) :
						main_category_name = category_ctx.get_text().strip()
						if('href' in category_ctx.attrs ) : 
							tmp_category_link = category_ctx.attrs['href']
							if(tmp_category_link.find('javascript') < 0 ) :
								if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

								category_link = tmp_category_link
								
								if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
								
								category_name = main_category_name
								if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
									self.CATEGORY_URL_HASH[category_link] = category_name
									if( config.__DEBUG__ ) :
										__LOG__.Trace('%s : %s' % ( category_name, category_link ) )

									rtn = True
									
					ul_ctx = li_ctx.find('ul')	
					if( ul_ctx != None ) :
						sub_li_list = ul_ctx.find_all('a')
						for sub_category_ctx in sub_li_list :
							if('href' in sub_category_ctx.attrs ) : 
								tmp_category_link = sub_category_ctx.attrs['href']
								if(tmp_category_link.find('javascript') < 0 ) :
									if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, sub_category_ctx.attrs['href'] )

									category_link = tmp_category_link
									
									if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
									
									category_name = sub_category_ctx.get_text().strip()
									if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
										self.CATEGORY_URL_HASH[category_link] = '%s|%s' % (main_category_name, category_name )
										if( config.__DEBUG__ ) :
											__LOG__.Trace('%s|%s : %s' % ( main_category_name, category_name, category_link ) )

										rtn = True
						
					


			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		
		
		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
		
		
	
	def get_page_data(self, category_url, html):
		'''
		API : http://dfang.co.kr/exec/front/Product/ApiProductMain?display_group=40&supplier_code=S0000000&page=1&bInitMore=T&count=12
		
		- html 의 script 내용에서 
			1) API에서 사용하는 display_group=/ supplier_code=S0000000/ count= 값을 얻는다.
		
			try { $M.setDisplayPageMore(45, 46, 0, 12, 0, true, 'S0000000', false, ''); } catch(e) {}
		
		- 더보기 버튼에서 
			1) 최종 페이지 번호를 얻는다.
			
				<div class="xans-element- xans-product xans-product-listmore-39 xans-product-listmore xans-product-39 ec-base-paginate typeMoreview"><a href="#none" onclick="try { $M.displayMore(39, 40, 0, 12, 0, true, 'S0000000', false, ''); } catch(e) { return false; }" class="btnMores">
						더보기 (<span id="more_current_page_40" class=""> 1</span> /  <span id="more_total_page_40" class="">5 </span>)
						<span class="icoMore"></span>
					</a>
		</div>
		'''
		rtn = False

		self.set_param_page(html)
		
		# 초기화
		display_group = ''
		supplier_code = ''
		count = ''
		span_more_id = ''
		last_page = '1'
		
		# script 안에서 데이터 추출
		if( 0 < html.find('$M.setDisplayPageMore(') ) :
			split_list = html.split('$M.setDisplayPageMore(')
			sub_split_list = split_list[1].split(',')
			display_group = sub_split_list[1].strip()
			supplier_code = sub_split_list[6].replace("'","").strip()
			count = sub_split_list[3].strip()
			span_more_id = 'more_total_page_' + display_group
					
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		# 더보기 버튼에서 최종 페이지 추출
		morebtn_link_ctx = soup.find('a', class_='btnMores')
		if( morebtn_link_ctx != None) :
			total_page_ctx = morebtn_link_ctx.find('span', {'id': span_more_id })
			if( total_page_ctx != None) : last_page = total_page_ctx.get_text().strip()
				
		if( supplier_code != '') :
			page_link = 'http://dfang.co.kr/exec/front/Product/ApiProductMain?display_group=%s&supplier_code=%s&page=%s&bInitMore=T&count=%s' % ( display_group, supplier_code, last_page, count )
			
			if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
				self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
				__LOG__.Trace( page_link )
			
		
		return rtn , int(last_page)
		
		
		
	def process_page(self, category_url):
	
		rtn = False
		resptext = ''
		
		try :
			
			# 첫 페이지를 추가함.
			self.PAGE_URL_HASH[category_url] = self.CATEGORY_URL_HASH[category_url]
			
			if( config.__DEBUG__ ) :
				__LOG__.Trace('page : %s' % ( category_url ) )
				
			time.sleep(self.WAIT_TIME)
			URL = category_url
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header, verify=False)

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn, avaible_page_count = self.get_page_data( category_url, resptext )
							
		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
	
	
	def get_product_data(self, page_url, html):
		rtn = False
		
		self.set_param_product(html)
		product_link_list = []
		
		if(0 < page_url.find('ApiProductMain') ) :
			# 첫화면 이외의 api에서 얻은 데이터 처리
			json_data = json.loads(html)
		
			if('rtn_data' in json_data ) :
				product_json_data = json_data['rtn_data']['data']
				__LOG__.Trace('product list : %d' % len(product_json_data) )
				
				for idx in range(len(product_json_data)) :
					product_json = product_json_data[idx]
					self.set_product_data_second( page_url, product_json )					
		
		else :	
			# 첫 화면에 대한 html 파싱하는 부분
			soup = bs4.BeautifulSoup(html, 'lxml')
				
			if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
			__LOG__.Trace('product list : %d' % len(product_link_list) )
			
			for product_ctx in product_link_list :
				self.set_product_data( page_url, soup, product_ctx )

		return rtn
	
	'''
	######################################################################
	#
	# 상품 리스트 데이터 추출
	# - API의 json 데이터에서 추출하는 함수
	# - 2 페이지 부터
	######################################################################
	'''
	
	def set_product_data_second(self , page_url, product_json ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			# 상품 카테고리
			#
			#self.set_product_category_second(page_url, product_data, soup)
			#product_data.crw_category1 = self.PAGE_URL_HASH[ page_url ]
			product_data.crw_category1 = self.CRW_CATEGORY_1
			product_data.crw_category2 = self.CRW_CATEGORY_2
			product_data.crw_category3 = self.CRW_CATEGORY_3
			

			for key in product_json :
				#__LOG__.Trace('%s : %s' % (key, product_json[key] ))
				# 이미지
				if(key == 'image_medium' ) : 
					img_src = product_json[key]
					img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
					product_data.product_img = self.get_hangul_url_convert( img_link )

					
				if(key == 'image_big' ) : 
					if( product_data.product_img != '') : 
						img_src = product_json[key]
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )

						
				if(key == 'image_small' ) : 
					if( product_data.product_img != '') : 
						img_src = product_json[key]
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )
					
				# 상품명
				if(key == 'product_name_striptag' ) : product_data.crw_name = product_json[key]
				if(key == 'product_name_tag' ) : 
					if( product_data.crw_name != '') : product_data.crw_name = product_json[key]
				if(key == 'product_name' ) : 
					if( product_data.crw_name != '') : product_data.crw_name = product_json[key]
					
				# 상품명번호
				if(key == 'product_no' ) : product_data.crw_goods_code = str( product_json[key] )
				
				# 상품 URL
				if(key == 'link_product_detail' ) : 
					tmp_product_link = product_json[key]
					if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_json[key] )
					crw_post_url = tmp_product_link

					if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

				# 상품 가격
				if(key == 'product_custom' ) : product_data.crw_price = int( product_json[key] )
				if(key == 'product_price' ) : product_data.crw_price_sale = int( product_json[key] )
				
				# soldout
				if(key == 'soldout_icon' ) : 
					if( product_json[key].strip() != '') : product_data.crw_is_soldout = 1


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
	# 상품 리스트 데이터 추출
	# - 첫화면의 html에서 데이터 추출
	######################################################################
	'''		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
					
			# 상품 카테고리
			#
			self.CRW_CATEGORY_1 = ''
			self.CRW_CATEGORY_2 = ''
			self.CRW_CATEGORY_3 = ''
			
			split_list = self.PAGE_URL_HASH[ page_url ].split('|')
			
			idx = 0
			for split_data in split_list :
				idx += 1
				if(idx == 1) : product_data.crw_category1 = split_data
				elif(idx == 2) : product_data.crw_category2 = split_data
				elif(idx == 3) : product_data.crw_category3 = split_data
				
			#self.set_product_category_second(page_url, product_data, soup)
			self.CRW_CATEGORY_1 = product_data.crw_category1
			self.CRW_CATEGORY_2 = product_data.crw_category2
			self.CRW_CATEGORY_3 = product_data.crw_category3
		
			#product_data.crw_category1 = self.PAGE_URL_HASH[ page_url ]

			# 상품 이미지 확인
			self.set_product_image_fourth(product_data, product_ctx )
				
			# 품절여부 확인
			self.set_product_soldout_first(product_data, product_ctx ) 
			
			img_div_list = product_ctx.find_all('div', class_=self.C_PRODUCT_IMG_SELECTOR_CLASSNAME)

			for img_div_ctx in img_div_list :
				product_link_ctx = img_div_ctx.find('a')
				if( product_link_ctx != None) :
					if('href' in product_link_ctx.attrs ) :
						crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
						if(crw_post_url != '') :
							split_list = crw_post_url.split('/')
							if(5 < len(split_list) ) : product_data.crw_goods_code = split_list[5].strip()

			name_div_list = product_ctx.find_all('div', class_='description')

			for name_div_ctx in name_div_list :
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				name_strong_list = name_div_ctx.find_all('strong', class_='name')
				for name_strong_ctx in name_strong_list :
					product_link_list = name_strong_ctx.find_all('a')
					for product_link_ctx in product_link_list :
						span_list = product_link_ctx.find_all('span')
						for span_ctx in span_list :
							name_value = span_ctx.get_text().strip()
							if(0 != name_value.find('상품명') ) and (0 != name_value.find(':') ) and ( name_value.strip() != '') : product_data.crw_name = name_value


				# 가격
				li_list = name_div_ctx.find_all('li')
				for li_ctx in li_list :
					span_list = li_ctx.find_all('span')
					for span_ctx in span_list :
						price_value = span_ctx.get_text().strip()
						if(price_value != '' ) and ( price_value != ':' ) :
							if('style' in span_ctx.attrs) :
								if( 0 < span_ctx.attrs['style'].find('text-decoration') ) : product_data.crw_price = int( __UTIL__.get_only_digit( price_value ) )
								else : product_data.crw_price_sale = int( __UTIL__.get_only_digit( price_value ))
				
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
			
			crw_brand = []
			
			'''
			#
			# <meta name="keywords" content="[상품검색어],[브랜드],[트렌드],[제조사]">
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : crw_brand.append( split_list[1].strip() )
			'''

			table_list = soup.select('#infoArea > div.xans-element-.xans-product.xans-product-detaildesign > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )

			
			self.set_detail_brand( product_data, crw_brand )

			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDetail > div', '' )



			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	app = shop()
	app.start()
	

	
	