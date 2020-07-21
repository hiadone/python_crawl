#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018. 8. 31.

@author: user

고도몰 분류
1) 일반적인 고도몰
	https://www.biteme.co.kr/main/index.php
	https://www.fitpetmall.com/
	http://www.gaenimshop.com/
	http://ssfw.kr
	http://www.diditable.com/

	http://www.gulliverdog.co.kr/main/index.php
	http://www.edenchien.com/main/index.php
	http://bourdog.com/main/index.php
	http://vlab.kr/
	https://www.wangzzang.com/
	www.petgear.kr/


2) 1)형태에서 조금 벗어난 고도몰
   - 1)번과 상품리스트의 CSS SELECTOR 요소만 다름. (CLASS NAME 등..)
   
	http://ainsoap.com/
	http://www.petesthe.co.kr/main/index.php


3) 고도몰 형태가 아닌 일반 쇼핑몰에 가까운 형태
	- 상품 리스트 / 페이지 링크 리스트 / 상세 페이지 CSS SELECTOR 가 TABLE > TR > TD 에 
	  들어가 있는 형태
	  
	http://mytrianon.co.kr/shop/goods/goods_list.php?&category=003
	http://www.naturalex.co.kr/shop/main/index.php



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


    
class GodoMall(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)
		
		#
		# - 물품 리스트
		# 	카테고리를 추출시 추출하는 타입이 select 일때 True 이며
		# 	h1/h2 에서 추출할때는 False 이다.
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = True
		
		#
		# - 물품 리스트
		# 	카테고리를 추출시 CLASS NAME
		
		self.SET_PRODUCT_DATA_CATEGORY_DIV_SELECTOR = 'div'
		self.SET_PRODUCT_DATA_CATEGORY_CLASS_NAME = ''
				
		#
		# - 물품 리스트
		# 	카테고리를 추출시 HTML 요소 
		# self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = FALSE 일때 사용
		self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR = ''
		
		#
		# - 물품 상세 페이지
		# 	상품기본 정보 DL SELECTOR 
		# DL/DT 타입 : self.SET_PRODUCT_DETAIL_DATA_DL = True
		# LI 타입 : self.SET_PRODUCT_DETAIL_DATA_DL = False
		#
		self.SET_PRODUCT_DETAIL_DATA_DL = True
		
		self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR = ''
		
		
		#
		# - 물품 상세 페이지
		# 	물품 상세 설명에서 이미지와 글이 포함된 DIV SELECTOR 
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = ''
		
		#
		# - 물품 상세 페이지
		# 	self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR 안에 글자에 세부 HTML 요소 
		self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR = ''
		
		
		#
		# - 물품 상세 페이지
		# 	상세설명에 테이블 형태로 제조사/브랜드 명이 들어가 있을때 
		self.SET_PRODUCT_DETAIL_DATA_TABLE = False
		
		self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR = ''
		
	
	
	'''
	######################################################################
	#
	# 아래 사이트에서만 사용 , set_product_data을 set_product_data_second으로 사용함.
	#
	# - ainsoap : https://www.ainsoap.com
	# - petesthe : http://www.petesthe.co.kr
	#
	######################################################################
	'''
	
	def set_product_data_second(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			
			####################################
			# 상품 카테고리 추출
			####################################
			div_list = soup.find_all("div" , class_='cg-main')
			for div_ctx in div_list :
				category_list = div_ctx.find_all('h2')
				for category_ctx in category_list :
					product_data.crw_category1 = category_ctx.get_text().strip()
		
			'''
			# 브랜드 확인		
			brand_div_list = product_ctx.find_all('span', class_='item_brand')
			for brand_ctx in brand_div_list :
				brand_name = brand_ctx.get_text().strip()
				if( brand_name != '') : product_data.crw_brand1 = brand_name.replace('[','').replace(']','').strip()
			'''	
							
			####################################				
			# 상품 이미지 확인
			#
			# <div class="thumbnail">
			# <a href="../goods/goods_view.php?goodsNo=1000000030"><img src="/data/goods/16/10/43/1000000030/1000000030_main_072.jpg" width="184" alt="Pet Esthé Spa Mud Conditioner (스파 머드 컨디셔너) (3L)" title="Pet Esthé Spa Mud Conditioner (스파 머드 컨디셔너) (3L)" class="middle">
			# </a>
			# </div>
			####################################	
			img_div_list = product_ctx.find_all('div', class_='thumbnail')
			for img_div_ctx in img_div_list :
				img_ctx = img_div_ctx.find('img')
				#for img_ctx in img_list :

				if(img_ctx != None) :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )
			
			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="txt">
			# <a href="../goods/goods_view.php?goodsNo=1000000030">
			# <strong>Pet Esthé Spa Mud Conditioner (스파 머드 컨디셔너) (3L)</strong>                    </a>
			# </div>
			#
			####################################
			name_div_list = product_ctx.find_all('div', class_='txt')

			for name_div_ctx in name_div_list :
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :

					if('href' in product_link_ctx.attrs ) : 
						span_list = product_link_ctx.find_all('strong')
						for span_ctx in span_list :
							product_data.crw_name = span_ctx.get_text().strip()

							
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?goodsNo=')
						product_data.crw_goods_code = split_list[1].strip()
					
			####################################
			# 가격 / 품절여부
			#
			# <div class="price gd-default">
			# <span class="cost">
			# <strong>180,000</strong>원
			# </span>
			# <br>
			# </div>
			#
			# -------------품절시 -----------------
			# <div class="price gd-default">
			# <span class="cost">
			# <strong>일시품절</strong>
			# </span>
			# <br>
			# </div>
			#
			####################################
			div_list = product_ctx.find_all('div')
			for div_ctx in div_list :
				if('class' in div_ctx.attrs) :
					class_name_list = div_ctx.attrs['class']
					if( class_name_list[0] == 'price' ) :
						cost_ctx = div_ctx.find('span', class_='cost')
						if( cost_ctx != None ) : 
							cost_value = cost_ctx.get_text().strip()
							product_data.crw_price = int( __UTIL__.get_only_digit( cost_value ) )
							
							if(0 < cost_value.find('품절')) : product_data.crw_is_soldout = 1
							
			
			
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
			
			
			####################################
			# 상품 카테고리 추출
			####################################
			if(self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE == True) :
				# 
				# SELECT 타입으로 - DIV CLASS : 'location_tit' 에 카테고리 값이 있음.
				div_list = soup.find_all("div" , class_='location_tit' )
				category_list = []
				for div_ctx in div_list :
					category_list.append( div_ctx.get_text().strip() )
				
				y = 0
				for idx in range(len(category_list) -1, -1, -1) :
					if(y == 0 ) : product_data.crw_category1 = category_list[idx]
					elif(y == 1 ) : product_data.crw_category2 = category_list[idx]
					elif(y == 2 ) : product_data.crw_category3 = category_list[idx]
					y += 1
				

			else :
				# 
				# H1 / H2 / H3 타입으로 
				div_list = soup.find_all( self.SET_PRODUCT_DATA_CATEGORY_DIV_SELECTOR , class_=self.SET_PRODUCT_DATA_CATEGORY_CLASS_NAME )
				for div_ctx in div_list :				
					if( self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR == '' ) : 
						product_data.crw_category1 = div_ctx.get_text().strip()
					else :
						category_list = div_ctx.find_all( self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR )
						for category_ctx in category_list :
							product_data.crw_category1 = category_ctx.get_text().strip()
							
							
					
			####################################
			# 브랜드 추출	
			#
			# <span class="item_brand">
			# <strong>[지그니쳐]</strong>
			# </span>
			#
			####################################
			brand_div_list = product_ctx.find_all('span', class_='item_brand')
			for brand_ctx in brand_div_list :
				brand_name = brand_ctx.get_text().strip()
				if( brand_name != '') : product_data.crw_brand1 = brand_name.replace('[','').replace(']','').strip()
				
			####################################				
			# 상품 이미지 확인
			#
			# <div class="item_photo_box">
			# <a href="../goods/goods_view.php?goodsNo=1000000896&amp;mtn=%5E%7C%5E%5E%7C%5E">
			# <img data-original="/data/goods/19/10/43/1000000896/1000000896_add2_085.jpg" width="250" alt="바잇밀 - 치킨/오리/말고기 샘플러 100g (3종)" title="바잇밀 - 치킨/오리/말고기 샘플러 100g (3종)" class="middle gd_image_lazy" src="/data/goods/19/10/43/1000000896/1000000896_add2_085.jpg" style="display: inline;">
			# </a>
			# </div>
			####################################
			img_div_list = product_ctx.find_all('div', class_='item_photo_box')
			for img_div_ctx in img_div_list :
				img_ctx = img_div_ctx.find('img')
				#for img_ctx in img_list :

				if(img_ctx != None) :
					img_src = ''
					if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
					elif('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
						
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )

							
			####################################
			# 품절여부 추출 (2가지 방법)
			#
			# <div class="item_icon_box">
			# <img src="/data/icon/goods_icon/당일출고아이콘.gif" alt="벌써배송상품" title="벌써배송상품" class="middle"> 
			# <img src="/data/icon/goods_icon/icon_soldout.gif">
			# </div>
			#
			#------------------------------------
			#
			# <div class="item_photo_box">
			# <a href="../goods/goods_view.php?goodsNo=1000001614">
			# <img data-original="/data/goods/20/05/20/1000001614/1000001614_add2_099.jpg" width="250" alt="빅독 리틀 바이트 사료 - 악어고기 100g" title="빅독 리틀 바이트 사료 - 악어고기 100g" class="middle gd_image_lazy" src="/data/goods/20/05/20/1000001614/1000001614_add2_099.jpg" style="display: inline;">
			# <strong class="item_soldout_bg" style="background-image:url(/data/icon/goods_icon/soldout-1.png);">SOLD OUT</strong>
			# </a>
			# </div>
			#
			####################################
			soldout_div_list = product_ctx.find_all('div', class_='item_icon_box')
			for soldout_div_ctx in soldout_div_list :
				img_list = soldout_div_ctx.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs ) :
						if(0 < img_ctx.attrs['src'].find('soldout') ) : product_data.crw_is_soldout = 1
					

			if( product_data.crw_is_soldout != 1 ) :
				soldout_div_list = product_ctx.find_all('div', class_='item_photo_box')
				for soldout_div_ctx in soldout_div_list :
					img_list = soldout_div_ctx.find_all('strong', class_='item_soldout_bg')
					for img_ctx in img_list :
						product_data.crw_is_soldout = 1


			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="item_tit_box">
			# <a href="../goods/goods_view.php?goodsNo=1000001614">
			# <strong class="item_name">빅독 리틀 바이트 사료 - 악어고기 100g</strong>
			# </a>
			# </div>
			#
			####################################
			name_strong_list = product_ctx.find_all('div', class_='item_tit_box')
			for name_strong_ctx in name_strong_list :
				product_link_list = name_strong_ctx.find_all('a')
				for product_link_ctx in product_link_list :

					if('href' in product_link_ctx.attrs ) : 
						span_list = product_link_ctx.find_all('strong')
						for span_ctx in span_list :
							product_data.crw_name = span_ctx.get_text().strip()

							
						tmp_product_link = product_link_ctx.attrs['href'].strip()
						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')
					
						split_list = crw_post_url.split('?goodsNo=')
						product_data.crw_goods_code = split_list[1].strip()
			
			
			####################################
			# 가격
			#
			# <div class="item_money_box">
			# <strong class="item_price">
			# <span>23,000원 </span>
			# </strong>
			# </div>
			#
			####################################
			
			div_list = product_ctx.find_all('div', class_='item_money_box')
			for div_ctx in div_list :
				del_ctx = div_ctx.find('del')
				strong_ctx = div_ctx.find('strong', class_='item_price')
				if( del_ctx != None ) : product_data.crw_price = int( __UTIL__.get_only_digit( del_ctx.get_text().strip() ) )
				if( strong_ctx != None ) : 
					# 타임세일일때  뒷부분의 별도의 값이 붙어서, 값 이상 문제 해결법, 
					crw_price_sale = strong_ctx.get_text().strip().split('\n')
					product_data.crw_price_sale = int( __UTIL__.get_only_digit( crw_price_sale[0].strip() ))
					
			
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
			
			detail_page_txt = []
			detail_page_img = []

		
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			####################################
			# 상품 기본 정보에서 브랜드 등을 추출
			####################################
		
			crw_brand = []
			
			if( self.SET_PRODUCT_DETAIL_DATA_DL ) :
				dl_list = soup.select( self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR )
				rtn_dict = self.get_value_in_dl_dtdd( dl_list)
				if(rtn_dict.get('브랜드' , -1) != -1) :
					crw_brand.append( rtn_dict['브랜드'] )
					
				if(rtn_dict.get('제조사' , -1) != -1) :
					crw_brand.append( rtn_dict['제조사'] )
					
				if(rtn_dict.get('원산지' , -1) != -1) :
					crw_brand.append( rtn_dict['원산지'] )
			
			else :
			
				li_list = soup.select( self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR )
				for li_ctx in li_list :
					strong_ctx = li_ctx.find('strong')
					div_ctx = li_ctx.find('div')
					if(strong_ctx != None) :
						title_name = strong_ctx.get_text().strip()
						if( 0 == title_name.find( '브랜드')) : crw_brand.append( div_ctx.get_text().strip() )
						elif( 0 == title_name.find( '제조사')) : crw_brand.append( div_ctx.get_text().strip() )
						elif( 0 == title_name.find( '원산지')) : crw_brand.append( div_ctx.get_text().strip() )
			
			
			if( self.SET_PRODUCT_DETAIL_DATA_TABLE) :
				#
				# 상품상세페이지 설명에 있는 테이블 내용중에 내용 추출
				#
				table_list = soup.select( self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR )
				rtn_dict = self.get_value_in_table_two_colume( table_list, '', 'th', 'td')
				if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
				if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )	
				
				
			
			self.set_detail_brand( product_data, crw_brand )
			
			
			
			####################################
			# 상품상세설명에서 이미지 및 텍스트 추출
			####################################
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR, self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR, 'src' )
			
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	

	
	