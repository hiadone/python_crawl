#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 31.

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

from model.ProductData import ProductData , CategoryData
from model.Cafe24Data import Cafe24Data

from mall.Mall import Mall


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class Cafe24(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)
		
		'''
		# Cafe24 전용 
		#
		'''
		self.ORG_SITE_HOME = ''
		
		self.REFERER_SUB_CATEGORY_STR = ''
		
		self.MAIN_CATEGORY_NO = 1
		
		self.SUB_CATEGORY_URL_HASH = {}
		
		# 물품 이미지 CSS selector 정의
		self.C_PRODUCT_IMG_SELECTOR = ''
		self.C_PRODUCT_IMG_SELECTOR_CLASSNAME = ''
		
		
		# 물품 SOLDOUT CSS selector 정의
		self.C_PRODUCT_SOLDOUT_SELECTOR = ''
		self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME = ''
		
	
	'''
	######################################################################
	#
	# process_category_list 함수 대체
	#
	# - Cafe24 관련 사이트에 사용함.
	# - 카테고리 리스트를 SubCategory 질의에서 갖고 오는 경우에 사용함.
	# - 카테고리 분류 요청에 따라 사용하지 않는 함수. 
	######################################################################
	'''
	
	def get_sub_category_data_in_category(self, html, parent_cate_list):
		# 
		# 특정 카테고리 값에 해당되는 카테고리만 검색
		rtn = False
		
		category_no_list = []
		
		category_hash_tmp = {}
		
		# 특정카테고리만 추출하기 위해 추가
		parent_category_hash_tmp = {}
		for parent_cate_value in parent_cate_list :
			parent_category_hash_tmp[str(parent_cate_value)] = 1
		
		category_list = json.loads( html )
		
		for category_ctx in category_list :
			try :
				#__LOG__.Trace('--------------------------------------------')
				category_name = ''
				category_param = ''
				category_design_page_url = ''
				category_no = 0
				category_parent_cate_no = ''
				for key in category_ctx :
					if(key == 'name') : category_name = category_ctx[key]
					elif(key == 'param') : category_param = category_ctx[key]
					elif(key == 'cate_no') : category_no = int(category_ctx[key])
					elif(key == 'parent_cate_no') : category_parent_cate_no = str(category_ctx[key])
					elif(key == 'design_page_url') : category_design_page_url = category_ctx[key]
					#__LOG__.Trace( '------------------%s : %s' % (key, category_ctx[key]  ) )
				
				if( parent_category_hash_tmp.get( category_parent_cate_no , -1) != -1) : 
					if( category_hash_tmp.get( category_no , -1) == -1) : 
						parent_category_hash_tmp[str(category_no)] = 1
						category_hash_tmp[category_no] = [category_parent_cate_no, category_name, category_param, category_design_page_url ]
						category_no_list.append(category_no)
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		category_no_list.sort(reverse=True)
		
		# 카테고리 depth 명 정의하기
		for category_no in category_no_list :
			category_depth_name = []

			if( category_hash_tmp.get( category_no , -1) != -1) : 
				p_category_no = int( category_hash_tmp[category_no][0] )
				category_name = category_hash_tmp[category_no][1]
				category_depth_name.append(category_name)
				if( category_hash_tmp.get( p_category_no , -1) != -1) : 
					pp_category_no = int( category_hash_tmp[p_category_no][0] )
					p_category_name = category_hash_tmp[p_category_no][1]
					category_depth_name.append(p_category_name)
					if( category_hash_tmp.get( pp_category_no , -1) != -1) : 
						ppp_category_no = int( category_hash_tmp[pp_category_no][0] )
						pp_category_name = category_hash_tmp[pp_category_no][1]
						category_depth_name.append(pp_category_name)
						if( category_hash_tmp.get( ppp_category_no , -1) != -1) : 
							ppp_category_name = category_hash_tmp[pp_category_no][1]
							category_depth_name.append(ppp_category_name)

			self.CATEGORY_DEPTH_HASH[category_no] = category_depth_name
			__LOG__.Trace('--------------------------------------------')			
			__LOG__.Trace(category_no)
			__LOG__.Trace(category_depth_name)
			
		for category_no in category_no_list :
			try :
				value_list = category_hash_tmp[category_no]
				__LOG__.Trace('--------------------------------------------')

				category_parent_cate_no = value_list[0]
				category_name = value_list[1]
				category_param = value_list[2]
				category_design_page_url = value_list[3]
				#__LOG__.Trace('%s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
				
				if(self.check_ignore_category_text( category_name ) ) and (self.check_ignore_category_text( category_parent_cate_no ) ) :
					__LOG__.Trace('OK : %s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
					tmp_category_link = '%s/%s%s' % ( self.BASIC_CATEGORY_URL, category_design_page_url, category_param  )
					category_link = tmp_category_link
					if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
					if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
						self.CATEGORY_URL_HASH[category_link] = category_name
						
						if( config.__DEBUG__ ) : __LOG__.Trace('%s : %s' % ( category_name, category_link ) )

						rtn = True
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
		
	def get_sub_category_data(self, html):
		rtn = False
		
		category_no_list = []
		
		category_hash_tmp = {}
		
		category_list = json.loads( html )
		
		for category_ctx in category_list :
			try :
				#__LOG__.Trace('--------------------------------------------')
				category_name = ''
				category_param = ''
				category_design_page_url = ''
				category_no = 0
				category_parent_cate_no = ''
				for key in category_ctx :
					if(key == 'name') : category_name = category_ctx[key]
					elif(key == 'param') : category_param = category_ctx[key]
					elif(key == 'cate_no') : category_no = int(category_ctx[key])
					elif(key == 'parent_cate_no') : category_parent_cate_no = str(category_ctx[key])
					elif(key == 'design_page_url') : category_design_page_url = category_ctx[key]
					#__LOG__.Trace( '------------------%s : %s' % (key, category_ctx[key]  ) )
				
				if( category_hash_tmp.get( category_no , -1) == -1) : 
					category_hash_tmp[category_no] = [category_parent_cate_no,category_name, category_param, category_design_page_url ]
					category_no_list.append(category_no)
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		category_no_list.sort(reverse=True)
		
		# 카테고리 depth 명 정의하기
		for category_no in category_no_list :
			category_depth_name = []

			if( category_hash_tmp.get( category_no , -1) != -1) : 
				p_category_no = int( category_hash_tmp[category_no][0] )
				category_name = category_hash_tmp[category_no][1]
				category_depth_name.append(category_name)
				if( category_hash_tmp.get( p_category_no , -1) != -1) : 
					pp_category_no = int( category_hash_tmp[p_category_no][0] )
					p_category_name = category_hash_tmp[p_category_no][1]
					category_depth_name.append(p_category_name)
					if( category_hash_tmp.get( pp_category_no , -1) != -1) : 
						ppp_category_no = int( category_hash_tmp[pp_category_no][0] )
						pp_category_name = category_hash_tmp[pp_category_no][1]
						category_depth_name.append(pp_category_name)
						if( category_hash_tmp.get( ppp_category_no , -1) != -1) : 
							ppp_category_name = category_hash_tmp[pp_category_no][1]
							category_depth_name.append(ppp_category_name)

			self.CATEGORY_DEPTH_HASH[category_no] = category_depth_name
			__LOG__.Trace('--------------------------------------------')			
			__LOG__.Trace(category_no)
			__LOG__.Trace(category_depth_name)
			
			
		for category_no in category_no_list :
			try :
				value_list = category_hash_tmp[category_no]
				__LOG__.Trace('--------------------------------------------')

				category_parent_cate_no = value_list[0]
				category_name = value_list[1]
				category_param = value_list[2]
				category_design_page_url = value_list[3]
				__LOG__.Trace('%s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
				category_depth_name = self.CATEGORY_DEPTH_HASH[category_no]
				top_category = len(category_depth_name) -1
				
				if(self.check_ignore_category_text( category_name ) ) and (self.check_ignore_category_text( category_parent_cate_no ) )  and ( self.check_ignore_category_text(category_depth_name[top_category])):
					__LOG__.Trace('OK : %s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
					tmp_category_link = '%s/%s%s' % ( self.BASIC_CATEGORY_URL, category_design_page_url, category_param  )
					category_link = tmp_category_link
					if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
					if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
						self.CATEGORY_URL_HASH[category_link] = category_name
						
						if( config.__DEBUG__ ) : __LOG__.Trace('%s : %s' % ( category_name, category_link ) )

						rtn = True
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
		
	
	
	def get_header_subcategory(self):
	
		split_list = self.SITE_HOME.replace('http://','').replace('https://','').strip().split('/')
	
		host_str = split_list[0].strip()
		
		header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
			'Accept-Encoding': 'gzip, deflate' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'max-age=0' , \
			'Connection': 'keep-alive' , \
			'Cookie': self.COOKIE_STR , \
			'Host': host_str , \
			'Upgrade-Insecure-Requests': '1' , \
			'User-Agent': self.USER_AGENT } 
			
		if( self.REFERER_SUB_CATEGORY_STR != '' ) :
			header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
				'Accept-Encoding': 'gzip, deflate' , \
				'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
				'Cache-Control': 'max-age=0' , \
				'Connection': 'keep-alive' , \
				'Cookie': self.COOKIE_STR , \
				'Host': host_str , \
				'Referer': self.REFERER_SUB_CATEGORY_STR , \
				'Upgrade-Insecure-Requests': '1' , \
				'User-Agent': self.USER_AGENT } 
			
			
		return header
		
	
	'''
	#
	# - 카테고리 분류 요청에 따라 사용하지 않는 함수. 
	'''
	
	def process_sub_category_list(self):

		__LOG__.Trace("********** process_sub_category_list ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.CATEGORY_URL_HASH = None
			self.CATEGORY_URL_HASH = {}
		
			time.sleep(self.WAIT_TIME)
			
			URL = self.SITE_HOME + '/exec/front/Product/SubCategory'
			header = self.get_header_subcategory()
			
			resp = None
			resp = requests.get( URL, headers=header , verify=False)
			
			if(self.EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 인코딩
			
			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_sub_category_data( resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_sub_category_list Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn
	


	
	




	'''
	###########################################
	# Mall.py 대체
	#
	# 화면상의 카테고리 메뉴와 Cafe24의 SubCategory 와 상위 카테고리
	# 를 match 하여, 불필요한 카테고리에 대해 데이터 추출을 막는 부분
	#
	###########################################
	'''
	def web_get_category_data_second_in_img(self, html):
		rtn = False
		
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)
		
		__LOG__.Trace('web category : %d' % len(category_link_list) )
		if( len(category_link_list) == 0) : __LOG__.Trace( html )
		
		for category_ctx in category_link_list :
			try :
				category_name = category_ctx.get_text().strip()
							
				# 링크에 텍스트가 없고, 이미지가 있음.
				# 이미지의 alt 값이 해당 텍스트와 동일함
				img_ctx = category_ctx.find('img')
				if(img_ctx != None) :
					if('alt' in img_ctx.attrs) : category_name = img_ctx.attrs['alt'].strip()
					elif('title' in img_ctx.attrs) : category_name = img_ctx.attrs['title'].strip()
								
				if(self.check_ignore_category_text( category_name ) ) :
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(tmp_category_link.find('javascript') < 0 ) :
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )

							category_link = tmp_category_link
							
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')


							if( self.WEB_CATEGORY_NAME_HASH.get( category_link , -1) == -1) : 
								self.WEB_CATEGORY_NAME_HASH[category_name] = category_link
								if( config.__DEBUG__ ) :
									__LOG__.Trace('WEB 카테고리 %s : %s' % ( category_name, category_link ) )

								rtn = True


			except Exception as ex:
				__LOG__.Error(ex)
				pass

		if(config.__DEBUG__) : __LOG__.Trace( 'WEB 카테고리 수 : %d' % len(self.WEB_CATEGORY_NAME_HASH))
		
		return rtn


		
		
	def web_get_category_data_second(self, html):
		rtn = False
		
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)
		
		__LOG__.Trace('web category : %d' % len(category_link_list) )
		#if( len(category_link_list) == 0) : __LOG__.Trace( html )
		
		for category_ctx in category_link_list :
			try :
				if(self.check_ignore_category( category_ctx ) ) :
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(tmp_category_link.find('javascript') < 0 ) :
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )
							
							#category_link = self.get_hangul_url_convert( tmp_category_link )
							category_link = tmp_category_link
							
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
							category_name = category_ctx.get_text().strip()
							if( self.WEB_CATEGORY_NAME_HASH.get( category_link , -1) == -1) : 
								self.WEB_CATEGORY_NAME_HASH[category_name] = category_link
								if( config.__DEBUG__ ) :
									__LOG__.Trace('WEB 카테고리 %s : %s' % ( category_name, category_link ) )

								rtn = True


			except Exception as ex:
				__LOG__.Error(ex)
				pass

		if(config.__DEBUG__) : __LOG__.Trace( 'WEB 카테고리 수 : %d' % len(self.WEB_CATEGORY_NAME_HASH))
		
		return rtn

		
	def web_process_category_list_second(self):

		__LOG__.Trace("********** web_process_category_list_second ***********")
		
		rtn = False
		resptext = ''
		
		try :
		
			time.sleep(self.WAIT_TIME)
			
			URL = self.get_url_category_list()
			header = self.get_header()
			
			__LOG__.Trace( URL )
			
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
				rtn = self.web_get_category_data_second( resptext )
			
		except Exception as ex:
			__LOG__.Error( "web_process_category_list_second Error 발생 " )
			__LOG__.Error( ex )
			pass
			
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
	
	def get_sub_category_data_second(self, html):
		rtn = False
		
		category_list = json.loads( html )
		
		for category_ctx in category_list :
			try :
				__LOG__.Trace('--------------------------------------------')
				category_name = ''
				category_param = ''
				category_design_page_url = ''
				category_no = 0
				category_parent_cate_no = ''
				for key in category_ctx :
					if(key == 'name') : category_name = category_ctx[key].replace('<span>','').replace('</span>','').strip()
					elif(key == 'param') : category_param = category_ctx[key]
					elif(key == 'cate_no') : category_no = int(category_ctx[key])
					elif(key == 'parent_cate_no') : category_parent_cate_no = str(category_ctx[key])
					elif(key == 'design_page_url') : category_design_page_url = category_ctx[key]
					__LOG__.Trace( '------------------%s : %s' % (key, category_ctx[key]  ) )
				
				if( self.SUB_CATEGORY_URL_HASH.get( category_no , -1) == -1) : 
					self.SUB_CATEGORY_URL_HASH[category_no] = [category_parent_cate_no,category_name, category_param, category_design_page_url ]
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		
		
		if(config.__DEBUG__) : __LOG__.Trace( 'SUB 카테고리 수 : %d' % len(self.SUB_CATEGORY_URL_HASH))
		
		return rtn
		
		
		
	def process_sub_category_list_second(self):

		__LOG__.Trace("********** process_sub_category_list ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.SUB_CATEGORY_URL_HASH = None
			self.SUB_CATEGORY_URL_HASH = {}
		
			time.sleep(self.WAIT_TIME)
			
			len_domain = len(self.SITE_HOME.split('/'))
			
			URL = self.SITE_HOME + '/exec/front/Product/SubCategory'
			
			if( 3 < len_domain ) :
				URL = self.ORG_SITE_HOME + '/exec/front/Product/SubCategory'
			
			header = self.get_header_subcategory()
			
			__LOG__.Trace(URL)
			__LOG__.Trace(header)
			resp = None
			resp = requests.get( URL, headers=header , verify=False)
			
			if(self.EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 인코딩
			
			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_sub_category_data_second( resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_sub_category_list Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
	def process_category_list_second(self):

		__LOG__.Trace("********** process_category_list_second ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.CATEGORY_URL_HASH = None
			self.CATEGORY_URL_HASH = {}
		
			self.web_process_category_list_second()
			
			self.process_sub_category_list_second()

			#self.SUB_CATEGORY_URL_HASH[category_no] = [category_parent_cate_no,category_name, category_param, category_design_page_url ]
			main_category_hash = {}
			#main_category_list = []
			
			for category_no in self.SUB_CATEGORY_URL_HASH.keys() :
				main_value_list = self.SUB_CATEGORY_URL_HASH[int(category_no)]
				#__LOG__.Trace('%d-%d-%s' % ( int(main_value_list[0]), self.MAIN_CATEGORY_NO, main_value_list[1] ) )
				if( int(main_value_list[0]) == self.MAIN_CATEGORY_NO ) and ( self.WEB_CATEGORY_NAME_HASH.get(main_value_list[1], -1) != -1 ):
					if( self.check_ignore_category_text( main_value_list[1] ) ) :
						__LOG__.Trace('%d : %d : %s : %s : %s' % ( int(main_value_list[0]), category_no, main_value_list[1], main_value_list[2], main_value_list[3] ) )
						main_category_hash[category_no] = self.SUB_CATEGORY_URL_HASH[category_no]
						#main_category_list.append(category_no)
					
			sub_category_hash = {}	
			#sub_category_list = []
			
			for category_no in self.SUB_CATEGORY_URL_HASH.keys() :
				sub_value_list = self.SUB_CATEGORY_URL_HASH[category_no]
				if( main_category_hash.get(int(sub_value_list[0]), -1) != -1 ):
					if( self.check_ignore_category_text( sub_value_list[1] ) ) :
						main_category_list = main_category_hash[int(sub_value_list[0])]					
						__LOG__.Trace('%d : %d : %s : %s : %s' % ( int(sub_value_list[0]), category_no, sub_value_list[1], sub_value_list[2], sub_value_list[3] ) )
						category_name = '%s|%s' % ( main_category_list[1], sub_value_list[1] )
						sub_category_hash[category_no] = [sub_value_list[0],category_name, sub_value_list[2], sub_value_list[3] ]
						#sub_category_list.append(category_no)
					
			
			detail_category_hash = {}	
			#detail_category_list = []
			
			for category_no in self.SUB_CATEGORY_URL_HASH.keys() :
				detail_value_list = self.SUB_CATEGORY_URL_HASH[category_no]
				if( sub_category_hash.get(int(detail_value_list[0]), -1) != -1 ):
					if( self.check_ignore_category_text( detail_value_list[1] ) ) :
						sub_category_list = sub_category_hash[int(detail_value_list[0])]
						__LOG__.Trace('%d : %d : %s : %s : %s' % ( int(detail_value_list[0]), category_no, detail_value_list[1], detail_value_list[2], detail_value_list[3] ) )
						category_name = '%s|%s' % ( sub_category_list[1], detail_value_list[1] )
						detail_category_hash[category_no] = [detail_value_list[0],category_name, detail_value_list[2], detail_value_list[3] ]
						#detail_category_list.append(category_no)
					
			self.set_category_url_second( detail_category_hash )
			self.set_category_url_second( sub_category_hash )
			self.set_category_url_second(  main_category_hash )
			
		except Exception as ex:
			__LOG__.Error( "process_category_list_second Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn





	def set_category_url_second(self, category_hash_tmp ) :

		for category_no in category_hash_tmp.keys() :
			try :
				value_list = category_hash_tmp[category_no]
				__LOG__.Trace('-------------------set_category_url_second -------------------------')

				category_parent_cate_no = value_list[0]
				category_name = value_list[1]
				category_param = value_list[2]
				category_design_page_url = value_list[3]
				__LOG__.Trace('%s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
				
				if( self.CATEGORY_DEPTH_HASH.get( category_no , -1) == -1) : self.CATEGORY_DEPTH_HASH[category_no] = category_name
						
				if(self.check_ignore_category_text( category_name ) ) and (self.check_ignore_category_text( category_parent_cate_no ) ) :
					__LOG__.Trace('OK : %s %s %s %s' % (category_parent_cate_no, category_name, category_param, category_design_page_url ))
					tmp_category_link = '%s/%s%s' % ( self.BASIC_CATEGORY_URL, category_design_page_url, category_param  )
					category_link = tmp_category_link
					if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
					if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
						self.CATEGORY_URL_HASH[category_link] = category_name
						
						if( config.__DEBUG__ ) : __LOG__.Trace('%s : %s' % ( category_name, category_link ) )

						rtn = True
			
			except Exception as ex:
				__LOG__.Error(ex)
				pass



				
				
	

	
	'''
	######################################################################
	#
	# 카테고리 데이터를 추출하는 함수
	#
	######################################################################
	'''
	
	'''
	def set_product_category_third(self,  product_data, soup) :
			
		for tag in soup.find_all("meta"):
			if tag.get("property", None) == 'og:title' :
				rtn = tag.get('content', None)
				if(rtn != None) :
					if(0 < rtn.find('-') ) :
						split_list = rtn.split('-')
						idx = -1
						for split_data in split_list :
							if(split_data.strip() != '' ) :
								idx += 1
								if(idx == 0 ) : product_data.crw_category1 = split_data.strip()
								elif(idx == 1 ) : product_data.crw_category2 = split_data.strip()
								elif(idx == 2 ) : product_data.crw_category3 = split_data.strip()
		
	'''
	
	def set_product_category_second(self,  page_url, product_data, soup) :
		self.reset_product_category(product_data)
		
		category_no = 0
		if(0 < page_url.find('?cate_no=') ) :
			split_list = page_url.split('?cate_no=')
			sub_split_list = split_list[1].split('&')
			category_no = int(sub_split_list[0])
			
		elif(0 < page_url.find('/category/') ) :
			split_list = page_url.split('/')
			category_no = int(split_list[5])
			
		category_list = self.CATEGORY_DEPTH_HASH[category_no]
		category_depth_name = category_list.split('|')
		category_len = len(category_depth_name)
		
		if( category_len == 1 ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			
		elif( category_len == 2 ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			product_data.crw_category2 = category_depth_name[1].strip()
			
		elif( 3 <= category_len ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			product_data.crw_category2 = category_depth_name[1].strip()
			product_data.crw_category3 = category_depth_name[2].strip()

	'''
	def set_product_category_first(self,  product_data, soup) :
		for tag in soup.find_all("meta"):
			if tag.get("property", None) == 'og:description' :
				rtn = tag.get('content', None)
				if(rtn != None) :
					product_data.crw_category1 = rtn.strip()
	'''


	'''
	######################################################################
	#
	# 이미지 추출 함수들
	#
	######################################################################
	'''
	def set_product_image_first(self, product_data, product_ctx ) :
		#
		# 다른 html 요소 에 class name이 있고 , 그안에 이미지가 있는 경우
		#
		img_div_list = product_ctx.find_all(self.C_PRODUCT_IMG_SELECTOR, class_= self.C_PRODUCT_IMG_SELECTOR_CLASSNAME )
			
		for img_div_ctx in img_div_list :
			img_list = img_div_ctx.find_all('img')
			for img_ctx in img_list :
				if('src' in img_ctx.attrs ) :
					img_src = img_ctx.attrs['src'].strip()
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )

	
	def set_product_image_second(self, product_data, product_ctx ) :
		#
		# img 에 class name이 있는 경우
		#
		img_div_list = product_ctx.find_all(self.C_PRODUCT_IMG_SELECTOR, class_=self.C_PRODUCT_IMG_SELECTOR_CLASSNAME )
			
		for img_div_ctx in img_div_list :
			if('src' in img_div_ctx.attrs ) :
				img_src = img_div_ctx.attrs['src'].strip()
				if( img_src != '' ) :
					img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
					if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )
					
	
	def set_product_image_third(self, product_data, product_ctx ) :
		#
		# 다른 html 요소 에 class name이 있고 , 그안에 A 링크 안에 이미지가 있는 경우
		#
		img_div_list = product_ctx.find_all(self.C_PRODUCT_IMG_SELECTOR, class_= self.C_PRODUCT_IMG_SELECTOR_CLASSNAME )
			
		for img_div_ctx in img_div_list :
			a_link_ctx = img_div_ctx.find('a')
			if(a_link_ctx != None) :
				img_list = a_link_ctx.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs ) :
						img_src = img_ctx.attrs['src'].strip()
						if( img_src != '' ) :
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )	


	def set_product_image_fourth(self, product_data, product_ctx ) :
		#
		# 다른 html 요소 에 class name이 있고 , 그안에 A 링크 안에 이미지가 있는 경우
		#
		img_div_list = product_ctx.find_all(self.C_PRODUCT_IMG_SELECTOR, class_= self.C_PRODUCT_IMG_SELECTOR_CLASSNAME )
			
		for img_div_ctx in img_div_list :
			a_link_list = img_div_ctx.find_all('a')
			for a_link_ctx in a_link_list :
				if('name' in a_link_ctx.attrs) :
					if(0 <= a_link_ctx.attrs['name'].find('anchorBoxName')) :
						img_list = a_link_ctx.find_all('img')
						for img_ctx in img_list :
							if('src' in img_ctx.attrs ) :
								img_src = img_ctx.attrs['src'].strip()
								if( img_src != '' ) :
									img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
									if(product_data.product_img == '' ) : product_data.product_img = self.get_hangul_url_convert( img_link )	
	
	
	'''
	######################################################################
	#
	# 품절여부 데이터를 추출하는 함수
	#
	######################################################################
	'''
	def set_product_soldout_first(self, product_data, product_ctx ) :
		# 품절여부 확인
		soldout_div_list = product_ctx.find_all(self.C_PRODUCT_SOLDOUT_SELECTOR, class_= self.C_PRODUCT_SOLDOUT_SELECTOR_CLASSNAME)
		for soldout_div_ctx in soldout_div_list :
			img_list = soldout_div_ctx.find_all('img')
			for img_ctx in img_list :
				if('alt' in img_ctx.attrs ) :
					if( img_ctx.attrs['alt'].strip() == '품절') : product_data.crw_is_soldout = 1
					
	'''
	######################################################################
	#
	# 상품명 및 crw_goods_code 데이터를 추출하는 함수
	#
	######################################################################
	'''	
	
	def set_product_name_url_first(self, product_data, product_ctx , name_ctx_css, name_ctx_css_class) :
		#
		# crw_post_url 안에 ?product_no= 가 들어가 있는 경우
		# http://carmineproject.com/product/detail.html?product_no=59&cate_no=27&display_group=1
		# 
		# 상품명이 <a><strong><span>상품명</span></strong><span>"상품명"</span></a> 타입
		# 
		#
		# <p class="name">
		# <a href="/product/detail.html?product_no=195&amp;cate_no=55&amp;display_group=1"><span style="font-size:12px;color:#555555;">[공구상품]알로하 원피스</span></a><br><span class="zoom"><img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/btn_prd_zoom.gif" onclick="zoom('195', '55', '1','', '');" style="cursor:pointer" alt="상품 큰 이미지 보기"></span>
		# </p>
		#-----------------------------------------------------
		#
		# <p class="name">
		# <a href="/product/detail.html?product_no=286&amp;cate_no=43&amp;display_group=1"><strong class="title displaynone"><span style="font-size:12px;color:#555555;">상품명</span> :</strong> <span style="font-size:12px;color:#555555;">Frill Neck Sleeve Blouse Lavender [20%SALE]</span></a>
		# </p>
		#
		
		crw_post_url = ''

		try :

			name_div_list = product_ctx.find_all(name_ctx_css, class_=name_ctx_css_class)
			
			for name_div_ctx in name_div_list :
				
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :
					
					if('href' in product_link_ctx.attrs ) : 
						span_list = product_link_ctx.find_all('span')
						for span_ctx in span_list :
							name_value = span_ctx.get_text().strip()
							
							if(0 != name_value.find('상품명') ) and (0 != name_value.find(':') ) : 
								if(product_data.crw_name == '') : product_data.crw_name = name_value
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()

						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						split_list = crw_post_url.split('?product_no=')
						crw_goods_code_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = crw_goods_code_list[0].strip()

						
		except Exception as ex :
			__LOG__.Error( ex )
			pass
		
		return crw_post_url

	
		
	def set_product_name_url_second(self, product_data, product_ctx , name_ctx_css, name_ctx_css_class) :
		#
		# crw_post_url 안에 /product/ 가 들어가 있는 경우
		#
		# http://amor-ange.com/product/safari-padding-navy/67/category/25/display/1/
		# 
		crw_post_url = ''

		try :

			name_div_list = product_ctx.find_all(name_ctx_css, class_=name_ctx_css_class)
			
			for name_div_ctx in name_div_list :
				
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :
					
					if('href' in product_link_ctx.attrs ) : 
						span_list = product_link_ctx.find_all('span')
						for span_ctx in span_list :
							name_value = span_ctx.get_text().strip()
							
							if(0 != name_value.find('상품명') ) and (0 != name_value.find(':') ) : product_data.crw_name = name_value
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()

						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						split_list = crw_post_url.split('/')
						if( product_data.crw_name == '') : product_data.crw_name = split_list[4].strip()
						product_data.crw_goods_code = split_list[5].strip()

						
		except Exception as ex :
			__LOG__.Error( ex )
			pass
		
		return crw_post_url

		
	def set_product_name_url_third(self, product_data, product_ctx , name_ctx_css, name_ctx_css_class) :
		#
		# crw_post_url 안에 ?product_no= 가 들어가 있는 경우
		# http://carmineproject.com/product/detail.html?product_no=59&cate_no=27&display_group=1
		# 
		# 상품명이 <a><span>상품명</span>"상품명"</a> 타입
		#
		# <a href="/product/detail.html?product_no=140&amp;cate_no=25&amp;display_group=1" class=""><span class="title displaynone"><span style="font-size:12px;color:#555555;font-weight:bold;">상품명</span> :</span> 코코넛칠면조베지스틱</a>
		#
		crw_post_url = ''

		try :

			name_div_list = product_ctx.find_all(name_ctx_css, class_=name_ctx_css_class)
			
			for name_div_ctx in name_div_list :
				
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :
					
					if('href' in product_link_ctx.attrs ) : 
						name_value = product_link_ctx.get_text().strip()
						if(0 <= name_value.find('상품명') ) and (0 < name_value.find(':') ) : 
							split_list = name_value.split(':') 
							if(product_data.crw_name == '') : product_data.crw_name = split_list[1].strip()
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()

						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						split_list = crw_post_url.split('?product_no=')
						crw_goods_code_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = crw_goods_code_list[0].strip()

						
		except Exception as ex :
			__LOG__.Error( ex )
			pass
		
		return crw_post_url		
		
		
	def set_product_name_url_fourth(self, product_data, product_ctx , name_ctx_css, name_ctx_css_class) :
		#
		# crw_post_url 안에 ?product_no= 가 들어가 있는 경우
		# http://carmineproject.com/product/detail.html?product_no=59&cate_no=27&display_group=1
		# 
		# 상품명이 <a><span>"상품명"</span></a> 타입
		#
		# <p class="name"><a href="/product/detail.html?product_no=123&amp;cate_no=24&amp;display_group=1"><span style="font-size:12px;color:#555555;">애견 수제 간식 영양식 호박죽 화식</span></a></p>
		#
		crw_post_url = ''

		try :

			name_div_list = product_ctx.find_all(name_ctx_css, class_=name_ctx_css_class)
			
			for name_div_ctx in name_div_list :
				
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_list = name_div_ctx.find_all('a')
				for product_link_ctx in product_link_list :
					
					if('href' in product_link_ctx.attrs ) : 
						name_value = product_link_ctx.get_text().strip()
						if(product_data.crw_name == '') : product_data.crw_name = name_value
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()

						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						split_list = crw_post_url.split('?product_no=')
						crw_goods_code_list = split_list[1].strip().split('&')
						product_data.crw_goods_code = crw_goods_code_list[0].strip()

						
		except Exception as ex :
			__LOG__.Error( ex )
			pass
		
		return crw_post_url	

	
	def set_product_name_url_fifth(self, product_data, product_ctx , name_ctx_css, name_ctx_css_class) :
		#
		# crw_post_url 안에 /product/ 가 들어가 있는 경우
		#
		# http://amor-ange.com/product/safari-padding-navy/67/category/25/display/1/
		# 
		crw_post_url = ''

		try :

			name_div_list = product_ctx.find_all(name_ctx_css, class_=name_ctx_css_class)
			
			for name_div_ctx in name_div_list :
				
				#
				# 상품 링크 정보 및 상품명 / 상품코드
				#
				product_link_ctx = name_div_ctx.find('a')
				if(product_link_ctx != None) :
					
					if('href' in product_link_ctx.attrs ) : 
						span_list = product_link_ctx.find_all('span')
							
						tmp_product_link = product_link_ctx.attrs['href'].strip()

						if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs['href'].strip() )
						crw_post_url = tmp_product_link

						if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

						split_list = crw_post_url.split('/')
						if( product_data.crw_name == '') : product_data.crw_name = split_list[4].strip()
						product_data.crw_goods_code = split_list[5].strip()

						
		except Exception as ex :
			__LOG__.Error( ex )
			pass
		
		return crw_post_url
		
	'''
	######################################################################
	#
	# 브랜드 데이터를 추출하는 함수
	#
	######################################################################
	'''					
	def set_product_price_brand_first(self, product_data, name_div_ctx ) :
		li_list = name_div_ctx.find_all('li')
		for li_ctx in li_list :
			strong_ctx = li_ctx.find('strong')
			span_ctx = li_ctx.find_all('span')
			if(strong_ctx != None) :
				if(1 < len(span_ctx) ) :
					title_name = strong_ctx.get_text().strip()
					split_list = span_ctx[1].get_text().strip().split('(')
					value_str = split_list[0].strip()
					if( 0 == title_name.find( '브랜드')) : product_data.crw_brand1 = value_str
					elif( 0 == title_name.find( '제조사')) : product_data.crw_brand2 = value_str
					elif( 0 == title_name.find( '판매가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif( 0 == title_name.find( '할인판매가')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ))
					elif( 0 == title_name.find( 'SALE')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ))
	
	
	def set_product_price_brand_second(self, product_data, name_div_ctx ) :
		li_list = name_div_ctx.find_all('li')
		for li_ctx in li_list :
		
			strong_ctx = li_ctx.find('strong')
			span_ctx = li_ctx.find_all('span')
			if(strong_ctx != None) :
				if(1 < len(span_ctx) ) :
					title_name = strong_ctx.get_text().strip()
					split_list = span_ctx[1].get_text().strip().split('(')
					value_str = split_list[0].strip()

					if( 0 == title_name.find( '브랜드')) : product_data.crw_brand1 = value_str
					elif( 0 == title_name.find( '제조사')) : product_data.crw_brand2 = value_str
					elif( 0 == title_name.find( '소비자가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif( 0 == title_name.find( '권장 소비자가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif( 0 == title_name.find( '판매가')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ))

				
	def set_product_price_brand_third(self, product_data, name_div_ctx ) :
		li_list = name_div_ctx.find_all('li')
		for li_ctx in li_list :
			strong_ctx = li_ctx.find('strong')
			span_ctx = li_ctx.find_all('span')
			if(strong_ctx != None) :
				if(1 < len(span_ctx) ) :
					title_name = strong_ctx.get_text().strip()
					split_list = span_ctx[1].get_text().strip().split('(')
					value_str = split_list[0].strip()
					if( 0 == title_name.find( '브랜드')) : product_data.crw_brand1 = value_str
					elif( 0 == title_name.find( '판매가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif( 0 == title_name.find( '상품요약정보')) : 
						span_str = span_ctx[1].get_text().strip()
						if(0 <= span_str.find('할인')) or (0 <= span_str.find('이벤트')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( span_str ))	

	
	'''
	######################################################################
	#
	# Cafe24 전용으로 이미지의 attrs 값이 변동에 대처하기 위해 src / ec-data-src
	# 에서 모두 구함.
	#
	######################################################################
	'''						
	def get_cafe24_text_img_in_detail_content_part(self, soup, product_data, content_selector, text_sub_selector, img_selector='img' ) :
		try :

			detail_page_txt = []
			detail_page_img = []
			tmp_detail_page_img = []
			
			# 제품 상세 부분
			# 상세이미지 경로 수정 필요.
			#
			# http://gi.esmplus.com/no1jhk/%25E2%2598%2585%2520%25ED%258E%25AB%2520%25EB%25A6%25AC%25EB%2589%25B4%25EC%2596%25BC_170901/%25EC%2595%25A0%25EA%25B2%25AC%25EC%259A%25A9%25ED%2592%2588/%25ED%258F%25AC%25EC%25BC%2593%25EB%25B0%2594%25EB%259E%258C%25EB%25A7%2589%25EC%259D%25B4.jpg
			#
			detail_page_txt, tmp_detail_page_img = self.get_text_img_in_detail_content_part( soup, content_selector, text_sub_selector, 'src' )
			for detail_img in tmp_detail_page_img :
				if( 0 <= detail_img.find('%25') ) : detail_page_img.append( detail_img.replace('%25','%') )
				else : detail_page_img.append( detail_img )
				
			detail_page_txt, tmp_detail_page_img = self.get_text_img_in_detail_content_part( soup, content_selector, text_sub_selector, 'ec-data-src' )

			for detail_img in tmp_detail_page_img :
				if( 0 <= detail_img.find('%25') ) : detail_page_img.append( detail_img.replace('%25','%') )
				else : detail_page_img.append( detail_img )
				
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		

	
	'''
	######################################################################
	#
	# 추출한 데이터를 product_data에 값을 입력하는 함수
	#
	######################################################################
	'''	
	def set_product_url_hash(self, product_data, crw_post_url) :
	
		#if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
		
		self.set_product_data_sub( product_data, crw_post_url )
		self.process_product_api(product_data)
			
	

	
	
	'''	
	#################################################################################
	##
	## www.betterskorea.com 사이트에만 사용함
	##
	##	카페24에서 상품 상세페이지의 내용을 갖고 오는 API
	##  return 값은 jsondata 로 넘겨준다.

	Request URL: http://www.betterskorea.com/api/v2/products/5359
	Request Method: GET
	Status Code: 200 OK
	Remote Address: 183.111.163.238:80
	Referrer Policy: no-referrer-when-downgrade

	Access-Control-Allow-Origin: *
	Cache-Control: no-store, no-cache, must-revalidate
	Connection: keep-alive
	Content-Length: 71730
	Content-Type: application/json; charset=utf-8
	Date: Fri, 22 May 2020 06:40:29 GMT
	Expires: Thu, 19 Nov 1981 08:52:00 GMT
	P3P: CP="NOI ADM DEV PSAi COM NAV OUR OTR STP IND DEM"
	Pragma: no-cache
	Server: nginx
	X-Api-Call-Limit: 0/30
	x-cache-valid: YES
	X-Cafe24-Api-Version: 2019-12-11
	X-Trace_ID: 491b5828f4393f67a29cd73f08444bfd
	X-XSS-Protection: 1;mode=block

	Accept: */*
	Accept-Encoding: gzip, deflate
	Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6
	Connection: keep-alive
	Cookie: atl_epcheck=1; atl_option=1%2C1%2CH; CUK45=cuk45_shopbetters_660884afb43dba0e99b8eb4c6fbed555; CUK2Y=cuk2y_shopbetters_660884afb43dba0e99b8eb4c6fbed555; CID=CIDac53e5111054cdfbe37ac878fd7e1520; wish_id=aaf9e2265799239d92838332377e4771; wishcount_1=0; ch-veil-id=915ebbcb-773d-4780-b867-9d5385d96f8c; ECSESSID=8f6d49ec6fb026998d2ce720f0234421; CIDac53e5111054cdfbe37ac878fd7e1520=996d67f8908c4872fefdbbaae6bba3ba%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%2F%3A%3A1590122667%3A%3A%3A%3Appdp%3A%3A1590122667%3A%3A%3A%3A%3A%3A%3A%3A; isviewtype=pc; basketprice_1=0%EC%9B%90; basketcount_1=0; view_product_map=a%3A1%3A%7Bi%3A1%3Ba%3A3%3A%7Bi%3A0%3Bi%3A11507%3Bi%3A1%3Bi%3A11535%3Bi%3A2%3Bi%3A5359%3B%7D%7D; recent_plist=11507%7C11535%7C5359; ch-session-13247=eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzZXMiLCJrZXkiOiIxMzI0Ny01ZWM3MzFmMGE4MDk5NGRjYWExNCIsImlhdCI6MTU5MDEyOTI5NiwiZXhwIjoxNTkyNzIxMjk2fQ.epItLJYVs0pjdJj1hpKLHn0xpahRo1S3lR8jQ3PzMGE; vt=1590129628
	Host: www.betterskorea.com
	Referer: http://www.betterskorea.com/product/detail.html?product_no=5359&cate_no=883&display_group=1
	User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
	X-Cafe24-App-Key: iJf0852OYiGZTznb7gXaEG

	{"product":{"shop_no":1,"product_no":5359,"category":[{"category_no":48,"recommend":"F","new":"F"},{"category_no":901,"recommend":"F","new":"F"},{"category_no":1027,"recommend":"F","new":"F"},{"category_no":883,"recommend":"F","new":"F"},{"category_no":26,"recommend":"F","new":"F"}],"project_no":null,"product_code":"P0000HYC","custom_product_code":"","product_name":"\uc9c0\ucea3 \ube0c\ub8e9\ud074\ub9b0 \uace0\uc591\uc774\uc6a9 \ubaa9\uc904","eng_product_name":"","model_name":"","price_excluding_tax":"9091.00","price":"10000.00","retail_price":"10000.00","display":"T","description":"<h1 style='margin: 0px; padding: 0px 0px 30px; width: 1000px; color: rgb(51, 51, 51); line-height: 35px; letter-spacing: 1px; font-family: \"Noto Sans Korean\", sans-serif; font-size: 14px; font-weight: normal;'>DETAIL INFO<\/h1><p style='color: rgb(85, 85, 85); font-family: \ub098\ub214\uace0\ub515, NanumGothic, \"Nanum Gothic\"; font-size: 11px;'><b style=\"color: rgb(99, 99, 99); font-family: Tahoma; font-size: 9pt;\"><span style=\"font-size: 14pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">ZEE.CAT I BROOKLYN COLLAR<\/span><\/span><\/span><\/b><\/p><div style='margin: 0px; padding: 0px; color: rgb(85, 85, 85); font-family: \ub098\ub214\uace0\ub515, NanumGothic, \"Nanum Gothic\"; font-size: 11px;'><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><span class=\"s1\" style=\"font-kerning: none;\"><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-family: helvetica;\">Light, Discreet, and Innovative<\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \ubd80\ub4dc\ub7fd\uace0 \ud2bc\ud2bc\ud55c Teteron Polyester \uc18c\uc7ac\ub97c \uc0ac\uc6a9\ud558\uc5ec \ubaa9\ubd80\ubd84\uc758 \uc790\uadf9\uc744 \ucd5c\uc18c\ud654\ud574\uc90d\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- Breakway Buckle\uc744 \uc0ac\uc6a9\ud558\uc5ec \ubcf4\ub2e4 \uc548\uc804\ud558\uace0 \uc2e0\uc18d\ud558\uac8c \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \ub0b4\uad6c\uc131\uc744 \uace0\ub824\ud558\uc5ec \uace0\ubb34\ub85c \ub9cc\ub4e0 \uc9c0\ub3c5 \ub85c\uace0\uac00<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;&nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc2a4\ud2f0\uce58 \ubd80\ubd84\uc744 \ub354\uc6b1 \ud2bc\ud2bc\ud558\uac8c \ubcf4\ud638\ud574\uc90d\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc9c0\ub3c5\ub9cc\uc758 \uc6e8\ube59\uae30\uc220\ub85c \uc5b4\ub5a0\ud55c \uae30\ud6c4\uc5d0\ub3c4 \uc790\uc720\ub86d\uac8c \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-family: helvetica;\">Size Chart &nbsp;<\/span><\/span><\/span><\/span><\/span><\/b><\/span><b style=\"font-size: 9pt;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 9pt;\">\uc0ac\uc774\uc988\ubcc4 \ub108\ube44\/\uae38\uc774<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><b><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">ONE SIZE&nbsp;<\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"color: rgb(99, 99, 99); font-family: helvetica; font-size: 13.33px;\">1cm \/ 20 - 30cm<\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><b><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc18c\uc7ac<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;\ud3f4\ub9ac\uc5d0\uc2a4\ud14c\ub974, \uace0\ubb34<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><br><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 12pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Measuring Tape? No Worries &nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 9pt;\">\ud3b8\ub9ac\ud55c \uce21\uc815 \ubc29\ubc95<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">1. \ub85c\ud504, \uc904, \ubca8\ud2b8 \ub4f1\uc744 \uc0ac\uc6a9\ud558\uc5ec \uac15\uc544\uc9c0\uc758 \ubaa8\ub4e0 \uce58\uc218\ub97c \uce21\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4(\uc904\uc790\uac00 \uc5c6\uc5b4\ub3c4 \uce21\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4)<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">2. \uce21\uc815\ud55c \uae38\uc774\ub294 \uc2e0\uc6a9\uce74\ub4dc, \uc6b4\uc804\uba74\ud5c8\uc99d, \ud639\uc740 \uad50\ud1b5\uce74\ub4dc\ub85c \ud655\uc778\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\ub300\ubd80\ubd84 \uce74\ub4dc\uc758 \uae38\uc774\ub294 8.5 cm\uc774\uba70, \uc608\ub97c \ub4e4\uc5b4, \uce28\uc815 \uae38\uc774\uac00 \uce74\ub4dc 3\uac1c\uba74, \ub300\ub7b5 25.5 cm\uac00 \ub429\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><div style=\"margin: 0px; padding: 0px;\"><br><\/div><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 14pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Size Tutorial<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/zd_cat_size_shop1_154719.jpg\"><\/p><p>&nbsp;<\/p><br><p><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span style=\"color: rgb(99, 99, 99); font-family: Tahoma; font-size: 18.66px; font-weight: bold;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Features<\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/cat_collar_buckle_zeecat_feature_carousel_4cdb76a2-0c73-4fd8-a680-4ad38a0a27e2_1024x1024_shop1_154433.gif\"><\/p><p><\/p><p><br><\/p><p><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/zd_cat_collar_brooklyn_1024_shop1_162028.jpg\"><\/p><p>&nbsp;<\/p><p><\/p><p><\/p><p><\/p><p><\/p><div style=\"margin: 0px; padding: 0px;\"><p><\/p><\/div><p><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc0ac\uc6a9 \uc2dc \uc8fc\uc758\uc0ac\ud56d<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">1. \ubcf8 \uc81c\ud488\uc740 \ubc18\ub824\ub3d9\ubb3c\uc6a9\uc785\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">2. \uc6a9\ub3c4 \uc678 \uc0ac\uc6a9\uc744 \uae08\ud569\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">3. \uc5b4\ub9b0\uc544\uc774\uac00 \uac00\uc9c0\uace0 \uc7a5\ub09c\ud558\uc9c0 \uc54a\ub3c4\ub85d \uc8fc\uc758\ud558\uc2ed\uc2dc\uc624.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">4. \ud654\uae30\ub97c \ud53c\ud558\uc2ed\uc2dc\uc624.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">5. \uc0ac\uc6a9 \uc804\uc5d0\ub294 \ubc18\ub4dc\uc2dc \uac80\uc0ac\ud558\uc5ec \uc190\uc0c1 \uc5ec\ubd80\ub97c \ud655\uc778\ud558\uc138\uc694.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">6. \ubc18\ubcf5\uc801\uc73c\ub85c \uc2ec\ud558\uac8c \ub04c\uc5b4\ub2f9\uaca8 \ubb34\ub9ac\ub97c \uc8fc\uc9c0 \ub9c8\uc138\uc694.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><br><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><br><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">NOTICE<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc0c1\ud488 \uc0c9\uc0c1\uc740 \uc0ac\uc6a9\ud558\uc2dc\ub294 \ubaa8\ub2c8\ud130\uc758 \ud574\uc0c1\ub3c4\uc5d0 \ub530\ub77c \uc2e4\uc81c \uc0c9\uc0c1\uacfc \uc870\uae08\uc529 \ub2e4\ub974\uac8c \ubcf4\uc77c \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc77c\ubd80 \uc81c\ud488\uc758 \uacbd\uc6b0, \ubd80\ubd84 \ubc18\ud488 \ubc0f \uad50\ud658\uc740 \uc81c\ud55c\ub420 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><\/div>","mobile_description":"<h1 style='margin: 0px; padding: 0px 0px 30px; width: 1000px; color: rgb(51, 51, 51); line-height: 35px; letter-spacing: 1px; font-family: \"Noto Sans Korean\", sans-serif; font-size: 14px; font-weight: normal;'>DETAIL INFO<\/h1><p style='color: rgb(85, 85, 85); font-family: \ub098\ub214\uace0\ub515, NanumGothic, \"Nanum Gothic\"; font-size: 11px;'><b style=\"color: rgb(99, 99, 99); font-family: Tahoma; font-size: 9pt;\"><span style=\"font-size: 14pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">ZEE.CAT I BROOKLYN COLLAR<\/span><\/span><\/span><\/b><\/p><div style='margin: 0px; padding: 0px; color: rgb(85, 85, 85); font-family: \ub098\ub214\uace0\ub515, NanumGothic, \"Nanum Gothic\"; font-size: 11px;'><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><span class=\"s1\" style=\"font-kerning: none;\"><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-family: helvetica;\">Light, Discreet, and Innovative<\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \ubd80\ub4dc\ub7fd\uace0 \ud2bc\ud2bc\ud55c Teteron Polyester \uc18c\uc7ac\ub97c \uc0ac\uc6a9\ud558\uc5ec \ubaa9\ubd80\ubd84\uc758 \uc790\uadf9\uc744 \ucd5c\uc18c\ud654\ud574\uc90d\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- Breakway Buckle\uc744 \uc0ac\uc6a9\ud558\uc5ec \ubcf4\ub2e4 \uc548\uc804\ud558\uace0 \uc2e0\uc18d\ud558\uac8c \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \ub0b4\uad6c\uc131\uc744 \uace0\ub824\ud558\uc5ec \uace0\ubb34\ub85c \ub9cc\ub4e0 \uc9c0\ub3c5 \ub85c\uace0\uac00<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;&nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc2a4\ud2f0\uce58 \ubd80\ubd84\uc744 \ub354\uc6b1 \ud2bc\ud2bc\ud558\uac8c \ubcf4\ud638\ud574\uc90d\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc9c0\ub3c5\ub9cc\uc758 \uc6e8\ube59\uae30\uc220\ub85c \uc5b4\ub5a0\ud55c \uae30\ud6c4\uc5d0\ub3c4 \uc790\uc720\ub86d\uac8c \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-family: helvetica;\">Size Chart &nbsp;<\/span><\/span><\/span><\/span><\/span><\/b><\/span><b style=\"font-size: 9pt;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 9pt;\">\uc0ac\uc774\uc988\ubcc4 \ub108\ube44\/\uae38\uc774<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><b><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">ONE SIZE&nbsp;<\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"color: rgb(99, 99, 99); font-family: helvetica; font-size: 13.33px;\">1cm \/ 20 - 30cm<\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><b><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc18c\uc7ac<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;\ud3f4\ub9ac\uc5d0\uc2a4\ud14c\ub974, \uace0\ubb34<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><br><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 12pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Measuring Tape? No Worries &nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 9pt;\">\ud3b8\ub9ac\ud55c \uce21\uc815 \ubc29\ubc95<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">1. \ub85c\ud504, \uc904, \ubca8\ud2b8 \ub4f1\uc744 \uc0ac\uc6a9\ud558\uc5ec \uac15\uc544\uc9c0\uc758 \ubaa8\ub4e0 \uce58\uc218\ub97c \uce21\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4(\uc904\uc790\uac00 \uc5c6\uc5b4\ub3c4 \uce21\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4)<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">2. \uce21\uc815\ud55c \uae38\uc774\ub294 \uc2e0\uc6a9\uce74\ub4dc, \uc6b4\uc804\uba74\ud5c8\uc99d, \ud639\uc740 \uad50\ud1b5\uce74\ub4dc\ub85c \ud655\uc778\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\ub300\ubd80\ubd84 \uce74\ub4dc\uc758 \uae38\uc774\ub294 8.5 cm\uc774\uba70, \uc608\ub97c \ub4e4\uc5b4, \uce28\uc815 \uae38\uc774\uac00 \uce74\ub4dc 3\uac1c\uba74, \ub300\ub7b5 25.5 cm\uac00 \ub429\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><div style=\"margin: 0px; padding: 0px;\"><br><\/div><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><b style=\"font-family: Tahoma; font-size: 16px;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 14pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Size Tutorial<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/zd_cat_size_shop1_154719.jpg\"><\/p><p>&nbsp;<\/p><br><p><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span style=\"color: rgb(99, 99, 99); font-family: Tahoma; font-size: 18.66px; font-weight: bold;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\">Features<\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><br><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/cat_collar_buckle_zeecat_feature_carousel_4cdb76a2-0c73-4fd8-a680-4ad38a0a27e2_1024x1024_shop1_154433.gif\"><\/p><p><\/p><p><br><\/p><p><img style=\"margin: 0px; padding: 0px; vertical-align: top;\" alt=\"\" src=\"http:\/\/www.andforpets.com\/web\/upload\/NNEditor\/20180203\/zd_cat_collar_brooklyn_1024_shop1_162028.jpg\"><\/p><p>&nbsp;<\/p><p><\/p><p><\/p><p><\/p><p><\/p><div style=\"margin: 0px; padding: 0px;\"><p><\/p><\/div><p><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">\uc0ac\uc6a9 \uc2dc \uc8fc\uc758\uc0ac\ud56d<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">1. \ubcf8 \uc81c\ud488\uc740 \ubc18\ub824\ub3d9\ubb3c\uc6a9\uc785\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">2. \uc6a9\ub3c4 \uc678 \uc0ac\uc6a9\uc744 \uae08\ud569\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">3. \uc5b4\ub9b0\uc544\uc774\uac00 \uac00\uc9c0\uace0 \uc7a5\ub09c\ud558\uc9c0 \uc54a\ub3c4\ub85d \uc8fc\uc758\ud558\uc2ed\uc2dc\uc624.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">4. \ud654\uae30\ub97c \ud53c\ud558\uc2ed\uc2dc\uc624.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">5. \uc0ac\uc6a9 \uc804\uc5d0\ub294 \ubc18\ub4dc\uc2dc \uac80\uc0ac\ud558\uc5ec \uc190\uc0c1 \uc5ec\ubd80\ub97c \ud655\uc778\ud558\uc138\uc694.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">6. \ubc18\ubcf5\uc801\uc73c\ub85c \uc2ec\ud558\uac8c \ub04c\uc5b4\ub2f9\uaca8 \ubb34\ub9ac\ub97c \uc8fc\uc9c0 \ub9c8\uc138\uc694.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><br><\/span><\/p><p class=\"p2\" style=\"line-height: normal; font-family: Helvetica; min-height: 13px; font-stretch: normal; -webkit-text-stroke-color: rgb(0, 0, 0);\"><span class=\"s1\" style=\"font-kerning: none;\"><br><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><b><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">NOTICE<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/b><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc0c1\ud488 \uc0c9\uc0c1\uc740 \uc0ac\uc6a9\ud558\uc2dc\ub294 \ubaa8\ub2c8\ud130\uc758 \ud574\uc0c1\ub3c4\uc5d0 \ub530\ub77c \uc2e4\uc81c \uc0c9\uc0c1\uacfc \uc870\uae08\uc529 \ub2e4\ub974\uac8c \ubcf4\uc77c \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">&nbsp;<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><p class=\"p1\"><span class=\"s1\" style=\"font-kerning: none;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 12pt;\"><span style=\"font-family: Verdana;\"><span style=\"font-family: Tahoma;\"><span style=\"font-family: Arial;\"><span style=\"font-family: Tahoma;\"><span style=\"color: rgb(125, 125, 125);\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"color: rgb(70, 70, 70);\"><span style=\"font-size: 10pt;\"><span style=\"font-family: \uad81\uc11c, Gungsuh;\"><span style=\"font-family: Tahoma;\"><span style=\"font-size: 10pt;\"><span style=\"color: rgb(99, 99, 99);\"><span style=\"font-size: 8pt;\"><span style=\"font-size: 10pt;\"><span style=\"font-size: 9pt;\"><span style=\"font-family: helvetica;\"><span style=\"font-size: 12pt;\"><span style=\"font-size: 10pt;\">- \uc77c\ubd80 \uc81c\ud488\uc758 \uacbd\uc6b0, \ubd80\ubd84 \ubc18\ud488 \ubc0f \uad50\ud658\uc740 \uc81c\ud55c\ub420 \uc218 \uc788\uc2b5\ub2c8\ub2e4.<\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/span><\/p><\/div>\t\t\t","separated_mobile_description":"F","additional_image":null,"payment_info":"<p><br><\/p>","shipping_info":"<p><br><\/p>","exchange_info":"<p><br><\/p>","service_info":"<p><br><\/p>","product_tax_type_text":null,"set_product_type":null,"selling":"T","product_used_month":null,"simple_description":"\uc9c0\ub3c5 \uc81c\ud488\uc73c\ub85c 50,000 \uc774\uc0c1\uc740 \ubb34\ub8cc\ubc30\uc1a1, 50,000 \ubbf8\ub9cc\uc740 \ubc30\uc1a1\ub8cc 2,500\uc6d0\uc774 \ucd94\uac00\ub429\ub2c8\ub2e4.","summary_description":"1027","product_tag":"\ubaa9\uc904,\uc0b0\ucc45\uc904,\uace0\uc591\uc774\ubaa9\uc904,\uc9c0\ub3c5\ubaa9\uc904,\uc0b0\ucc45,\uace0\uc591\uc774\uc0b0\ucc45","price_content":null,"buy_limit_by_product":"F","buy_limit_type":null,"repurchase_restriction":"F","single_purchase_restriction":"F","buy_unit_type":"O","buy_unit":1,"order_quantity_limit_type":"O","minimum_quantity":1,"maximum_quantity":0,"points_by_product":"F","points_setting_by_payment":null,"points_amount":null,"adult_certification":"F","detail_image":"http:\/\/wooof.co.kr\/web\/product\/big\/201802\/5359_shop1_566060.jpg","list_image":"http:\/\/wooof.co.kr\/web\/product\/medium\/201802\/5359_shop1_566060.jpg","tiny_image":"http:\/\/wooof.co.kr\/web\/product\/tiny\/201802\/5359_shop1_566060.jpg","small_image":"http:\/\/wooof.co.kr\/web\/product\/small\/201802\/5359_shop1_566060.jpg","has_option":"F","option_type":null,"use_naverpay":null,"naverpay_type":null,"manufacturer_code":"M00000JH","trend_code":"T0000000","brand_code":"B0000BAM","made_date":"","expiration_date":{"start_date":null,"end_date":null},"origin_classification":"F","origin_place_no":1798,"origin_place_value":"","made_in_code":"KR","icon_show_period":{"start_date":"2018-02-13T00:00:00+09:00","end_date":"2018-02-21T00:00:00+09:00"},"icon":null,"product_material":"","shipping_method":null,"prepaid_shipping_fee":null,"shipping_period":null,"shipping_scope":"A","shipping_area":null,"shipping_fee_type":null,"shipping_rates":null,"clearance_category_code":null,"origin_place_code":1798,"list_icon":{"soldout_icon":false,"recommend_icon":false,"new_icon":false},"additional_information":[{"key":"custom_option1","name":"DESCRIPTION","value":""}],"main":[3],"relational_product":[{"product_no":5355,"interrelated":"T"},{"product_no":5356,"interrelated":"T"},{"product_no":5357,"interrelated":"T"},{"product_no":5358,"interrelated":"T"}],"select_one_by_option":"F","approve_status":"","sold_out":"F"}}
	#################################################################################
	'''

	def get_data_cafe24_api_products_v2(self, cafe24_data, jsondata):
		rtn = False
		try :
			if('product' in jsondata) :			
				productdata = jsondata['product']
				for key in productdata :				
					if('product_no' in productdata ) : cafe24_data.product_no = productdata['product_no']
					if('product_name' in productdata ) : cafe24_data.product_name = productdata['product_name']
					if('price' in productdata ) : cafe24_data.price = productdata['price']
					if('retail_price' in productdata ) : cafe24_data.retail_price = productdata['retail_price']
					if('description' in productdata ) : cafe24_data.description = productdata['description']
					
					if('sold_out' in productdata ) : 
						if( productdata['sold_out'] != 'F') : cafe24_data.sold_out = True
				
		except Exception as ex :
			__LOG__.Error( "get_data_cafe24_api_products_v2 - Error")
			__LOG__.Error( ex)
			pass
	
		
	def send_cafe24_api_products_v2(self, api_key, site_url, product_id, product_url , COOKIE_STR, USER_AGENT ): 

		data = None
		res =  None
		rtn = False
		
		cafe24_data = Cafe24Data()
		try :
			site_home_list = site_url.replace('https://','').replace('http://','').split('/')
			site_home = site_home_list[0]
			
			header = { 'Accept': '*/*' , \
					'Accept-Encoding': 'gzip, deflate' , \
					'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
					'Connection': 'keep-alive' , \
					'Cookie': COOKIE_STR , \
					'Host': site_home , \
					'Referer': product_url , \
					'User-Agent': USER_AGENT, \
					'X-Cafe24-App-Key': api_key } 
					
			URL = '%s/api/v2/products/%s' % ( site_url, product_id)
		
			res = requests.get(URL, headers=header)
			if(res.status_code != 200) : __LOG__.Error( res.status_code )
			else: 
				data = json.loads(res.text)
				self.get_data_cafe24_api_products_v2(cafe24_data, data)

		except Exception as ex :
			__LOG__.Error( 'send_cafe24_api_products_v2' )
			__LOG__.Error( ex)
			pass
			

		return cafe24_data

			
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = Cafe24()
	app.test_process_sub_category_list()
	#app.send_cafe24_api_products_v2('iJf0852OYiGZTznb7gXaEG', 'http://www.betterskorea.com', '5359', 'http://www.betterskorea.com/product/detail.html?product_no=5359&cate_no=883&display_group=1' , 'JSESSIONID=T8vYyG9M1LW5dC_YyxEh8_TzQgLaIDn9ZmrYZ1hb3a8; page_uid=3e87e101923ea2be3c45e802b407a302', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357 Safari/537.36' )

