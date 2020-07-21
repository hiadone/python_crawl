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
from mall.Mall import Mall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class MakeShop(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)
		
		self.XCODE_HASH = {}
		self.MCODE_HASH = {}
		
		#
		# - 물품 리스트
		# 	카테고리를 추출시 추출하는 타입이 select 일때 True 이며
		# 	h1/h2 에서 추출할때는 False 이다.
		#self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = True
		
		#
		# - 물품 리스트
		# 	카테고리를 추출시 CLASS NAME
		
		self.SET_CATEGORY_DATA_X_CODE_SELECTOR = ''
		self.SET_CATEGORY_DATA_M_CODE_SELECTOR = ''
		
		#self.SET_PRODUCT_DATA_CATEGORY_CLASS_NAME = ''
				
		#
		# - 물품 리스트
		# 	카테고리를 추출시 HTML 요소 
		# self.SET_PRODUCT_DATA_CATEGORY_CLASS_SELECT_TYPE = FALSE 일때 사용
		#self.SET_PRODUCT_DATA_CATEGORY_TEXT_SELECTOR = ''
		
		#
		# - 물품 상세 페이지
		# 	상품기본 정보 DL SELECTOR 
		# DL/DT 타입 : self.SET_PRODUCT_DETAIL_DATA_DL = True
		# LI 타입 : self.SET_PRODUCT_DETAIL_DATA_DL = False
		#
		#self.SET_PRODUCT_DETAIL_DATA_DL = True
		
		#self.SET_PRODUCT_DETAIL_DATA_DL_SELECTOR = ''
		
		
		#
		# - 물품 상세 페이지
		# 	물품 상세 설명에서 이미지와 글이 포함된 DIV SELECTOR 
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR = ''
		
		self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR_SECOND = ''
		
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
	# URL 에서 카테고리 값을 표현하는 xcode , mcode 값을 얻어서,
	# 카테고리명을 self.XCODE_HASH dict 에 저장하는 함수들
	#
	######################################################################
	'''
	
	def get_category_value( self, product_data, crw_post_url ) :
		#
		# 입력 : 물품 URL
		# 출력 : 카테고리명
		#
		try :

			xcode_key , mcode_key = self.get_xcode_mcode( crw_post_url )
			key = '%s-%s' % ( xcode_key, mcode_key )
			
			if(self.MCODE_HASH.get(key, -1) != -1) :
				product_data.crw_category1  = self.MCODE_HASH[key]
				if(self.XCODE_HASH.get(xcode_key, -1) != -1) : product_data.crw_category2  = self.XCODE_HASH[xcode_key] 
			else :
				if(self.XCODE_HASH.get(xcode_key, -1) != -1) : product_data.crw_category1  = self.XCODE_HASH[xcode_key]
			
		except Exception as ex :
			__LOG__.Trace(ex)
			pass
	
	def get_xcode_mcode(self, crw_post_url) :
		#
		# 물품 URL에서 xcode, mcode 값 추출
		# 입력 : 물품 URL
		# 출력 : xcode , mcode 값
		#
		xcode_key = ''
		mcode_key = ''
		
		try :
			split_list = crw_post_url.split('xcode=')
						
			sub_split_list = split_list[1].strip().split('&')
			xcode_key = sub_split_list[0].strip()
			
			second_split_list = split_list[1].split('mcode=')
			last_split_list = second_split_list[1].split('&')
			mcode_key = last_split_list[0].strip()
			
		except :
			pass

		return xcode_key, mcode_key
		
	
	def set_param_category(self, html) :
		#
		# self.XCODE_HASH : 상위 카테고리명 dict , dict key는 xcode 3자리
		#
		# self.MCODE_HASH : 하위 카테고리명 dict dict key는 xcode,mcode 조합 ( xxx-mmm )
		#
		try :
			soup = bs4.BeautifulSoup(html, 'lxml')
			xcode_link_list = soup.select( self.SET_CATEGORY_DATA_X_CODE_SELECTOR )
			mcode_link_list = soup.select( self.SET_CATEGORY_DATA_M_CODE_SELECTOR )
			
			for mcode_link_ctx in mcode_link_list :
				if('href' in mcode_link_ctx.attrs) :
					link_str = mcode_link_ctx.attrs['href']
					if(0 < link_str.find('mcode=')) :

						xcode_key , mcode_key = self.get_xcode_mcode( link_str )
						
						mcode_name = mcode_link_ctx.get_text().strip()
						key = '%s-%s' % ( xcode_key, mcode_key )
						if(self.MCODE_HASH.get(key, -1) == -1 ) : self.MCODE_HASH[key] = mcode_name
						
			for xcode_link_ctx in xcode_link_list :
				if('href' in xcode_link_ctx.attrs) :
					link_str = xcode_link_ctx.attrs['href']
					if(0 < link_str.find('xcode=')) :
					
						xcode_key , mcode_key = self.get_xcode_mcode( link_str )
						self.XCODE_HASH[xcode_key] = xcode_link_ctx.get_text().strip()
						
						#m_key = '%s-000' % ( xcode_key)
						#if(self.MCODE_HASH.get(m_key, -1) == -1 ) : self.MCODE_HASH[m_key] = xcode_link_ctx.get_text().strip()
						
			
			#for key in self.MCODE_HASH.keys() :
			#	__LOG__.Trace('%s : %s' % (key, self.MCODE_HASH[key]) )

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return True
		
	'''
	######################################################################
	#
	# URL 에서 물품번호를 얻는 함수
	#
	######################################################################
	'''
	def get_crw_goods_code( self, product_data, crw_post_url ) :
		#
		# 입력 : 물품 URL
		# 출력 : branduid 값
		#
		try :
			split_list = crw_post_url.split('?branduid=')
			second_split_list = split_list[1].split('&')
			product_data.crw_goods_code = second_split_list[0].strip()
			
		except Exception as ex :
			__LOG__.Trace(ex)
			pass
			
		


		
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
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
	
			if( self.SET_PRODUCT_DETAIL_DATA_TABLE ) :
				table_list = soup.select( self.SET_PRODUCT_DETAIL_DATA_TABLE_SELECTOR )
				
				rtn_dict = self.get_value_in_table( table_list, '상품 옵션', 'th', 'td', 0)
				if(rtn_dict.get('브랜드' , -1) != -1) : crw_brand.append( rtn_dict['브랜드'] )
				if(rtn_dict.get('제조사' , -1) != -1) : crw_brand.append( rtn_dict['제조사'] )	
				if(rtn_dict.get('원산지' , -1) != -1) : crw_brand.append( rtn_dict['원산지'] )
			
			self.set_detail_brand( product_data, crw_brand )
			
			# 제품 상세 부분
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR, self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR, 'src' )
			if(len(detail_page_img) == 0 ) : detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, self.SET_PRODUCT_DETAIL_DATA_DIV_SELECTOR_SECOND, self.SET_PRODUCT_DETAIL_DATA_TEXT_SELECTOR, 'src' )
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	
	
	