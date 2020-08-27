#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- Dog 카테고리만 수집함. ( http://studioalive.co.kr/product/list.html?cate_no=52 )
	
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

		#self.REFERER_SUB_CATEGORY_STR = 'http://studioalive.co.kr/product/list.html?cate_no=52'
		
		self.SITE_HOME = 'http://studioalive.co.kr/product/list.html?cate_no=52'
		
		self.ORG_SITE_HOME = 'http://studioalive.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#path-wrap > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#paging > ul > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#product > ul > li > div'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''

		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.ORG_SITE_HOME
		self.BASIC_PAGE_URL = self.ORG_SITE_HOME + '/product/list.html'
		self.BASIC_PRODUCT_URL = self.ORG_SITE_HOME
		self.BASIC_IMAGE_URL = self.ORG_SITE_HOME
		
		'''
		# Cafe24 전용 
		#
		'''
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = 'div'
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'thumb2'
		
		
		# 물품 SOLDOUT CSS selector 정의
		# 
		self.C_PRODUCT_SOLDOUT_SELECTOR = 'div'
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = 'icon'
		
		

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
			###########################
			self.set_product_image_fourth( product_data, product_ctx )

			# 품절여부 확인
			#
			self.set_product_soldout_first(product_data, product_ctx ) 
						

			###########################
			# 상품명/URL
			###########################
			
			crw_post_url = self.set_product_name_url_first( product_data, product_ctx , 'div', 'name')
			
			
			##############################
			# 가격
			#
			# <div class="xans-element- xans-product xans-product-listitem table"><div class="price  xans-record-"><span style="font-size:12px;color:#555555;text-decoration:line-through;">73,000원</span><span id="span_product_tax_type_text" style="text-decoration:line-through;"> </span></div>
			# <div class="saleprice  xans-record-"><span style="font-size:12px;color:#ff0000;">65,700원 <span style="font-size:12px;color:#ff0000;font-weight:bold;">(7,300원 할인)</span></span></div>
			# <div class="saleprice  xans-record-"><div class="discountPeriod">
			# <a href="#none"><img src="//img.echosting.cafe24.com/skin/base_ko_KR/product/btn_details.gif" alt="자세히"></a>
			# <div class="layerDiscountPeriod ec-base-tooltip" style="display: none;">
			# <div class="content">
			# <strong class="title"><img src="//img.echosting.cafe24.com/skin/base_ko_KR/common/ico_tip_title.gif" alt=""> 할인기간</strong>
			# <p><strong>남은시간 1794일 11:24:06 (7,300원 할인)</strong></p>
			# <p>2020-07-24 00:00 ~ 2025-07-01 23:55</p>
			# </div>
			# <a href="#none" class="close btnClose"><img src="//img.echosting.cafe24.com/skin/base_ko_KR/common/btn_close_tip.gif" alt="닫기"></a>
			# <span class="edge"></span>
			# </div>
			# </div></div>
			# <div class="saleprice  xans-record-"><div class="color"><span class="chips" title="#FFFFFF" style="background-color:#FFFFFF" color_no="" displaygroup="1"></span><span class="chips" title="#A9A9A9" style="background-color:#A9A9A9" color_no="" displaygroup="1"></span><span class="chips" title="#FEC0CB" style="background-color:#FEC0CB" color_no="" displaygroup="1"></span><span class="chips" title="#FFFFFF" style="background-color:#FFFFFF" color_no="" displaygroup="1"></span><span class="chips" title="#A9A9A9" style="background-color:#A9A9A9" color_no="" displaygroup="1"></span><span class="chips" title="#FEC0CB" style="background-color:#FEC0CB" color_no="" displaygroup="1"></span></div></div>
			# </div>
			##############################
			#self.set_product_price_brand_first(product_data, product_ctx)
			price_div_list = product_ctx.find_all('div', class_='price')
			for price_div_ctx in price_div_list :
				product_data.crw_price = int( __UTIL__.get_only_digit( price_div_ctx.get_text().strip() ) )
			
			sale_price_div_list = product_ctx.find_all('div', class_='saleprice')
			for sale_price_div_ctx in sale_price_div_list :
				check_div_ctx = sale_price_div_ctx.find('div')
				#div 가 없어야 함.
				if( check_div_ctx == None) :
					split_list = sale_price_div_ctx.get_text().strip().split('(')
					value_str = split_list[0].strip()
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ) )
				
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

			
			table_list = soup.select('#df-product-detail > div > div.infoArea-wrap > div > div > div.scroll-wrapper.df-detail-fixed-scroll.scrollbar-macosx > div.df-detail-fixed-scroll.scrollbar-macosx.scroll-content > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('BRAND' , -1) != -1) : crw_brand.append( rtn_dict['BRAND'] )
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			if(rtn_dict.get('Origin' , -1) != -1) : crw_brand.append( rtn_dict['Origin'] )
			'''
			
			self.set_detail_brand( product_data, crw_brand )
			
			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDscp > div.cont', '' )

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	
	