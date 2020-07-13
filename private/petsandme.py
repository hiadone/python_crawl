#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

특이사항
	- 'ISO-8859-1'인코딩, 일치하지 않으면 한글 깨짐.
	
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
		
		self.EUC_ENCODING = None	# 'ISO-8859-1'일때 인코딩값, 일치하지 않으면 한글 깨짐.
		
		self.SITE_HOME = 'http://www.petsandme.co.kr'
		
		self.SITE_ORG_HOME = self.SITE_HOME
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		self.C_CATEGORY_VALUE = '#header > div.gnb_wrap > div.box1 > div.gnb > ul.menu > li > p > a'
		self.C_CATEGORY_IGNORE_STR = ['New','BEST PRODUCTS']
		self.C_CATEGORY_STRIP_STR = '..'

		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = '#contents > div > div > div > div.paging_no > div > a'
		self.C_PAGE_STRIP_STR = '..'
		
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 10	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''


		self.C_PRODUCT_VALUE = '#contents > div > div > div.prodarea > div.prodBox'
		self.C_PRODUCT_STRIP_STR = '..'
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#contents > div > div > div > div.paging_btn > div > a'
		
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

			table_list = soup.select('#contents > div > div.prod_view.box > form > div > div.info_wrap > div > div.spec > div > div > table')
			rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 1)
			for key in rtn_dict :
				if(0 <= key.find('제조사') ) or (0 <= key.find('제조국') ) or (0 <= key.find('브랜드')) or (0 <= key.find('원산지') ) : crw_brand.append( rtn_dict[key].strip() )
			self.set_detail_brand( product_data, crw_brand )
			

			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#contents > div > div.prod_view_con.box > div', 'p', 'src' )
			
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
			
			
			product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
			
			
			####################################				
			# 상품 이미지 확인
			#
			# <div class="img prod_resize" style="height: 271px;">
			# <img src="../shop_sun/files/pro_img/list/202003142040570.jpg" border="0" align="absmiddle" alt="유치원 조끼 ( 4 colors )">                <!-- <div class="layerMenu_on">
			# <span class="bg"></span>
			# <div class="inner">
			# <p class="sale">10 %</p>
			# <ul class="icon_btn"> -->
			# <!-- <li class="t2"><a href="#"><i class="xi xi-cart-o"></i></a></li> --><!--장바구니 -->
			# <!-- <li class="t2"><a href="#"><i class="xi xi-heart-o"></i></a></li> --><!--찜하기 -->
			# <!-- </ul>
			# </div>
			# </div> -->
			# </div>
			# 
			####################################
			
			span_list = product_ctx.find_all('div', class_='img prod_resize')
			for span_ctx in span_list :
				img_list = span_ctx.find_all('img')
				for img_ctx in img_list :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].replace('..','').strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].replace('..','').strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						product_data.product_img = self.get_hangul_url_convert( img_link )
						
						
			
			####################################
			# 품절여부
			#
			# <p class="prod_icon equal2" style="height: 20px;"><span class="st4">품절</span></p>
			####################################
			name_div_list = product_ctx.find_all('p', class_='prod_icon equal2')
			for name_div_ctx in name_div_list :			
				soldout_ctx = name_div_ctx.find('span', class_='st4')
				if( soldout_ctx != None) : 
					if( 0 <= soldout_ctx.get_text().find('품절')) : product_data.crw_is_soldout = 1
			
				
			####################################
			# 상품명 / 상품 링크 정보 / 상품번호
			#
			# <div class="prod line_ani" onclick="javascript:location.href='../product/view.php?p_idx=218&amp;cate=0005_0008_'">
			####################################
			name_div_ctx = product_ctx.find('div', class_='prod_info')
			if( name_div_ctx != None) :
				product_link_ctx = name_div_ctx.find('p', class_='prod_tit equal3')
				if( product_link_ctx != None ) : product_data.crw_name = product_link_ctx.get_text().strip()



			name_div_ctx = product_ctx.find('div', class_='prod line_ani')
			if( name_div_ctx != None) :
				if('onclick' in name_div_ctx.attrs ) : 
					split_list = name_div_ctx.attrs['onclick'].split('.href=')
					tmp_link = split_list[1].replace("'","").replace('&amp;','&').strip()
					tmp_product_link = tmp_link
					if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, tmp_link )
					crw_post_url = tmp_product_link

					if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
				
					split_list = crw_post_url.split('?p_idx=')
					sub_split_list = split_list[1].strip().split('&')
					product_data.crw_goods_code = sub_split_list[0]
	

			####################################
			# 가격
			#
			# <div class="price"><span class="t1">26,000</span><span class="t2">원</span></p></div>
			####################################

			price_list = product_ctx.find_all('div', class_='price')
			for price_ctx in price_list :
				p_ctx = price_ctx.find('p', class_='p2')
				if(p_ctx != None) : 
					value_ctx = p_ctx.find('span', class_='t1')
					if(value_ctx != None) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_ctx.get_text().strip() ) )

	

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

	
	
	
	