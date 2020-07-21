#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user
'''
import json
import time
import os, signal
import bs4
import sys
import warnings
import requests


from secrets import token_urlsafe, token_hex
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from urllib import parse

from app import config
from app import define_mall as __DEFINE__
from api import hiadone_api as __API__
from imagejob import img_merge as __IMGJOB__

import log as Log;  Log.Init()

from model.ProductData import ProductData
from browser.Browser import Browser

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class Mall(Browser) :    
        
	def __init__(self) :
	
		# Selenium 관련 상속
		Browser.__init__(self)
		
		# 신호처리
		signal.signal(signal.SIGTERM, self.Shutdown)
		signal.signal(signal.SIGINT, self.Shutdown)
		signal.signal(signal.SIGHUP, self.Shutdown)
		signal.signal(signal.SIGPIPE, self.Shutdown)
		
		self.SHUTDOWN = False
		
		self.WAIT_TIME = 0.5	# 1초
		
		# Request header 에서 사용되는 쿠키 및 User-Agent 정보
		self.COOKIE_STR = ''
		self.USER_AGENT = ''
		
		
		
		self.BRD_ID = 0				# mall id
		self.SPECIAL_CATEGORY = ''
		
		#
		# Request 질의에 대한 응답메시지의 encoding 지정 변수
		# EUC-KR / 'ISO-8859-1' 일때 일치하지 않으면 한글 깨짐.
		#
		# self.EUC_ENCODING = False : 일반적인 UTF-8
		# self.EUC_ENCODING = True  : EUC-KR 인코딩
		# self.EUC_ENCODING = None  : 'ISO-8859-1' 인코딩
		# 
		self.EUC_ENCODING = False
		

		# 카테고리 URL 저장 dict
		self.CATEGORY_URL_HASH = {}
		
		# 페이지 URL 저장 dict
		self.PAGE_URL_HASH = {}
		
		# 물품 URL 저장 dict
		self.PRODUCT_URL_HASH = {}
		
		
		#
		# 검색된 물품 URL 과 API에서 얻은 기존 물품 URL
		# 물품 DELETE 시 사용함.
		#
		self.PRODUCT_AVAIBLE_ITEM_HASH = {}	# 검색된 물품 리스트 dict
		self.PRODUCT_ITEM_HASH = {}	# API 에 얻은 물품 리스트 dict
		
		
		
		
		self.SITE_HOME = ''		# 처음 접속하는 사이트 URL
		
		
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		self.C_CATEGORY_VALUE = ''
		self.C_CATEGORY_VALUE_2 = ''
		
		self.C_CATEGORY_STRIP_STR = ''			# URL 에서 삭제할 String
		self.C_CATEGORY_IGNORE_STR = []			# 카테고리 중에 무시해야 하는 카테고리
		
		
		
		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		self.C_PAGE_VALUE = ''
		

		self.C_PAGE_STRIP_STR = ''			# URL 에서 삭제할 String
		self.C_PAGE_IGNORE_STR = []			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''
		self.C_PRODUCT_VALUE = ''
		
		self.C_PRODUCT_STRIP_STR = ''		# URL 에서 삭제할 String
		
		
		
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = ''
		
		
		self.PAGE_FIRST_URL = ''		# 페이지 링크에서 구분자의 앞 URL
		self.PAGE_SECOND_URL = ''		# 페이지 링크에서 구분자의 뒷 URL
		self.PAGE_SPLIT_STR = ''		# 페이지 링크에서 page를 구분할수 있는 구분자
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부
		self.PAGE_LAST_VALUE = 0		# 페이지 맨끝 링크의 값
		


		
		self.BASIC_CATEGORY_URL = '' 	# 사이트 카테고리 URL 링크 정보 앞에 추가적으로 붙이는 URL String
		self.BASIC_PAGE_URL = '' 	# 사이트 물품 URL 링크 정보 앞에 추가적으로 붙이는 URL String
		self.BASIC_PRODUCT_URL = '' 	# 사이트 물품 URL 링크 정보 앞에 추가적으로 붙이는 URL String
		self.BASIC_IMAGE_URL = '' 	# 사이트 이미지 URL 링크 정보 앞에 추가적으로 붙이는 URL String


	
	
	def Shutdown(self, sigNum=0, frame=0) :
		print ("Recv Signal(%d)" % sigNum)
		self.SHUTDOWN = True


	'''
	##########################################
	# request 에서 사용되는 Header 겂
	##########################################
	'''
	def get_header(self):
	
		header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Connection': 'keep-alive' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Upgrade-Insecure-Requests': '1' , \
			'User-Agent': self.USER_AGENT } 

		return header
		
	'''
	##########################################
	# 쿠키 값을 시작시 임의로 생성하는 함수
	##########################################
	'''	
	def set_cookie(self) :
		token = token_urlsafe(32)
		token_2 = token_hex(16)
		self.COOKIE_STR = 'JSESSIONID=' + token + '; page_uid=' + token_2
		if(config.__DEBUG__) : __LOG__.Trace('%s' % (self.COOKIE_STR) )
	
	
	'''
	##########################################
	# User-Agent 값을 시작시 임의로 생성하는 함수
	##########################################
	'''	
	def set_user_agent(self) :

		software_names = [SoftwareName.CHROME.value]
		#operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
		operating_systems = [OperatingSystem.WINDOWS.value]

		user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

		# Get list of user agents.
		#user_agents = user_agent_rotator.get_user_agents()

		# Get Random User Agent String.
		self.USER_AGENT = user_agent_rotator.get_random_user_agent()
		if(config.__DEBUG__) : __LOG__.Trace('%s' % (self.USER_AGENT) )
	

	'''
	##########################################
	# self.SITE_HOME 값을 시작시 임의로 생성하는 함수
	#
	# smartstore 및 shopnaver에서 사용함
	##########################################
	'''	
	def set_site_home(self, URL ) :
		self.SITE_HOME = URL
		
		
	def set_ignore_category(self, CATEGORY_IGNORE_STR ) :
		self.C_CATEGORY_IGNORE_STR = CATEGORY_IGNORE_STR
		
	
	def set_detail_brand(self, product_data, crw_brand ) :
	
		for idx in range(len(crw_brand)) :
			if(idx == 0) : product_data.d_crw_brand1 = crw_brand[idx]
			elif(idx == 1) : product_data.d_crw_brand2 = crw_brand[idx]
			elif(idx == 2) : product_data.d_crw_brand3 = crw_brand[idx]
			elif(idx == 3) : product_data.d_crw_brand4 = crw_brand[idx]
			elif(idx == 4) : product_data.d_crw_brand5 = crw_brand[idx]
	
	
	def get_strip_string(self, before_str, first_split, second_split , replace_str_list) :
		#
		# before_str : 추출 원문자열
		# first_split : 첫번째 split 인자
		# second_split : 두번째 split 인자
		# strip_str : 추출된 문자열에서 공백으로 replace 시켜야 하는 문자열 리스트
		#
		# 사용예 : get_strip_basic( before_str, '_nao['pnm'] =', '";' , ['"'])
		# _nao['pnm'] = "하이포닉 고양이, 강아지 워터리스 샴푸 190ml"; --> 하이포닉 고양이, 강아지 워터리스 샴푸 190ml
		#
		after_replace_str = ''
		split_list = before_str.split(first_split)
		if(1 < len(split_list)) :
			tmp_str = split_list[1]
			del_pos  = tmp_str.find(second_split) # - 1
			after_replace_str = tmp_str[:del_pos]
			for replace_str in replace_str_list :
				tmp_replace_str = after_replace_str.replace(replace_str, '').strip()
				after_replace_str = tmp_replace_str

		return after_replace_str
		
	def get_value_in_list(self, object_list) :
		rtn = ''
		for object_ctx in object_list :
			rtn = object_ctx.get_text().strip()
		
		return rtn

	def get_first_value_in_list(self, object_list) :
		rtn = ''
		for object_ctx in object_list :
			rtn = object_ctx.get_text().strip()
			break
		
		return rtn
	
	'''	
	def get_detail_text_with_strip(self, detail_text) :
		rtn_data = []
		split_list = detail_text.split('\n')

		for split_ctx in split_list :
			split_data = split_ctx.replace('\xa0',' ').strip()
			if(split_data != '') : 
				#__LOG__.Trace( '--------------------------------------------' )
				#__LOG__.Trace(split_data)
				if(split_data.find('<span') < 0 ) and (split_data.find('</span>') < 0 ) and (split_data.find(' font:') < 0 ) and (split_data.find(' font-size:') < 0 ) and (split_data.find('<style') < 0 ) : rtn_data.append( split_data )
				#rtn_data.append( split_data )
			
		return ' '.join(rtn_data)
	'''
	
		
	def get_detail_text_with_strip(self, detail_text) :			
		return detail_text
		
		
	
	'''
	##########################################
	# 한글 URL을 Request에 사용할수 있도록 변경하는 함수
	##########################################
	'''	
	def get_hangul_url_convert(self, hangul_url) :
		rtn_url = hangul_url
		ignore_pos = hangul_url.find('://')
		if( 0 < ignore_pos ) :
			cvt_url = parse.quote(hangul_url[ignore_pos+3:])
			rtn_url = hangul_url[:ignore_pos+3] + cvt_url
		return rtn_url

		
	'''
	##########################################
	# 불완전한 이미지 URL를 완전한 형태의 URL로 변경하는 함수
	#
	# 불완전한 URL : ./upload/a.jpg
	# 완전한 URL   : http://www.xxxx.com/upload/a.jpg
	##########################################
	'''	
	def get_crw_post_url(self, product_link_ctx, attrs_value) :
		crw_post_url = ''
		tmp_product_link = product_link_ctx.attrs[attrs_value].strip()
		if( tmp_product_link.find('javascript') < 0 ) :
			if(0 != tmp_product_link.find('http')) : tmp_product_link = '%s%s' % ( self.BASIC_PRODUCT_URL, product_link_ctx.attrs[attrs_value].strip() )
			crw_post_url = tmp_product_link

			if(self.C_PRODUCT_STRIP_STR != '') : crw_post_url = tmp_product_link.replace( self.C_PRODUCT_STRIP_STR,'')

		return crw_post_url
		
		
	'''
	##########################################
	# 불완전한 이미지 URL를 완전한 형태의 URL로 변경하는 함수
	#
	# 불완전한 URL : ./upload/a.jpg
	# 완전한 URL   : http://www.xxxx.com/upload/a.jpg
	##########################################
	'''	
	def set_img_url(self, img_basic_url, img_org_src) :
		
		# 이미지 파일명에 "?" 뒤에 옵션 있는 것을 제거하기.
		img_src = img_org_src
		if(0 <= img_org_src.find('https://proxy.smartstore.naver.com')) : 
			img_src = img_org_src
		else :
			split_list = img_org_src.split('?')
			img_src = split_list[0].strip()
			
		#elif(0 <= img_org_src.find('https://ifh.cc')) : 
		#	split_list = img_org_src.split('/')
		#	if(5 <= len(split_list) ) : 
		#		sub_split_list = split_list[4].split('.')
		#		img_src = 'https://ifh.cc/v-%s' % (sub_split_list[0].strip())

		
		#img_link = '%s%s' % ( self.BASIC_IMAGE_URL, img_src )
		img_link = '%s%s' % ( img_basic_url, img_src )
		if(0 == img_src.strip().find('http') ) : img_link = img_src
		elif(0 == img_src.strip().find('//') ) : 
			split_list = img_basic_url.split('//')
			img_link = '%s%s' % ( split_list[0].strip(), img_src )

		return img_link
	
	
	'''
	##########################################
	# 상세페이지의 이미지 및 텍스트 값 설정 함수
	##########################################
	'''	
	
	def set_detail_page( self, product_data, detail_page_txt, detail_page_img) :
		self.set_detail_page_text( product_data, detail_page_txt )
		self.set_detail_page_img( product_data, detail_page_img )
	
	'''
	##########################################
	# 상세페이지의 텍스트 값 설정 함수
	##########################################
	'''	
	def set_detail_page_text( self, product_data, detail_page_txt ) :
		product_data.cdt_content = '\n'.join( detail_page_txt )
	
	'''
	##########################################
	# 상세페이지의 이미지 값 설정 함수
	##########################################
	'''	
	def set_detail_page_img( self, product_data, detail_page_img ) :
		product_data.detail_page_img = detail_page_img
		
	'''
	##########################################
	# 상품의 이미지 값 설정 함수
	##########################################
	'''
	def set_product_page_img( self, product_data, product_img ) :
		product_data.product_img = product_img
	
	
	'''
	######################################################################
	#
	# 상속 받는 프로그램에서 별도로 필요한 값을 추출하여, 사용할수 미리 생성해 놓음 함수
	# Mall.py 를 상속받은 프로그램에서 overwrite 사용함.
	#
	######################################################################
	'''
	def set_param_category(self, html ) :
	
		return True
	
	
	def set_param_page(self, html ) :
	
		return True

	def set_param_product(self, html ) :
	
		return True
		
	
		
	'''
	######################################################################
	# 카테고리 리스트를 갖고 오는 부분
	######################################################################
	'''
	def check_ignore_category(self , link_obj) :
		rtn = True
		link_text = link_obj.get_text().strip()
		for ignore_category in self.C_CATEGORY_IGNORE_STR :
			if(ignore_category.strip() == link_text) :
				rtn = False
				break
		
		# text 가 아닌 이미지로 되어 있을때, <a> 의 href 값으로 무시하는 것을 추가함.
		#
		if( 'href' in link_obj.attrs ) :
			link_href = link_obj.attrs['href'].strip()
			
			for ignore_page in self.C_CATEGORY_IGNORE_STR :
				if(ignore_page.strip() == link_href) :
					rtn = False
					break	
					
		return rtn
		
	
	def check_ignore_category_text(self , c_link_text) :
		rtn = True
		link_text = c_link_text.strip()
		for ignore_category in self.C_CATEGORY_IGNORE_STR :
			if(ignore_category.strip() == link_text) :
				rtn = False
				break
				
		return rtn
		
		
	
	def get_url_category_list(self) :
		return self.SITE_HOME
	
	
	
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
			if(self.C_CATEGORY_VALUE_2.strip() != '') : category_link_list_2 = soup.select(self.C_CATEGORY_VALUE_2)

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
					if('href' in category_ctx.attrs ) : 
						tmp_category_link = category_ctx.attrs['href']
						if(tmp_category_link.find('javascript') < 0 ) :
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )
							
							category_link = tmp_category_link
							
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
							
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
		
			time.sleep(self.WAIT_TIME)
			
			URL = self.get_url_category_list()
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
		

	'''
	######################################################################
	# 카테고리별로 페이지 URL을 얻는 함수
	######################################################################
	'''
	
	def check_ignore_page(self , link_obj) :
		rtn = True
		link_text = link_obj.get_text().strip()
		
		for ignore_page in self.C_PAGE_IGNORE_STR :
			if(ignore_page.strip() == link_text) :
				rtn = False
				break
		

		return rtn
		
	
	def get_page_url_split(self, page_link, is_last_page):

		if(self.PAGE_SPLIT_STR != '') and ( 0 < page_link.find(self.PAGE_SPLIT_STR) ) :
			split_data = page_link.split(self.PAGE_SPLIT_STR)
			
			self.PAGE_FIRST_URL = split_data[0]
			del_pos = split_data[1].find('&')
			if(del_pos < 0 ) : 
				self.PAGE_SECOND_URL = ''
				page_num = int( split_data[1] )
			else : 
				self.PAGE_SECOND_URL = split_data[1][del_pos:]
				page_num = int( split_data[1][:del_pos] )
			
			if(is_last_page) : 
				self.PAGE_LAST_VALUE = page_num
		


	def set_page_list_with_last_link(self, category_url):
		#
		# 
		# last page 값이 있어, page 숫자를 증가시켜 page url을 설정하는 부분
		#
		first_page = self.C_PAGE_COUNT_PER_DISPLAY + 1
		last_page = self.PAGE_LAST_VALUE + 1
		
		if(config.__DEBUG__) :
			__LOG__.Trace( 'self.PAGE_LAST_VALUE : %d' % (self.PAGE_LAST_VALUE)  )
			__LOG__.Trace( 'first_page : %d' % (first_page)  )
			__LOG__.Trace( 'last_page : %d' % (last_page)  )
			__LOG__.Trace( 'PAGE_FIRST_URL : %s' % (self.PAGE_FIRST_URL)  )
			__LOG__.Trace( 'PAGE_SPLIT_STR : %s' % (self.PAGE_SPLIT_STR)  )
			__LOG__.Trace( 'PAGE_SECOND_URL : %s' % (self.PAGE_SECOND_URL)  )
		
		for page in range( first_page, last_page ) :
		
			tmp_page_link = '%s%s%d%s' % ( self.PAGE_FIRST_URL, self.PAGE_SPLIT_STR , page, self.PAGE_SECOND_URL )
			
			# page url이 '?page=' 일때 처리
			if(( self.PAGE_FIRST_URL == '' ) or ( self.PAGE_FIRST_URL == self.SITE_HOME ) ) and (self.PAGE_SECOND_URL == '') : tmp_page_link = '%s%s%d' % ( category_url, self.PAGE_SPLIT_STR , page )
			
			page_link = tmp_page_link
			#page_link = self.get_hangul_url_convert( tmp_page_link )
			if(self.C_PAGE_STRIP_STR != '') : page_link = tmp_page_link.replace( self.C_PAGE_STRIP_STR,'')
			if( page_link.find('javascript') < 0 ) :
				if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
					self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
					if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )
					
	
	
	
	def get_page_list_with_request(self, html, category_url):
		avaible_page_count = 0
		page_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( self.C_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : page_link_list = soup.select(self.C_PAGE_VALUE)
			
				
		# 각 페이지 링크에 대한 처리
		for page_ctx in page_link_list :
			try :
				if(self.check_ignore_page( page_ctx ) ) :
					if('href' in page_ctx.attrs ) : 
						avaible_page_count += 1
						
						tmp_page_link = page_ctx.attrs['href']
						if(0 != tmp_page_link.find('http')) : tmp_page_link = '%s%s' % ( self.BASIC_PAGE_URL, page_ctx.attrs['href'] )
						
						page_link = tmp_page_link
						#page_link = self.get_hangul_url_convert( tmp_page_link )
						if(self.C_PAGE_STRIP_STR != '') : page_link = tmp_page_link.replace( self.C_PAGE_STRIP_STR,'')
						if( page_link.find('javascript') < 0 ) :
							if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
								self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
								if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )

			except Exception as ex:
				__LOG__.Error(ex)
				pass

		return avaible_page_count
		
	
	def set_page_list_with_request(self, category_url):
		#
		#
		# last page 값이 없을때, 화면당 표시되는 페이지수만큼 건너뛴 페이들을 계속해서, 질의하여 페이지를 얻어오는 부분
		#
		resptext = ''
		page = self.C_PAGE_COUNT_PER_DISPLAY + 1
		
		if(self.PAGE_SPLIT_STR != '') :
			while(True) :
				if(self.SHUTDOWN) : break
				avaible_page_count = 0
				try :
					page_url = '%s%s%d%s' % ( self.PAGE_FIRST_URL, self.PAGE_SPLIT_STR , page, self.PAGE_SECOND_URL )
					self.C_PAGE_IGNORE_STR.append(str(page))
					
					time.sleep(self.WAIT_TIME)
					URL = page_url
					header = self.get_header()
					
					resp = None
					resp = requests.get( URL, headers=header , verify=False)

					if( resp.status_code != 200 ) :
						__LOG__.Error(resp.status_code)
					else :
						resptext = resp.text
						avaible_page_count = self.get_page_list_with_request( resptext, category_url )
									
				except Exception as ex:
					__LOG__.Error( "set_page_list_with_request Error 발생 " )
					__LOG__.Error( ex )
					pass
					
				if(avaible_page_count == ( self.C_PAGE_COUNT_PER_DISPLAY -1) ) : page += self.C_PAGE_COUNT_PER_DISPLAY
				else : break
				


	def get_page_data(self, category_url, html):
		rtn = False
		
		self.set_param_page(html)
		
		page_link_list = []
		
		last_page_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( self.C_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : page_link_list = soup.select(self.C_PAGE_VALUE)

			
		if(self.PAGE_LAST_LINK) :
			if( self.C_LAST_PAGE_CASE == __DEFINE__.__C_SELECT__ ) : last_page_link_list = soup.select(self.C_LAST_PAGE_VALUE)
		
			# 맨끝 페이지 링크에 대한 처리
			for last_page_ctx in last_page_link_list :
				try :
					if('href' in last_page_ctx.attrs ) : 
						page_link = last_page_ctx.attrs['href']
						if(0 != page_link.find('http')) : page_link = '%s%s' % ( self.BASIC_PAGE_URL, last_page_ctx.attrs['href'] )
						
						if(0 < page_link.find( self.PAGE_SPLIT_STR )) : self.get_page_url_split( page_link , True )

				except Exception as ex:
					__LOG__.Error(ex)
					pass
		
		# 각 페이지 링크에 대한 처리
		avaible_page_count = 0
		for page_ctx in page_link_list :
			try :
				if(self.check_ignore_page( page_ctx ) ) :
					if('href' in page_ctx.attrs ) : 
						avaible_page_count += 1
						tmp_page_link = page_ctx.attrs['href']
						if(0 != tmp_page_link.find('http')) : 
							if( 0 == tmp_page_link.find('?page=') ) :			
								# 페이지 링크 정보가 '?page=' 로 시작되어 질때, 카테고리 URL을 추가해준다.
								tmp_page_link = '%s%s' % ( category_url, page_ctx.attrs['href'] )
							else : 
								tmp_page_link = '%s%s' % ( self.BASIC_PAGE_URL, page_ctx.attrs['href'] )
						
						page_link = tmp_page_link

						if(self.C_PAGE_STRIP_STR != '') : page_link = tmp_page_link.replace( self.C_PAGE_STRIP_STR,'')
						if( page_link.find('javascript') < 0 ) :
							if( self.PAGE_URL_HASH.get( page_link , -1) == -1) : 
								self.PAGE_URL_HASH[page_link] = self.CATEGORY_URL_HASH[category_url]
								if(self.PAGE_FIRST_URL == '' ) : self.get_page_url_split( page_link , False )
								rtn = True
								if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( page_link ) )

			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		
		
		return rtn , avaible_page_count
					
		
	def process_page(self, category_url):
	
		rtn = False
		resptext = ''
		avaible_page_count = 0
		
		try :
			# 카테고리 URL로 첫 화면에서 페이지 리스트를 얻어옴.
			# 초기화
			self.PAGE_FIRST_URL = ''		
			self.PAGE_SECOND_URL = ''
			self.PAGE_LAST_VALUE = 0
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
				
			# 나머지 페이지 리스트를 얻어옴.
			if(self.PAGE_LAST_LINK) : 
				# last page 값이 있어, page 숫자를 증가시켜 page url을 설정하는 부분
				self.set_page_list_with_last_link(category_url)
			elif(self.PAGE_LAST_LINK == False) and (avaible_page_count == ( self.C_PAGE_COUNT_PER_DISPLAY -1) ) : 
				# last page 값이 없을때, 화면당 표시되는 페이지수만큼 건너뛴 페이들을 계속해서, 질의하여 페이지를 얻어오는 부분
				self.set_page_list_with_request(category_url)
			
		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
		
		
	def process_page_list(self):

		__LOG__.Trace("********** process_page_list ***********")
		
		rtn = False
		resptext = ''
		
		self.PAGE_URL_HASH = None
		self.PAGE_URL_HASH = {}
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_PAGE_CASE )
			__LOG__.Trace( self.C_PAGE_VALUE )
			
		for category_url in self.CATEGORY_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			self.process_page( category_url )
		
		if(config.__DEBUG__) : __LOG__.Trace( '페이지 수 : %d' % len(self.PAGE_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn

	'''
	######################################################################
	# 상품 리스트 함수
	######################################################################
	'''
	
	
	def set_product_data_sub(self , product_data, crw_post_url) :
		##################
		#
		# 상품 데이터에 대한 최종 판단 및 보정하는 부분.
		#
		##################
		
		# 가격 보정, 원가격 또는 판매가격에 값이 없을때
		# 판매가격 = 원가격을 입력
		if( product_data.crw_price_sale == 0) : product_data.crw_price_sale = product_data.crw_price
		elif( product_data.crw_price == 0) : product_data.crw_price = product_data.crw_price_sale
		
		# 가격이 역전되어 추출되었을때 보정
		# 판매가격이 원가격 보다 높을때, 가격을 변경하여 저장함.
		if( product_data.crw_price < product_data.crw_price_sale ) :
			crw_price_sale = product_data.crw_price
			crw_price = product_data.crw_price_sale
			product_data.crw_price = crw_price
			product_data.crw_price_sale = crw_price_sale
			
		
		
		# 기존 상품정보가 입력되어 있을때 UPDATE Action 으로 변경.
		if(self.PRODUCT_ITEM_HASH.get(product_data.crw_goods_code, -1) != -1) : 
			product_data.crw_action = __DEFINE__.__UPDATE_CRW__
			product_data.crw_id = self.PRODUCT_ITEM_HASH[product_data.crw_goods_code]
		
		product_data.brd_id = self.BRD_ID
		product_data.crw_post_url = crw_post_url
		
		self.PRODUCT_URL_HASH[crw_post_url] = product_data
		self.PRODUCT_AVAIBLE_ITEM_HASH[product_data.crw_goods_code] = product_data.crw_id
					
	
	def set_product_data(self , soup, product_ctx ) :

		# 
		# 각 사이트별로 변경해서 사용해야함.
		#
		# soup = bs4.BeautifulSoup(html, 'lxml')
		# product_ctx : 상품리스트에서 상품 하나를 나타내는  element
		#
					
		return True
		
	
	def get_product_data(self, page_url, html):
		rtn = False
		
		self.set_param_product(html)
		
		product_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
			
		if( self.C_PRODUCT_CASE == __DEFINE__.__C_SELECT__ ) : product_link_list = soup.select(self.C_PRODUCT_VALUE)
		__LOG__.Trace('product list : %d' % len(product_link_list) )
		for product_ctx in product_link_list :
			self.set_product_data( page_url, soup, product_ctx )
		
		
		return rtn
		
		
	def process_product(self, page_url):
	
		rtn = False
		resptext = ''
		
		try :
		
			if( config.__DEBUG__ ) :
				__LOG__.Trace('page : %s' % ( page_url ) )
				
			time.sleep(self.WAIT_TIME)
			URL = page_url
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
				rtn = self.get_product_data( page_url, resptext )
			
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
			
		for page_url in self.PAGE_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			self.process_product( page_url )
		
		if(config.__DEBUG__) : __LOG__.Trace( '총 물품 수 : %d' % len(self.PRODUCT_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
	'''
	######################################################################
	# 상품 상세 페이지
	######################################################################
	'''
	
	def get_image_data_innerhtml(self, inner_str):
		#
		#	javascript 문구 안에 있는 <img> html 요소에서
		#   이미지 URL을 추출하는 함수
		#
		#  입력 : inner_str 
		#
		
		try :
			detail_page_img = []
			
			# 필요없는 문자 삭제
			inner_html = inner_str.replace('\\n"','' ).replace('\\n','\n' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','' ).replace('&quot;',' ' ).replace('\\x3C!','<!').replace('\\>','>').strip()
			
			
			# 완전한 html 문자열로 변경
			html = '''<html lang="ko"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
					<body>''' + inner_html + '''</body></html>'''
			
			# bs4를 이용한 이미지 URL 추출
			soup = bs4.BeautifulSoup(html, 'lxml')

			img_list = soup.find_all('img')
			for img_ctx in img_list :
				if('src' in img_ctx.attrs) : 
					img_src = img_ctx.attrs['src']
					if( img_src != '' ) :
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						detail_page_img.append(self.get_hangul_url_convert( img_link ) )
				
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return detail_page_img
	
	
	
	def get_text_data_innerhtml(self, inner_str):
		#
		#	javascript 문구 안에 있는 <img> html 요소에서
		#   텍스트를 추출하는 함수
		#
		#  입력 : inner_str 
		#
		try :
			detail_page_txt = []
			
			# 필요없는 문자 삭제
			inner_html = inner_str.replace('\\n"','' ).replace('\\n','\n' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','' ).replace('&quot;',' ' ).replace('\\x3C!','<!').replace('\\>','>').strip()
			
			# 완전한 html 문자열로 변경
			html = '''<html lang="ko"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
					<body>''' + inner_html + '''</body></html>'''
			
			# bs4를 이용한 이미지 URL 추출
			soup = bs4.BeautifulSoup(html, 'lxml')

			div_list = soup.find_all('div')
			for div_ctx in div_list :
				detail_page_txt.append( div_ctx.get_text().strip() )

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return detail_page_txt


	def get_value_in_dl_dtdd(self, dl_list) :
		#
		#	dl > dt /dd 에서 title 과 값을 얻어 오는 함수
		#   dict 형태로 얻어옴
		#   
		#  입력 : dl_list - bs4의 dl selector로 얻은 DL 리스트
		#  출력 : rtn_dict - key : 구분자 , value : 표현값
		#
		rtn_dict = {}
		
		for dl_ctx in dl_list :			
			dt_ctx = dl_ctx.find('dt')		# 구분자 ( '브랜드', '판매가'등 )
			dd_ctx = dl_ctx.find('dd')		# 표현값
			if(dt_ctx != None) :
				title_name = dt_ctx.get_text().strip()
				if(title_name != '') :
					if(dd_ctx != None) :
						content_value = dd_ctx.get_text().strip()
						rtn_dict[title_name] = content_value
						
		return rtn_dict				
						
	
	def get_value_in_table_two_colume(self, table_list, table_caption, title_selector, content_selector) :
		#
		#	테이블 에서 title 과 값을 얻어 오는 함수
		#   dict 형태로 얻어옴
		#   2개의 th 와 2개 td 로 구성되어 있는 경우와 같을때 사용
		#
		#  입력 : 
		#	1) table_list - bs4의 table selector로 얻은 table 리스트
		#	2) table_caption - table 의 caption 문자열
		#	3) title_selector - 구분자의 bs4 element
		#	4) content_selector - 표현값의 bs4 element
		#
		#  출력 : rtn_dict - key : 구분자 , value : 표현값
		#
		rtn_dict = {}
		is_caption = True
		
		for table_ctx in table_list :
			try :
				tb_caption_ctx =  table_ctx.find('caption')
				
				# table의 특정 caption 여부 체크
				if(table_caption != '') :
					is_caption = False
					if(tb_caption_ctx != None) :
						if(table_caption == tb_caption_ctx.get_text().strip() ) : is_caption = True
				
				
				if(is_caption) :		
					tr_list = table_ctx.find_all('tr')
					for tr_ctx in tr_list :
						title_list = tr_ctx.find_all( title_selector )
						content_list = tr_ctx.find_all( content_selector )
						idx = -1
						for title_ctx in title_list :
							idx += 1
							title_name = title_ctx.get_text().strip()
							content_value = ''
							if(title_name != '') and ( content_list != None ) :
								if(idx == 0) :
									if(1 <= len(content_list) ) : content_value = content_list[0].get_text().strip()
								elif(idx == 1) :
									if(2 <= len(content_list) ) : content_value = content_list[1].get_text().strip()
								rtn_dict[title_name] = content_value
			except :
				pass
					
		return rtn_dict
		
	
	def get_value_in_table(self, table_list, table_caption, title_selector, content_selector, content_idx) :
		#
		#	테이블 에서 title 과 값을 얻어 오는 함수
		#   dict 형태로 얻어옴
		#   1개의 th 와 2개 td 로 구성되어 있는 경우와 같을때 사용
		#
		#  입력 : 
		#	1) table_list - bs4의 table selector로 얻은 table 리스트
		#	2) table_caption - table 의 caption 문자열
		#	3) title_selector - 구분자의 bs4 element
		#	4) content_selector - 표현값의 bs4 element
		#	5) content_idx - 표현값의 bs4 element의 idx 값
		#
		#  출력 : rtn_dict - key : 구분자 , value : 표현값
		#
		rtn_dict = {}
		is_caption = True
		
		for table_ctx in table_list :
			tb_caption_ctx =  table_ctx.find('caption')
			
			# table의 특정 caption 여부 체크
			if(table_caption != '') :
				is_caption = False
				if(tb_caption_ctx != None) :
					if(table_caption == tb_caption_ctx.get_text().strip() ) : is_caption = True
			
			
			if(is_caption) :		
				tr_list = table_ctx.find_all('tr')
				for tr_ctx in tr_list :
					title_ctx = tr_ctx.find( title_selector )
					if(title_ctx != None) :
						title_name = title_ctx.get_text().strip()
						if(title_name != '') :
							content_list = tr_ctx.find_all( content_selector )
							idx = -1
							for content_ctx in content_list :
								idx += 1
								if(idx == content_idx ) :
									content_value = content_ctx.get_text().strip()
									rtn_dict[title_name] = content_value
								
					
		return rtn_dict
		
		
	def get_value_in_meta(self, soup, meta_property, tag_attr='content') :
		#
		#	html 안에 meta 필드에서 값을 추출하는 함수
		#

		rtn = None
		for tag in soup.find_all("meta"):
			if tag.get("property", None) == meta_property :
				rtn = tag.get(tag_attr, None)
				break
				
		return rtn
	
	
	
	def get_json_data_innerhtml(self, inner_str, split_first, split_last):

		#
		# html 에서 split 인자로 특정부분을 json 데이터를 추출하는 함수
		# split_first 인자를 이용해서 리스트 1번을 --> tmp_html 문자열로 지정
		# tmp_html문자열에서 split_last 인자를 이용해서 리스트 0을 갖고 와서 json 데이터 형식의 last_html 을 얻는다.
		#

		jsondata = None
		try :
			split_list = inner_str.split(split_first)
			tmp_html = split_list[1].strip()
			second_split_list = tmp_html.split(split_last)
			last_html = second_split_list[0].strip()
			jsondata = json.loads(last_html)

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return jsondata


		


		
	def print_product_page_info( self, product_data ) :
		#
		# 상세 제품에 대한 크롤링 내용 출력
		#
		
		__LOG__.Trace('----------------------------------------------------------')
		__LOG__.Trace( 'BRD ID : %d' % product_data.brd_id )
		__LOG__.Trace( '카테고리1 : %s' % product_data.crw_category1 )
		__LOG__.Trace( '카테고리2 : %s' % product_data.crw_category2 )
		__LOG__.Trace( '카테고리3 : %s' % product_data.crw_category3 )

		__LOG__.Trace( '상품 URL : %s' % product_data.crw_post_url )
		__LOG__.Trace( '상품코드 : %s' % product_data.crw_goods_code )
		__LOG__.Trace( '상품명 : %s' % product_data.crw_name )
		if(product_data.crw_is_soldout == 1) : __LOG__.Trace( '매진여부 : 품절 ')
		else : __LOG__.Trace( '매진여부 : 판매 ')	
		__LOG__.Trace( '브랜드1   : %s' % product_data.crw_brand1 )
		__LOG__.Trace( '브랜드2   : %s' % product_data.crw_brand2 )
		__LOG__.Trace( '브랜드3   : %s' % product_data.crw_brand3 )
		__LOG__.Trace( '브랜드4   : %s' % product_data.crw_brand4 )
		__LOG__.Trace( '브랜드5   : %s' % product_data.crw_brand5 )
		
		__LOG__.Trace( '가격     : %d' % product_data.crw_price )
		__LOG__.Trace( '할인가   : %d' % product_data.crw_price_sale )
		#__LOG__.Trace( product_data.cdt_content)
		__LOG__.Trace( '이미지   : %s' % product_data.product_img )
			
	
	def print_detail_page_info( self, product_data ) :
		#
		# 상세 제품에 대한 크롤링 내용 출력
		#
		__LOG__.Trace('----------------------------------------------------------')
		__LOG__.Trace( 'BRD ID : %d' % product_data.brd_id )
		__LOG__.Trace( 'CRW ID : %d' % product_data.crw_id )
		__LOG__.Trace( '브랜드1   : %s' % product_data.d_crw_brand1 )
		__LOG__.Trace( '브랜드2   : %s' % product_data.d_crw_brand2 )
		__LOG__.Trace( '브랜드3   : %s' % product_data.d_crw_brand3 )
		__LOG__.Trace( '브랜드4   : %s' % product_data.d_crw_brand4 )
		__LOG__.Trace( '브랜드5   : %s' % product_data.d_crw_brand5 )
		__LOG__.Trace( '텍스트    : %s' % product_data.cdt_content )
		__LOG__.Trace( product_data.detail_page_img )
	
	
	
	def get_product_detail_data(self, product_data, html):
		#
		#
		# 각 사이트별로 Overwrite 입력
		#
		rtn = False
		
		return rtn
		
	
	
	def process_product_detail(self, product_url, product_data):
	
		rtn = False
		resptext = ''
		
		try :
			__LOG__.Trace('------------------------------------------------')
			if( config.__DEBUG__ ) : __LOG__.Trace('product : %s' % ( product_url ) )

			time.sleep(self.WAIT_TIME)
			
			URL = product_url
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
				rtn = self.get_product_detail_data( product_data, resptext )
				
				# API 작업
				self.process_product_detail_api(product_data)
				
		except Exception as ex:
			__LOG__.Error( "process_product_detail Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		self.PRODUCT_URL_HASH[product_url] = product_data
		
		return rtn
		
		
		
	def process_product_detail_page(self):

		__LOG__.Trace("********** process_product_detail_page ***********")
		
		rtn = False
		resptext = ''

		for product_url in self.PRODUCT_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			product_data = self.PRODUCT_URL_HASH[product_url]
			
			# 신규 입력일때만 상세페이지 조회
			if( product_data.crw_action == __DEFINE__.__INSERT_CRW__ ) : self.process_product_detail( product_url ,product_data )
			#self.process_product_detail( product_url ,product_data )
		
		__LOG__.Trace("*************************************************")	
		
		return rtn

	
	def get_text_img_in_detail_content_part(self, soup, content_selector, text_sub_selector, img_attr, img_selector='img' ) :
		#
		# 상품 상세 페이지에서 텍스트와 이미지 리스트를 얻어오는 함수
		#
		# content_selector : 상세페이지 부분의 selector 표시
		# text_sub_selector : content_selector 안에 텍스트가 들어가 있는 서브 selector
		# text_sub_selector = '' 일때 content_selector 으로 텍스트를 얻어옴.
		# img_attr : 이미지의 url이 들어가 있는 attrs 를 지정하는 값을 ( 보통 : 'src' 에 있으나, 'ec-data-src' 에 있는 경우도 있음)
		# img_selector : img tag가 아닌 것을 위해서 추가함.
		#
		detail_page_txt = []
		detail_page_img = []
		
		try :
			# 제품 상세 부분
			
			detail_content_list = soup.select(content_selector)
			
			for detail_content_ctx in detail_content_list :
				# 제품 상세 텍스트
				if(text_sub_selector =='') :
					content_text = detail_content_ctx.get_text().strip()
					if( 0 < len(content_text) ) :
						rtn_str = self.get_detail_text_with_strip( content_text )
						detail_page_txt.append( rtn_str )
				else :
					sub_content_list = detail_content_ctx.find_all(text_sub_selector)
					for sub_content_ctx in sub_content_list :
						content_text = sub_content_ctx.get_text().strip()
						if( 0 < len(content_text) ) :
							rtn_str = self.get_detail_text_with_strip( content_text )
							detail_page_txt.append( rtn_str )
						

				# 제품 상세 이미지
				image_link_list = detail_content_ctx.find_all(img_selector)
				for img_ctx in image_link_list :
					#__LOG__.Trace( img_ctx )
					if(img_attr in img_ctx.attrs ) : 
						img_src = img_ctx.attrs[img_attr].strip()
						if( img_src != '' ) and (img_src.startswith('data:') == False) :
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							detail_page_img.append( self.get_hangul_url_convert( img_link ) )
							
							
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return detail_page_txt, detail_page_img
	


	'''
	######################################################################
	# API 작업
	######################################################################
	'''

	def process_product_api(self, product_data) :
		#
		# 상품 INSERT / UPDATE 하는 API 진행
		#
		if( config.__DEBUG__ ) : self.print_product_page_info( product_data )
		
		# config.__REAL__ = True 일때 실서버 작업
		if( config.__REAL__ ) :
		
			if(product_data.crw_action == __DEFINE__.__INSERT_CRW__ ) :		# INSERT
				__LOG__.Trace('ITEM INSERT -----------------------------------------------------')
				if( product_data.product_img == '') :
					__LOG__.Trace(' 상품 리스트에 이미지가 없습니다' )
				else : 
					rtn , crw_file_1 = __IMGJOB__.get_single_img(product_data.product_img)
					
					if(rtn ) :
						product_data.crw_file_1 = crw_file_1
						crw_id = __API__.insert_itemlist(product_data)
						if(crw_id != 0) : 
							product_data.crw_id = crw_id
							self.PRODUCT_ITEM_HASH[product_data.crw_goods_code] = product_data.crw_id
						
						__IMGJOB__.remove_img(crw_file_1)
						
			else :		# UPDATE
				__LOG__.Trace('ITEM UPDATE -----------------------------------------------------')
				__API__.update_itemlist(product_data)

			

	def process_product_detail_api(self, product_data) :
		#
		# 상품 상세 INSERT하는 API 진행
		#
		if( config.__DEBUG__ ) : self.print_detail_page_info( product_data )
		
		# config.__REAL__ = True 일때 실서버 작업
		if( config.__REAL__ ) :
			if(product_data.crw_action == __DEFINE__.__INSERT_CRW__ ) :		# INSERT
				__LOG__.Trace('ITEMDETAIL INSERT -----------------------------------------------------')
				#__LOG__.Trace( product_data.detail_page_img )
				rtn , d_crw_file_1 = __IMGJOB__.get_merge_img(product_data.detail_page_img)
				
				if(rtn ) : product_data.d_crw_file_1 = d_crw_file_1
				__API__.insert_itemdetail(product_data)
				if(rtn ) : __IMGJOB__.remove_img(d_crw_file_1)

	
	
	
	def process_product_delete_api(self) :
		#
		# 상품리스트에 없는 기존 상품에 대해서, 삭제하는 API 진행
		#
		# config.__REAL__ = True 일때 실서버 작업
		if( config.__REAL__ ) :
			for key in self.PRODUCT_ITEM_HASH.keys() :
				if(self.SHUTDOWN) : break
				if(self.PRODUCT_AVAIBLE_ITEM_HASH.get(key, -1) == -1) :
					crw_id = self.PRODUCT_ITEM_HASH[key]
					__API__.is_delete( crw_id )
	
	'''
	######################################################################
	# 메인 함수
	######################################################################
	'''
	
	def init_mall(self, brd_id) :
		#
		# mall 초기화
		#
		self.BRD_ID = brd_id
		self.SPECIAL_CATEGORY = ''
		
		# 초기화
		self.PRODUCT_AVAIBLE_ITEM_HASH = None
		self.PRODUCT_AVAIBLE_ITEM_HASH = {}
		
		self.PRODUCT_ITEM_HASH = None
		self.PRODUCT_ITEM_HASH = {}
		self.PRODUCT_ITEM_HASH = __API__.get_itemlist(self.BRD_ID)
		
		for key in self.PRODUCT_ITEM_HASH.keys() :
			__LOG__.Trace('%s : %d' % ( key , self.PRODUCT_ITEM_HASH[key] ))
		
		#랜덤 COOKIE 및 USER AGENT 값을 얻어 오기
		self.set_cookie()
		self.set_user_agent()
		
		
			
	def main(self, site_home, brd_id):

		__LOG__.Trace("***********************************************************")
		__LOG__.Trace("Start %s ( BRD_ID : %s ) ....." % ( site_home, str(brd_id)) )
		__LOG__.Trace("***********************************************************")
		

		try :
			
			#초기화
			self.init_mall(brd_id)
			
			# 카테고리 리스트 갖고 오기
			self.process_category_list()
			
			#페이지 URL 갖고 오기
			self.process_page_list()
			
			#물품 URL 갖고 오기
			self.process_product_list()
			
			#물품의 상세 페이지 정보 갖고 오기
			self.process_product_detail_page()
			
			#삭제된 물품리스트에 대해서, 삭제처리 
			self.process_product_delete_api()
			
		except Exception as ex :  
			__LOG__.Error(ex)            
			pass
			
			
		__LOG__.Trace("***********************************************************")
		__LOG__.Trace("Program End......")
		__LOG__.Trace("***********************************************************")	
	

	def start(self):
		#
		# mall 도메인을 갖고 storelist에서 mall 의 brd_id 를 찾아 main 함수에 전달.
		# brd_id 을 얻지 못하면 main 함수는 동작하지 않음.
		#
		split_list = self.SITE_HOME.split('/')
		search_web_str = split_list[2].strip()
		
		if(search_web_str.startswith('www.')) : search_web_str = split_list[2].replace('www.','')
		elif(search_web_str.startswith('shop.')) : search_web_str = split_list[2].replace('shop.','')
		

		BRD_ID_HASH = __API__.get_storelist( search_web_str )
		
		if(len(BRD_ID_HASH) == 0) :
			__LOG__.Trace("***********************************************************")
			__LOG__.Trace("에러 : BRD_ID 를 얻지 못했습니다. ( %s )" % ( self.SITE_HOME) )
			__LOG__.Trace("***********************************************************")
		
		for app_url in BRD_ID_HASH.keys() :
			if(self.SHUTDOWN) : break
			brd_id = BRD_ID_HASH[app_url]
			self.main(app_url, brd_id)
			
			
	def start_test(self):
		#
		# mall 도메인을 갖고 storelist에서 mall 의 brd_id 를 찾아 main 함수에 전달.
		# brd_id 을 얻지 못하면 main 함수는 동작하지 않음.
		#
		split_list = self.SITE_HOME.split('/')
		search_web_str = split_list[2].strip()
		
		if(search_web_str.startswith('www.')) : search_web_str = split_list[2].replace('www.','')
		elif(search_web_str.startswith('shop.')) : search_web_str = split_list[2].replace('shop.','')
		

		BRD_ID_HASH = __API__.get_storelist( search_web_str )		
		brd_id = 1
		app_url = self.SITE_HOME
		self.main(app_url, brd_id)
			
			
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))



	
	
	