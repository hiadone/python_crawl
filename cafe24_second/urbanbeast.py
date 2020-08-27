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
from cafe24.Cafe24 import Cafe24


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(Cafe24) :    

	def __init__(self) :
	
		Cafe24.__init__(self)

		
		self.SITE_HOME = 'http://www.urbanbeast.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#main > header > div.header-wrap > nav > ul.xans-element-.xans-layout.xans-layout-category.main-cate > li > a'
		
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#contents > div > div.xans-element-.xans-product.xans-product-normalpaging.paging.row > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#contents > div:nth-child(3) > div.prdList-wrap > div.xans-element-.xans-product.xans-product-listnormal.infinite > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''

		self.C_LAST_PAGE_VALUE = '#contents > div.inner > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
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
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'box'
		
		
		# 물품 SOLDOUT CSS selector 정의
		# 
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'p'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'name'
		
	'''
	######################################################################
	#
	# Mall.py 대체
	#
	######################################################################
	'''

	def process_category_list(self):
		self.process_category_list_second()		

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
			
			# 상품 카테고리
			#
			self.set_product_category_third(product_data, soup)
			#self.set_product_category_second(page_url, product_data, soup)
			
				
			###########################
			# 상품 이미지 확인
			#
			# <a href="/product/detail.html?product_no=348&amp;cate_no=105&amp;display_group=1" name="anchorBoxName_348"><img class="lazy thumb" src="//www.urbanbeast.co.kr/web/product/big/201901/270edfd2fcebe218147a9cdf9904bc06.jpg" data-original="//www.urbanbeast.co.kr/web/product/big/201901/270edfd2fcebe218147a9cdf9904bc06.jpg" alt="" style="display: inline;"></a>
			###########################
			img_link_list = product_ctx.find_all('a')
			for img_link_ctx in img_link_list :
				if('name' in img_link_ctx.attrs) :
					if( 0 <= img_link_ctx.attrs['name'].find('anchorBoxName_')) :
						img_ctx = img_link_ctx.find('img')
						if( img_ctx != None) : 
							if('data-original' in img_ctx.attrs ) :
								img_src = img_ctx.attrs['data-original'].strip()
								if( img_src != '' ) :
									img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
									if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )
							

			# 품절여부 확인
			#
			self.set_product_soldout_first(product_data, product_ctx ) 

			###########################
			# 상품명/URL
			#
			# <a href="/product/detail.html?product_no=146&amp;cate_no=24&amp;display_group=1" class="text-wrap ease">             
			# <span class="text ease"> 
			# <p class="name"><span style="font-size:12px;color:#1e1e1e;">Beast Den Bumper Bed Dynamite Red<br>비스트덴 다이너마이트 레드</span>   </p>
			# <ul class="xans-element- xans-product xans-product-listitem"><li class=" xans-record-">
			# <strong class="title displaynone"><span style="font-size:12px;color:#1e1e1e;font-weight:bold;">판매가</span> :</strong> <span style="font-size:12px;color:#1e1e1e;font-weight:bold;">98,000원</span><span id="span_product_tax_type_text" style=""> </span></li>
			# </ul>
			# </span>                            
			# </a>
			###########################
			product_link_ctx = product_ctx.find('a', class_='text-wrap ease')
			if(product_link_ctx != None) :
				tmp_product_link = product_link_ctx.attrs['href'].strip()

				if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
				crw_post_url = tmp_product_link

				if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

				split_list = crw_post_url.split('?product_no=')
				crw_goods_code_list = split_list[1].strip().split('&')
				product_data.crw_goods_code = crw_goods_code_list[0].strip()
				
			
			product_name_ctx = product_ctx.find('p', class_='name')
			if(product_name_ctx != None) : product_data.crw_name = product_name_ctx.get_text().strip()
			

			##############################
			# 가격
			#

			##############################
			self.set_product_price_brand_first(product_data, product_ctx)

				
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
			####################################
			# 상품 기본 정보에서 브랜드 등을 추출
			####################################
		
			crw_brand = []
			
			'''
			for tag in soup.find_all("meta"):
				if tag.get("name", None) == 'keywords' :
					rtn = tag.get('content', None)
					if(rtn != None) :
						split_list = rtn.split(',')
						if( split_list[1].strip() != '' ) : crw_brand.append( split_list[1].strip() )
			'''

			table_list = soup.select('#contents > div.xans-element-.xans-product.xans-product-detail.row > div.xans-element-.xans-product.xans-product-image.imgArea > div.infoArea > div.infomation > div.xans-element-.xans-product.xans-product-detaildesign > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('BRAND' , -1) != -1) : crw_brand.append( rtn_dict['BRAND'] )
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('제조국' , -1) != -1) : crw_brand.append( rtn_dict['제조국'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			if(rtn_dict.get('Origin' , -1) != -1) : crw_brand.append( rtn_dict['Origin'] )

			
			self.set_detail_brand( product_data, crw_brand )
			
			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#contents > div.xans-element-.xans-product.xans-product-detail.row > div.xans-element-.xans-product.xans-product-image.imgArea > div.imgArea-wrap.ease > div.detailArea.clearfix', '' )
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	