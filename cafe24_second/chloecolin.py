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
		
		
		self.SITE_HOME = 'http://chloecolin.com'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		
		
		self.C_CATEGORY_VALUE = '#menu > div > div.xans-element-.xans-layout.xans-layout-category > div > ul > li > a'
		self.C_CATEGORY_IGNORE_STR = []
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		
		self.C_PAGE_VALUE = '#prd_contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		self.C_PRODUCT_VALUE = '#prd_contents > div.xans-element-.xans-product.xans-product-normalpackage > div.xans-element-.xans-product.xans-product-listnormal.plan-product > ul > li'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		
		self.C_LAST_PAGE_VALUE = '#prd_contents > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > a.last'
		
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
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = 'thumbnail'
		
		
		# 물품 SOLDOUT CSS selector 정의
		#
		self.C_PRODUCT_SOLDOUT_SELECTOR = ''
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = ''
		
		
		
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
			self.set_product_category_first(product_data, soup)

			###########################
			# 상품 이미지 확인
			#
			# <div class="thumbnail">
			# <span class="chk"><input type="checkbox" class="ProductCompareClass xECPCNO_20 displaynone"></span>
			# <div class="button eff"> <span class="wtooltip" data-title="간단보기"><img src="/web/upload/icon_201710231745322300.png" onclick="zoom('20', '43', '1','', '');" style="cursor:pointer" alt="상품 큰 이미지 보기"></span> <span class="wtooltip" data-title="관심상품"><img src="/web/upload/icon_201710231745462400.png" class="icon_img ec-product-listwishicon" alt="관심상품 등록 전" productno="20" categoryno="43" icon_status="off" login_status="F" individual-set="F"></span> <span class="wtooltip" data-title="장바구니"><img src="/web/upload/icon_201710231745388300.png" onclick="CAPP_SHOP_NEW_PRODUCT_OPTIONSELECT.selectOptionCommon(20,  43, 'basket', '')" alt="장바구니 담기" class="ec-admin-icon cart"></span> <span class="wtooltip" data-title="옵션보기"><a onclick="optionPreview(this,'listnormal-0',20,'T')" "=""><img src="/web/upload/icon_201710231745425200.png" id="btn_preview_listnormal-020" class="option_preview" alt=""></a></span> </div>
			# <div class="likeButton eff displaynone">
			# <button type="button"><strong></strong></button>
			# </div>
			# <a href="/product/detail.html?product_no=20&amp;cate_no=43&amp;display_group=1" name="anchorBoxName_20"><img src="//chloecolin.com/web/product/medium/201711/20_shop1_139403.jpg" id="eListPrdImage20_1" alt="유니크하고 편안한 프리미엄 반려견 의류. friendship forever."></a> <p class="sale eff" style=""><strong>50%</strong></p></div>
			############################
			
			self.set_product_image_fourth( product_data, product_ctx )
								

							
			###########################
			# 품절여부 확인
			#
			# <div class="button eff"> <span class="wtooltip" data-title="간단보기"><img src="/web/upload/icon_201710231745322300.png" onclick="zoom('104', '43', '1','', '');" style="cursor:pointer" alt="상품 큰 이미지 보기"></span> <span class="wtooltip" data-title="관심상품"><img src="/web/upload/icon_201710231745462400.png" class="icon_img ec-product-listwishicon" alt="관심상품 등록 전" productno="104" categoryno="43" icon_status="off" login_status="F" individual-set="F"></span> <span class="wtooltip" data-title="장바구니"><img src="/web/upload/icon_201710231745388300.png" onclick="CAPP_SHOP_NEW_PRODUCT_OPTIONSELECT.selectOptionCommon(104,  43, 'basket', '')" alt="장바구니 담기" class="ec-admin-icon cart"></span> <span class="wtooltip" data-title="옵션보기"><a onclick="optionPreview(this,'listnormal-0',104,'T')" "=""><img src="/web/upload/icon_201710231745425200.png" id="btn_preview_listnormal-0104" class="option_preview" alt=""></a></span> </div>
			# ------------- 품절시 ------
			# 장바구니 / 옵션보기 이미지가 없음
			# <div class="button eff"> <span class="wtooltip" data-title="간단보기"><img src="/web/upload/icon_201710231745322300.png" onclick="zoom('36', '42', '1','', '');" style="cursor:pointer" alt="상품 큰 이미지 보기"></span> <span class="wtooltip" data-title="관심상품"><img src="/web/upload/icon_201710231745462400.png" class="icon_img ec-product-listwishicon" alt="관심상품 등록 전" productno="36" categoryno="42" icon_status="off" login_status="F" individual-set="F"></span> <span class="wtooltip" data-title="장바구니"></span> <span class="wtooltip" data-title="옵션보기"></span> </div>
			###########################
			span_list = product_ctx.find_all('span', class_='wtooltip')
			for span_ctx in span_list :
				if('data-title' in span_ctx.attrs ) :
					if( span_ctx.attrs['data-title'] == '장바구니') :
						img_ctx = span_ctx.find('img')
						if(img_ctx == None ) : product_data.crw_is_soldout = 1
					

			###########################
			#
			# <span class="name"><a href="/product/detail.html?product_no=20&amp;cate_no=43&amp;display_group=1" class=""><span class="title displaynone"><span style="font-size:12px;color:#555555;">상품명</span> :</span> <span style="font-size:12px;color:#555555;">Robe black</span></a></span>
			###########################
			
			crw_post_url = self.set_product_name_url_first( product_data, product_ctx , 'span', 'name')
	
			self.set_product_price_brand_first(product_data, product_ctx )

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

			table_list = soup.select('#plus_all > div > div.xans-element-.xans-product.xans-product-detaildesign > table')
			
			rtn_dict = self.get_value_in_table_two_colume( table_list, '기본 정보', 'th', 'td')
			if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
			if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )
			if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			
			self.set_detail_brand( product_data, crw_brand )
			
			# 제품 상세 부분			
			self.get_cafe24_text_img_in_detail_content_part( soup, product_data, '#prdDetail > div > div', '' )
			
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()

	
	
	