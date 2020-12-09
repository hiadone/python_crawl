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
import re
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
from imweb.ImWeb import ImWeb


if not sys.warnoptions:
    warnings.simplefilter("ignore")


    
class shop(ImWeb) :    

	def __init__(self) :
	
		ImWeb.__init__(self)
		
		self.EUC_ENCODING = False
		
		self.SITE_HOME = 'https://eledog.co.kr'
		
		self.SITE_ORG_HOME = 'https://eledog.co.kr'
		
		self.SEARCH_MODE = __DEFINE__.__CATEGORY_ALL__

		
		
		self.C_CATEGORY_CASE = __DEFINE__.__C_SELECT__
		self.C_CATEGORY_TYPE = ''
		

		# self.C_CATEGORY_VALUE = 'body > div > main > div.doz_aside._doz_aside > div > div > div > div > div > div > div > ul > li > a'	#하위 메뉴용
		self.C_CATEGORY_VALUE = '#top_category > div > div > ul > div > ul > li'	#하위 메뉴용
		self.C_CATEGORY_IGNORE_STR = ['개인결제창']																
		self.C_CATEGORY_STRIP_STR = ''

		
		
		self.C_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_PAGE_TYPE = ''
		
		# self.C_PAGE_VALUE = 'body > div > main > div > div > div > div > div > div > nav > ul > li > a'
		self.C_PAGE_VALUE = '#container > div.xans-element-.xans-product.xans-product-normalpaging.ec-base-paginate > ol > li > a'
		self.C_PAGE_STRIP_STR = ''
		
		self.C_PAGE_IGNORE_STR = ['1']			# 페이지 중에 무시해야 하는 스트링
		self.C_PAGE_COUNT_PER_DISPLAY = 5	# 화면당 페이지 갯수
		
		
		self.C_PRODUCT_CASE = __DEFINE__.__C_SELECT__
		self.C_PRODUCT_TYPE = ''

		#self.C_PRODUCT_VALUE = 'body > div > main > div > div > div > div > div > div > div > div > div > div.shop-item._shop_item'
		
		# self.C_PRODUCT_VALUE = 'body > div > main > div > div > div > div > div > div > div > div > div > div.shop-item._shop_item'
		self.C_PRODUCT_VALUE = '#container > div.xans-element-.xans-product.xans-product-normalpackage > div > ul > li > div.item_list_box'
		
		self.C_PRODUCT_STRIP_STR = ''
		
		# self.PAGE_LAST_LINK = True 일때 사용
		self.C_LAST_PAGE_CASE = __DEFINE__.__C_SELECT__
		self.C_LAST_PAGE_TYPE = ''
		self.C_LAST_PAGE_VALUE = ''
		
		self.PAGE_SPLIT_STR = '&page='		# 페이지 링크에서 page를 구분할수 있는 구분자
		
		self.PAGE_LAST_LINK = False		# 페이지에서 맨끝 링크 존재 여부

		
		
		self.BASIC_CATEGORY_URL = self.SITE_ORG_HOME
		self.BASIC_PAGE_URL = self.SITE_ORG_HOME
		self.BASIC_PRODUCT_URL = self.SITE_ORG_HOME
		self.BASIC_IMAGE_URL = self.SITE_ORG_HOME
	
	'''
	######################################################################
	#
	# Mall.py 를 OverWrite 시킴
	#
	######################################################################
	'''
	
	def get_category_data(self, html):
		rtn = False
		
		main_category_name = ''
		self.set_param_category(html)
		
		category_link_list = []
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace( self.C_CATEGORY_CASE )
			__LOG__.Trace( self.C_CATEGORY_VALUE )
			
		if( self.C_CATEGORY_CASE == __DEFINE__.__C_SELECT__ ) : 
			category_link_list = soup.select(self.C_CATEGORY_VALUE)


		for category_main_ctx in category_link_list :

			try :
				category_ctx = category_main_ctx.find('a')
				
				if(category_ctx != None) :

					if(self.check_ignore_category( category_ctx ) ) :
						if('href' in category_ctx.attrs ) : 
							tmp_category_link = category_ctx.attrs['href']
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, category_ctx.attrs['href'] )
							category_link = tmp_category_link
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
				
							main_category_name = category_ctx.get_text().strip()
							if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
								self.CATEGORY_URL_HASH[category_link] = main_category_name
								if( config.__DEBUG__ ) :
									__LOG__.Trace('%s : %s' % ( main_category_name, category_link ) )

								rtn = True
					
				ul_ctx = category_main_ctx.find('ul')
				if( ul_ctx != None) :
					a_link_list = ul_ctx.find_all('a')
					for sub_link_ctx in a_link_list :
						if('href' in sub_link_ctx.attrs ) : 
							tmp_category_link = sub_link_ctx.attrs['href']
							if(0 != tmp_category_link.find('http')) : tmp_category_link = '%s%s' % ( self.BASIC_CATEGORY_URL, sub_link_ctx.attrs['href'] )
							category_link = tmp_category_link
							if(self.C_CATEGORY_STRIP_STR != '') : category_link = tmp_category_link.replace( self.C_CATEGORY_STRIP_STR,'')
											
							sub_category_name = sub_link_ctx.get_text().strip()
							if( self.CATEGORY_URL_HASH.get( category_link , -1) == -1) : 
								self.CATEGORY_URL_HASH[category_link] = '%s|%s' % ( main_category_name, sub_category_name )
								if( config.__DEBUG__ ) :
									__LOG__.Trace('%s|%s : %s' % ( main_category_name, sub_category_name , category_link ) )

			except Exception as ex:
				__LOG__.Error(ex)
				pass

		if(config.__DEBUG__) : __LOG__.Trace( '카테고리 수 : %d' % len(self.CATEGORY_URL_HASH))
		
		return rtn
		
	def set_product_data(self , page_url, soup, product_ctx ) :
		
		# 
		#
		try :
			product_data = ProductData()
			crw_post_url = ''
			
			
			self.reset_product_category(product_data)
			
			####################################
			# 상품 카테고리 추출
			####################################
			
			self.get_category_value( product_data, page_url, soup )
			
			

			####################################				
			# 상품 이미지 확인
			#
			# <div class="prdImg  scroll-fade">
                #     <a href="/product/방수커버/57/category/61/display/1/" name="anchorBoxName_57">
                #         <img src="//eledog.co.kr/web/product/medium/202011/74b4cc12fc9dd4f38c49d4de2d2f6b51.jpg" id="eListPrdImage57_1" class="thumb_Img" alt="방수커버">                    </a>              
                # </div>
			#
			# class_='_org_img org_img _lazy_img'
			# class_='_org_img org_img owl-lazy'
			####################################
			
			img_ctx = product_ctx.find('div', class_='prdImg')
			
			
			
			img_ = img_ctx.find('img', class_='thumb_Img')
			
			img_src = ''
			if('src' in img_.attrs ) : img_src = img_.attrs['src'].strip()
			
			if( img_src != '' ) :
				img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
				product_data.product_img = self.get_hangul_url_convert( img_link )

			crw_goods_code_ = img_ctx.find('a')

			if(crw_goods_code_ != '') :
				if('name' in crw_goods_code_.attrs ) :
					if( 0 <= crw_goods_code_.attrs['name'].find('anchorBoxName_')) :
						class_name_list = crw_goods_code_.attrs['name']
						product_data.crw_goods_code = class_name_list.replace('anchorBoxName_','')


			
			####################################
			# 품절여부 추출
			#
			# <div class="promotion"><img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/ico_product_soldout.gif" class="icon_img" alt="품절">      </div>
			#
			####################################
			soldout_div_list = product_ctx.find_all('img', alt='품절')
			for soldout_div_ctx in soldout_div_list :
				product_data.crw_is_soldout = 1
			
			####################################
			# <div class="item_list_box">
			#             <div class="thumbnail">
			#                 <div class="custom_pro  dj_count30"><span class="dj-mov-fade-in-out2">21%</span></div>
			#                 <div class="button">
			#                       <ul>
			# <li class="likeButton displaynone"><button type="button">LIKE<strong></strong></button></li>
			#                       </ul>
			# <ul class="other">
			# <li class="option"><span>옵션보기</span>
			# </li>
			#                         <li class="cart">
			# <a href="#none"><img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/btn_list_cart.gif" onclick="CAPP_SHOP_NEW_PRODUCT_OPTIONSELECT.selectOptionCommon(43,  42, 'basket', '')" alt="장바구니 담기" class="ec-admin-icon cart"></a><span>장바구니</span>
			# </li>
			#                         <li class="zoom">
			# <a href="#none"><img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/btn_prd_zoom.gif" onclick="zoom('43', '42', '1','', '');" style="cursor:pointer" alt="상품 큰 이미지 보기"></a><span>확대보기</span>
			# </li>
			#                         <li class="pop">
			# <a href="/product/ver02-맞춤이가방-카키/43/category/42/display/1/" target="blank"><img src="/_dj/img/button_other_04.png"></a><span>새창보기</span>
			# </li>
			#                       </ul>
			# </div>
			#                   <div class="prdImg  scroll-fade">
			#                     <a href="/product/ver02-맞춤이가방-카키/43/category/42/display/1/" name="anchorBoxName_43">
			#                         <img src="//eledog.co.kr/web/product/medium/202011/d05fff61e25635e2dae85c6a7dadce63.jpg" id="eListPrdImage43_1" class="thumb_Img" alt="[ver.02] 맞춤이가방 : 카키">                    </a>              
			#                 </div>
			#             </div>
			#             <div class="description" onclick="window.location.href='/product/ver02-맞춤이가방-카키/43/category/42/display/1/';">
			#                 <div class="inner">
			#                      <div class="displaynone">
			#                                            </div>
			#                    <div class="brand displaynone"></div>
			#                    <strong class="name"><a href="/product/ver02-맞춤이가방-카키/43/category/42/display/1/" class=""><span style="font-size:12px;color:#555555;">[ver.02] 맞춤이가방 : 카키</span></a></strong>
			#                    <ul class="spec">
			# <li class="summary_line displaynone">         
			#                        </li>
			# <li class="summary displaynone"></li>
			#                        <li class="price_all">
			#                            <span class="custom ">188,000원</span>
			#                            <span class="price  displaynone"><span class="strike">149,000원</span><span class="pri">149,000원</span></span>
			#                            <span class="sale displaynone"></span> 
			#                        </li>
			#                    </ul>
			# <div class="icon">
			#                        <div class="promotion">  <img src="//img.echosting.cafe24.com/design/skin/admin/ko_KR/ico_product_recommended.gif" class="icon_img" alt="추천">    </div>
			#                    </div>
			#                    </div>
			#              </div>
			#          </div>
			#
			####################################
			name_div_list = product_ctx.find_all('div', class_='description')

			for name_div_ctx in name_div_list :
				h2_list = name_div_ctx.find_all('strong')
				for h2_ctx in h2_list :
					
					product_link_ctx = name_div_ctx.find('a')
					if( product_link_ctx != None) :

						if('href' in product_link_ctx.attrs ) : 

							product_data.crw_name = h2_ctx.get_text().strip()
							
							crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')

							
							
			
			####################################
			# 가격
			#
			# <li class="price_all">
			#     <span class="custom ">188,000원</span>
			#     <span class="price  displaynone"><span class="strike">149,000원</span><span class="pri">149,000원</span></span>
			#     <span class="sale displaynone"></span> 
			# </li>
			#
			####################################			
			price_div_list = product_ctx.find_all('li', class_='price_all')
			
			for price_ctx in price_div_list :	
				p_list = name_div_ctx.find_all('span')
				for p_ctx in p_list :
					if('class' in p_ctx.attrs ) :
						class_name_list = p_ctx.attrs['class']
						if(class_name_list[0] == 'custom' ) : product_data.crw_price = int( __UTIL__.get_only_digit( p_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'pri' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( p_ctx.get_text().strip() ))
					

			
			if( crw_post_url != '' ) :
				#if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
				
				self.set_product_data_sub( product_data, crw_post_url )

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
		'''
		#
		#
		'''
		rtn = False
		try :
			
			detail_page_txt = []
			detail_page_img = []
			crw_brand = []
			
			soup = bs4.BeautifulSoup(html, 'lxml')
			
			# table_list = soup.select('#goods_spec > form > table')
			
			# rtn_dict = self.get_value_in_table( table_list, '', 'th', 'td', 0)
			# if( '브랜드' in  rtn_dict) : crw_brand.append(rtn_dict['브랜드'])
			# elif( '제조사' in  rtn_dict) : crw_brand.append(rtn_dict['제조사'])
			
			# self.set_detail_brand( product_data, crw_brand )

				
			# 제품 상세 설명 부분의 텍스트 및 이미지
			detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#products_info', 'p', 'ec-data-src' )
			
			if(detail_page_img == ''):
				detail_page_txt, detail_page_img = self.get_text_img_in_detail_content_part( soup, '#products_info', 'p', 'src' )
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)

			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
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
			
			__LOG__.Trace(len(detail_content_list))
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

						pattern = re.compile(r'\s+')
						img_src = re.sub(pattern, '', img_ctx.attrs[img_attr])
						
						print(img_src)
						if( img_src != '' ) and (img_src.startswith('data:') == False) :
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							detail_page_img.append( self.get_hangul_url_convert( img_link ) )
							
							
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return detail_page_txt, detail_page_img

	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	
	
	def get_category_value(self, product_data, page_url, soup ) :
		#
		# div 안에 텍스트에서 물품 숫자를 제외한 부분만 추출해야 함.
		#
		# <div class="inline-blocked float_l">
		#							캠핑									<span class="text-brand"> 23</span>
		#						</div>
		#
		try :
			div_list = soup.find_all('div', class_='shop-tools clearfix')
			for div_ctx in div_list :
				category_ctx = div_ctx.find('div', class_='inline-blocked float_l')
				if(category_ctx != None) :
					ignore_str = ''
					org_str = category_ctx.get_text().strip()
					span_ctx = category_ctx.find('span')
					if(span_ctx != None) : ignore_str = span_ctx.get_text()
					able_pos = len(org_str) - len(ignore_str)
					
					product_data.crw_category1 = org_str[:able_pos].strip()
				

		except :
			pass
			
		return True
	'''		


	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 5))

	app = shop()
	app.start()
	
	
	