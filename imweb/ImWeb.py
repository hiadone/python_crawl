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


    
class ImWeb(Mall) :    

	def __init__(self) :
	
		Mall.__init__(self)
		
		
		
	'''
	######################################################################
	#
	# 상품 리스트 페이지 : 사이트별 수정해야 함.
	#
	######################################################################

	
	def get_category_value(self, product_data, page_url, soup ) :
	
		if(self.PAGE_URL_HASH.get( page_url , -1) != -1) : product_data.crw_category1 = self.PAGE_URL_HASH[page_url]
	'''
	
	def get_category_value(self, product_data, page_url, soup ) :
	
		if(self.PAGE_URL_HASH.get( page_url , -1) != -1) : 
			split_list = self.PAGE_URL_HASH[page_url].split('|')
			idx = 0
			for split_data in split_list :
				idx += 1
				if(idx == 1) :product_data.crw_category1 = split_data.strip()
				elif(idx == 2) :product_data.crw_category2 = split_data.strip()
				elif(idx == 3) :product_data.crw_category3 = split_data.strip()
				
	
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
			# <img data-prodcode="s20200603cfcd165650db6" alt="" src="https://cdn.imweb.me/thumbnail/20200603/69b4e17496c01.jpg" class="_org_img org_img _lazy_img" data-original="https://cdn.imweb.me/thumbnail/20200603/69b4e17496c01.jpg" data-src="https://cdn.imweb.me/thumbnail/20200603/69b4e17496c01.jpg" style="display: inline;">
			#
			# class_='_org_img org_img _lazy_img'
			# class_='_org_img org_img owl-lazy'
			####################################

			img_list = product_ctx.find_all('img')			
			for img_ctx in img_list :
				if('class' in img_ctx.attrs) :
					class_name_list = img_ctx.attrs['class']
					if( 2 < len(class_name_list) ) :
						if( class_name_list[0] == '_org_img' ) and ( class_name_list[1] == 'org_img' ) :
							img_src = ''
							if('data-original' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-original'].strip()
							
							if( img_src == '' ) :
								if('data-src' in img_ctx.attrs ) : img_src = img_ctx.attrs['data-src'].strip()
								
							if( img_src == '' ) :
								if('src' in img_ctx.attrs ) : img_src = img_ctx.attrs['src'].strip()
							
							if( img_src != '' ) :
								img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
								product_data.product_img = self.get_hangul_url_convert( img_link )

			
			####################################
			# 품절여부 추출
			#
			# <div class="ns-icon clearfix">
			# <!--<span class="new bg-brand">NEW</span>-->
			# <div class="prod_icon sale">SALE</div><div class="prod_icon sold_out">SOLDOUT</div>											</div>
			#
			####################################
			soldout_div_list = product_ctx.find_all('div', class_='prod_icon sold_out')
			for soldout_div_ctx in soldout_div_list :
				product_data.crw_is_soldout = 1
			
			####################################
			# 상품 링크 정보 및 상품명 / 상품코드
			#
			# <div class="item-detail" style="">
			# <div class="item-pay">
			# <h2 style="display: ">
			# <a class="_fade_link" href="/shop/?idx=1185">어반비스트 훈련용 코만도백</a>
			# </h2>
			# <div class="item-pay-detail">
			# <p class="sale_pay body_font_color_50" style="">78,000원</p>											<p class="pay" style=";">
			# 58,500원											</p>
			# </div>
			# <div class="ns-icon clearfix">
			# <!--<span class="new bg-brand">NEW</span>-->
			# <div class="prod_icon sale">SALE</div><div class="prod_icon sold_out">SOLDOUT</div>											</div>
			# </div>
			# <div class="item-summary holder">
			# <p>반려견의 산책과 훈련을 위한 코만도백</p>											<a class="item-summary-link _fade_link" href="/shop/?idx=1185"><span class="sr-only">상품 요약설명</span></a>
			# </div>
			# <div class="item-icon">
			# <span><i class="icon-bubble"></i> 0</span>
			# </div>
			# </div>
			#
			####################################
			name_div_list = product_ctx.find_all('div', class_='item-detail')

			for name_div_ctx in name_div_list :
				h2_list = name_div_ctx.find_all('h2')
				for h2_ctx in h2_list :
					product_link_ctx = name_div_ctx.find('a', class_='_fade_link')
					if( product_link_ctx != None) :

						if('href' in product_link_ctx.attrs ) : 
							product_data.crw_name = h2_ctx.get_text().strip()
							
							crw_post_url = self.get_crw_post_url( product_link_ctx, 'href')
							if(crw_post_url != '') :
								split_list = crw_post_url.split('?idx=')
								crw_goods_code_list = split_list[1].strip().split('&')
								product_data.crw_goods_code = crw_goods_code_list[0].strip()
							
			
			####################################
			# 가격
			#
			# <div class="item-pay-detail">
			# <p class="sale_pay body_font_color_50" style="">78,000원</p>											<p class="pay" style=";">
			# 58,500원											</p>
			# </div>
			#
			####################################			
			price_div_list = product_ctx.find_all('div', class_='item-pay-detail')

			for price_ctx in price_div_list :	
				p_list = name_div_ctx.find_all('p')
				for p_ctx in p_list :
					if('class' in p_ctx.attrs ) :
						class_name_list = p_ctx.attrs['class']
						if(class_name_list[0] == 'sale_pay' ) : product_data.crw_price = int( __UTIL__.get_only_digit( p_ctx.get_text().strip() ) )
						elif(class_name_list[0] == 'pay' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( p_ctx.get_text().strip() ))
					

			
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
	# 
	#
	#
	######################################################################
	'''
	def get_detail_brand_data(self, product_data, html):
		#
		#
		# 상세페이지 부분에서 브랜드 데이터 갖고 오기
		#
		#<script type='application/ld+json'>{"@context":"http:\/\/schema.org","@type":"Product","name":"Raglan T-shirt #mint","image":["https:\/\/cdn.imweb.me\/thumbnail\/20200512\/6ca1480c2e3ad.jpg"],"description":"\ucc38\uace0\uc0ac\ud56d\uc81c\ud488\uc758 \uc0c9\uc0c1\uc740 \uc2e4\ub0b4 \ubc0f \uc2e4\uc678\uc5d0\uc11c \ucc28\uc774\uac00 \uc788\uc744 \uc218 \uc788\uc2b5\ub2c8\ub2e4.\ub098\ub098 NANA \ucc29\uc6a9\uc0ac\uc774\uc988 - M\ub85c\ub2c8 RONI \ucc29\uc6a9\uc0ac\uc774\uc988 - M\uc0c1\ud488 \uc0ac\uc774\uc988\ud45c\uc0ac\uc774\uc988\ub294 \uce21\uc815 \ubc29\ubc95\uc5d0 \ub530\ub77c &plusmn;1-2cm \uc624\ucc28\uac00 ... ","brand":{"@type":"Brand","name":"Hipaw"},"offers":{"@type":"Offer","price":32000,"priceCurrency":"KRW","url":"http:\/\/hipaw.co.kr\/shop_view\/?idx=28","availability":"http:\/\/schema.org\/InStock"},"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0000","reviewCount":"3"}}</script>
		crw_brand = []
		ignore_str = "<script type='application/ld+json'>"
		del_pos = html.find(ignore_str)
		
		if(0 < del_pos):
			ignore_pos = html.find(ignore_str) + len( ignore_str )
			last_pos = html[ignore_pos:].find('</script>')
			
			detail_data = html[ignore_pos:ignore_pos+last_pos].strip()
			json_data = json.loads( detail_data )

			for key in json_data :
				#__LOG__.Trace('%s : %s' % (key, json_data[key]))
				if(key == 'brand') : crw_brand.append( json_data[key]['name'] )

			self.set_detail_brand( product_data, crw_brand )
	

	
	def get_detail_img_text_data(self, product_data, html):
		#
		#
		# 상세페이지 부분에서 텍스트 와 이미지 갖고 오기
		#
		#$(function(){SNS.init({"_main_url":"http:\/\/gettouch.co.kr","_site_name":"\uac9f\ud130\uce58",
		#"_subject":"[\ub7f0\uce6d \uae30\ud68d\uc804]\uc5d0\uc5b4\ubc94\ud37c\uc2dc\ud2b8 990g \ucd08\uacbd\ub7c9 \ucda9\uaca9\uc644\ud654 \ubc18\ub824\uacac \uce74\uc2dc\ud2b8",
		#"_body":"<p><span class=\"fr-video fr-fvc fr-dvb fr-draggable\" contenteditable=\"false\" draggable=\"true\"><iframe width=\"640\" height=\"360\" src=\"https:\/\/www.youtube.com\/embed\/cHJALpiSiP4?&wmode=opaque\" frameborder=\"0\" allowfullscreen=\"\" class=\"fr-draggable\"><\/iframe><\/span><br><\/p><p style=\"text-align: center;\"><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/5758d95849304.png\" style=\"width: 837px;\"><strong><span style=\"font-size: 22px;\"><u><span class=\"fr-emoticon fr-deletable fr-emoticon-img\" style=\"background: url(https:\/\/cdnjs.cloudflare.com\/ajax\/libs\/emojione\/2.0.1\/assets\/svg\/1f600.svg);\">&nbsp;<\/span> &#39;\uac9f\ud130\uce58&#39; \uc628\ub77c\uc778\uc1fc\ud551\ubab0 \uc5d0\uc11c\ub9cc \uc9c4\ud589\ub418\ub294 40% &#39;\ud55c\uc815 \ud560\uc778&#39; \uc785\ub2c8\ub2e4. <span class=\"fr-emoticon fr-deletable fr-emoticon-img\" style=\"background: url(https:\/\/cdnjs.cloudflare.com\/ajax\/libs\/emojione\/2.0.1\/assets\/svg\/1f601.svg);\">&nbsp;<\/span>&nbsp;<\/u><\/span><\/strong><\/p><p style=\"text-align: center;\"><strong><span style=\"color: rgb(184, 49, 47);\"><span style=\"font-size: 18px;\"><u>[\ud68c\uc6d0\uac00\uc785 \uc2dc 3000\ud3ec\uc778\ud2b8, \ub9ac\ubdf0\uc791\uc131 \uc2dc 2000\ud3ec\uc778\ud2b8\ub97c &nbsp;\ub4dc\ub9bd\ub2c8\ub2e4]<\/u><\/span><\/span><\/strong><\/p><p style=\"text-align: center;\"><br><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/9ebf087528faa.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/cf44c929412b4.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/f86b21a482630.png\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/4d8d48359fa80.jpg\"><\/p><p style=\"text-align: center;\"><strong><span style=\"font-size: 24px;\"><u>\ucda9\uaca9\uc744 \uc644\ud654\ud558\ub294 &nbsp;&quot;\uc5d0\uc5b4\ubc31 \uce74\uc2dc\ud2b8&quot;<\/u><\/span><\/strong><\/p><p style=\"text-align: center;\"><br><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\uc138\ud0c1 \uc5c6\uc774\ub3c4 \uccad\uacb0\ud558\uace0, &nbsp;\ud754\ub4e4\ub9bc\uc5c6\uc774 \uc548\uc804\ud55c \uce74\uc2dc\ud2b8, \uc544\ub291\ud55c \ud558\uc6b0\uc2a4, \uc2a4\ud30c\uc695\uc870 , \ub4dc\ub77c\uc774\ubd80\uc2a4\ub85c !<\/span><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\ubaa8\ub4e0 \uae30\ub2a5\uc744 \ud569\uccd0\uc11c \uc644\ubcbd \uad6c\ud604\uc774 \uac00\ub2a5\ud55c &#39;\ub2e8, \ud558\ub098\uc758 \uce74\uc2dc\ud2b8&#39; \ub97c \uc18c\uac1c\ud569\ub2c8\ub2e4 &nbsp;<\/span><\/p><p style=\"text-align: center;\"><span style=\"color: rgb(71, 85, 119);\"><span style=\"font-size: 18px;\"><u>\uae30\uc874\uc758 \ubb34\uac81\uace0, \ud3fc\uc744 \ub123\uace0 \ube7c\uace0 \uc138\ud0c1\ud558\ub294 \ubc88\uac70\ub85c\uc6c0\uc740 \ub098\uc5d0\uac90 \uc5c6\uc2b5\ub2c8\ub2e4.<\/u><\/span><\/span><\/p><p style=\"text-align: center;\"><br><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/b3e5483d799f8.jpg\"><\/p><p style=\"text-align: left;\"><span style=\"font-size: 14px;\"><u><strong>\uad50\ud1b5\uc0ac\uace0 \uc2dc \uac00\uc7a5 \uc704\ud5d8\ud55c \uac83\uc740 \uc548\uc804\uc7a5\uce58\uac00 \uc5c6\ub294 \uc6b0\ub9ac\uc758 &nbsp;\ubc18\ub824\ub3d9\ubb3c \uc785\ub2c8\ub2e4<\/strong><\/u><\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 14px;\">\ucda9\uaca9\uc740 \uace0\uc2a4\ub780\uc774 \uc6b0\ub9ac\uc758 \ubc18\ub824\ub3d9\ubb3c\uc5d0\uac8c \uc804\ud574\uc9c0\uac8c \ub429\ub2c8\ub2e4.&nbsp;<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 14px;\">\uc2e0\ubc1c\uc744 \uc2e0\uace0 \ucc28\ub7c9\uc744 \ud0d1\uc2b9\ud558 \ub4ef &nbsp;\ubc18\ub824\ub3d9\ubb3c\ub3c4 \uc57c\uc678\ud65c\ub3d9 \ud6c4 \uadf8\ub300\ub85c \ucc28\ub7c9\uc5d0 \ud0d1\uc2b9\ud558\uac8c \ub429\ub2c8\ub2e4.<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 14px;\"><u>\ud611\uc18c\ud55c \ucc28\ub7c9\uc758 \uc2e4\ub0b4\ub294 \ub9ce\uc740 \uc0dd\ud65c \uba3c\uc9c0\uac00 \ubc1c\uc0dd\ud558\uac8c \ub418\uace0 \uc6b0\ub9ac\uc758 \ud638\ud761\uae30\ub85c \uc720\uc785 \ub418\uae30\ub3c4 \ud569\ub2c8\ub2e4.<\/u><\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 14px;\"><u>\uc774 \ucc98\ub7fc \uce74\uc2dc\ud2b8\uc758 \uccad\uacb0\ub3c4 \uc911\uc694\ud569\ub2c8\ub2e4.<\/u><\/span><\/p><p><br><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/88845ec4f555d.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/d1360fb10a96f.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/4e2df0db9f24b.png\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/3a1420a901537.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/9032ea39a1c9f.jpg\"><\/p><p><strong><span style=\"font-size: 16px;\"><u>3\uc911 &nbsp;\ucda9\uaca9 \ubcf4\ud638<\/u><\/span><\/strong><\/p><p><span style=\"font-size: 14px;\"><u>\ubb34\uc5c7\ubcf4\ub2e4 \ubc00\ucc29\ub41c \uace0\uc815\ub825\uc774 \uc911\uc694\ud569\ub2c8\ub2e4.&nbsp;<\/u><\/span><\/p><p><span style=\"font-size: 14px;\">\uae30\uc874\uc758 \uce74\uc2dc\ud2b8\ub294 \uc548\uc804\ubcf4\ub2e4\ub294 \ucc28\ub7c9\uc6a9 \uac15\uc544\uc9c0 \ubc29\uc11d\uc758 \uc5ed\ud560 \ube44\uc911\uc774 \ub192\uc558\uc8e0.<\/span><\/p><p><span style=\"font-size: 14px;\">\uc55e,\ub4a4 \ubfd0\ub9cc\uc544\ub2c8\ub77c \uc88c,\uc6b0\uce21\ub3c4 \ubc94\ud37c\ub85c \ubcf4\ud638\ud560 \uc218 \uc788\uc5b4\uc57c\uc9c0\ub9cc \uc0ac\uace0 \uc2dc \ucda9\uaca9\uc744 \ub9c9\uc544\uc904 \uc218 \uc788\uc5b4\uc694.&nbsp;<\/span><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/cc75ab07df4d2.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/ef73da35093d7.jpg\"><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\"><strong><u>\ud2b9\uc218 \uc5e0\ubcf4 \uce5c\ud658\uacbd PVC\uc790\uc7ac\ub97c \uc0ac\uc6a9\ud558\uc5ec \uac15\uc544\uc9c0 \ubc1c\ud1b1\uc73c\ub85c \uae01\uc5b4\ub3c4 \ucc22\uc5b4\uc9c0\uc9c0 \uc54a\uc544\uc694<\/u><\/strong><\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\uac15\uc544\uc9c0\uc758 \uc785\uc758 \ud06c\uae30, \uac01\ub3c4\ub97c \uacc4\uc0b0\ud558\uc5ec \uc27d\uac8c \ubb3c\uc218 \uc5c6\ub294 \ub450\uaed8\uc640 \uac01\ub3c4\ub85c \uc124\uacc4 \uc81c\uc791\ud558\uc600\uc5b4\uc694.<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">&nbsp;(\ud14c\uc2a4\ud2b8 \ubaa8\ub378 \uacac: 10kg \uc774\ud558 \uac15\uc544\uc9c0)<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\"><br><\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\"><strong><u>\ud0c4\uc131\uc744 \uac00\uc9c0\uace0 \uc788\uc5b4\uc11c \ubcf5\uc6d0\ub825\uc774 \uc6b0\uc218\ud569\ub2c8\ub2e4&nbsp;<\/u><\/strong><\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\ud0c4\uc131\uc774 \uc5c6\ub294 \ub531\ub531\ud55c \ubb3c\uac74, \ub610\ub294 \uc778\uc7a5\ub825\uc774 \uc57d\ud55c \ud328\ube0c\ub9ad\uc740 \uc27d\uac8c \ucc1f\uc5b4\uc9c8 \uc218 \uc788\uc9c0\ub9cc<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\ud0c4\uc131\uc774 \uac15\ud55c \ud2b9\uc218 PVC\ub294 \ud0c0\uc774\uc5b4\uc640 \ubcf4\ud2b8\uc5d0\ub3c4 \uc0ac\uc6a9 \ub420 \ub9cc\ud07c \ud798\uc774 \uac15\ud569\ub2c8\ub2e4<\/span><\/p><p style=\"text-align: center;\"><br><\/p><p><span style=\"font-size: 22px;\"><strong><u>\ud754\ub4e4\ub9bc \uc5c6\ub294 \uace0\uc815\ub825, &nbsp;\ub109\ub109\ud55c \uc0ac\uc774\uc988<\/u><\/strong><\/span><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/95f416a215783.jpg\"><\/p><p><br><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\ucc28\ub7c9 \uc2dc\ud2b8\uc5d0 \uc7a5\ucc29\ud588\uc744 \ub54c, \ucc28\ub7c9\uc2dc\ud2b8 \ubcf4\ub2e4 &nbsp;\uce74\uc2dc\ud2b8\uac00 &nbsp;10cm \uae38\uc5b4 \ub0b4\ubd80\uac00 \ub109\ub109 \ud569\ub2c8\ub2e4.&nbsp;<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\ucc28\ub7c9 \uc55e \ubc94\ud37c\uc5d0 \ub9de \ub2ff\ub3c4\ub85d \ucc28\ub7c9\uc2dc\ud2b8\ub97c \uc870\uc808\ud574 \uc8fc\uc2dc\uba74 \ud754\ub4e4\ub9bc\uc5c6\uc774 \ud54f \ub418\uc5b4 \ub354\uc6b1 \uc548\uc815\uc801\uc785\ub2c8\ub2e4.&nbsp;<\/span><\/p><p style=\"text-align: left;\"><span style=\"font-size: 16px;\">\uc55e\uba74\uacfc \ub4b7\uba74 \ubaa8\ub450 \uc544\uc774\uc18c\ud53d\uc2a4\uc5d0 \uace0\uc815\ud558\uc2e4 \uc218 \uc788\uc2b5\ub2c8\ub2e4<\/span><span style=\"font-size: 18px;\">&nbsp;<\/span><\/p><p><span style=\"font-size: 18px;\"><span class=\"fr-video fr-fvc fr-dvb fr-draggable\" contenteditable=\"false\" draggable=\"true\"><iframe width=\"640\" height=\"360\" src=\"https:\/\/www.youtube.com\/embed\/NPerRgJCaks?&wmode=opaque\" frameborder=\"0\" allowfullscreen=\"\" class=\"fr-draggable\"><\/iframe><\/span><\/span><br><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/541f6302f3a2c.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/beb7eded136a7.jpg\"><\/p><p><br><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\ucd94\uc6b4\ub0a0\uc5d0\ub294 \uadf9\uc138\uc0ac \ubc29\uc11d\uc73c\ub85c \ub530\ub4ef\ud558\uac8c~ <span class=\"fr-emoticon fr-deletable fr-emoticon-img\" style=\"background: url(https:\/\/cdnjs.cloudflare.com\/ajax\/libs\/emojione\/2.0.1\/assets\/svg\/1f600.svg);\">&nbsp;<\/span>&nbsp;<\/span><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\ub530\ub4ef\ud55c\ub0a0\uc5d4 \uadf9\uc138\uc0ac \ubc29\uc11d\uc744 \ube7c\uace0 \uc0ac\uc6a9\ud574\ubcf4\uc138\uc694.&nbsp;<\/span><\/p><p style=\"text-align: center;\"><br><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">&#39;\uc5d0\uc5b4\ubc94\ud37c\uc2dc\ud2b8&#39; \ubc14\ub2e5\uba74\uc740, \uacf5\uae30\uce35\uc774 \uc5c6\uc5b4\uc694.<\/span><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">&nbsp;\ubc14\ub2e5\ub0b4\ubd80\uc5d0\ub294 &nbsp;\ud3fc\ubc29\uc11d\uc774 \ub4e4\uc5b4\uc788\uc5b4 \ud3ed\uc2e0\ud569\ub2c8\ub2e4.<\/span><\/p><p style=\"text-align: center;\"><br><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\uc5ec\ub984\uc5d0\ub294 \ub0c9\ubc29\uc11d\uc744 \ub123\uc5b4 \uc0ac\uc6a9\ud574\ubcf4\uc138\uc694.&nbsp;<\/span><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\">\uc5d0\uc5b4\ubc94\ud37c\uc2dc\ud2b8\uc758 4\uba74 \uacf5\uae30\uce35 \uc73c\ub85c \ub0c9\ubc29\uc11d\uc758 \ub0c9\uae30\uac00 \uc720\uc9c0\ub418\uc5b4 \ubcf4\ub0c9\ud6a8\uacfc\ub97c \uac00\uc9d1\ub2c8\ub2e4.<\/span><\/p><p style=\"text-align: center;\"><br><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\"><span class=\"fr-video fr-fvc fr-dvb fr-draggable\" contenteditable=\"false\" draggable=\"true\"><iframe width=\"640\" height=\"360\" src=\"https:\/\/www.youtube.com\/embed\/elkd0X2PlZs?&t=5s&wmode=opaque\" frameborder=\"0\" allowfullscreen=\"\" class=\"fr-draggable\"><\/iframe><\/span><\/span><\/p><p style=\"text-align: center;\"><br><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/c4b97c8050810.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/56001b1085311.jpg\"><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\"><u><strong>\ub0b4 \uc544\uc774\ucc98\ub7fc \ub098\uc758 \ubc18\ub824\ub3d9\ubb3c\ub3c4 \uc18c\uc911\ud558\ub2c8\uae4c! &nbsp;&nbsp;<\/strong><\/u><\/span><\/p><p style=\"text-align: center;\"><span style=\"font-size: 18px;\"><u><strong>&nbsp;KC \uc5b4\ub9b0\uc774\uc81c\ud488 \uacf5\ud1b5 \uc548\uc804\uc778\uc99d \uc644\ub8cc<\/strong><\/u><\/span><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/c40017b03523e.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/70e3cda051bde.jpg\"><\/p><p><img src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/17d19dfed8e43.jpeg\" class=\"fr-fic fr-dii\" data-files=\"[object Object]\"><\/p><p><img src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/b19744c90f92c.jpeg\" class=\"fr-fic fr-dii\" data-files=\"[object Object]\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/c2a53406145cb.png\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/ebdab09239586.jpg\"><\/p><p><img class=\"fr-dib\" src=\"https:\/\/cdn.imweb.me\/upload\/S2017102059e9750974f52\/d3e2b5695a689.jpg\"><\/p>","_post_url":"http:\/\/gettouch.co.kr\/24\/?idx=14","_security_post_url":"aHR0cDovL2dldHRvdWNoLmNvLmtyLzI0Lz9pZHg9MTQ=","_img":"https:\/\/cdn.imweb.me\/thumbnail\/20191219\/cc417159e78ed.jpg","ace_counter_plus_switch":false,"_share_type":"commerce","_pin_page":"Y","_additional":{"commerce":{"orig_price":150000,"sale_price":89000}}});});
		#
		
		ignore_str = '$(function(){SNS.init('
		del_pos = html.find(ignore_str)
		
		if(0 < del_pos):
			ignore_pos = html.find(ignore_str) + len( ignore_str )
			last_pos = html[ignore_pos:].find(');});')
			
			detail_data = html[ignore_pos:ignore_pos+last_pos].strip()
			json_data = json.loads( detail_data )
			inner_html = ''
			for key in json_data :
				#__LOG__.Trace('%s : %s' % (key, json_data[key]))
				if(key == '_body') : inner_html = json_data[key]
			

			html = '''<html lang="ko"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
					<body><div>''' + inner_html + '''</div></body></html>'''
					

			soup = bs4.BeautifulSoup(html, 'lxml')
			detail_content_list = soup.select('html > body > div')
			
			detail_page_txt = []
			detail_page_img = []
			
			for detail_content_ctx in detail_content_list :
				content_text = detail_content_ctx.get_text().strip()
				
				if( 0 < len(content_text) ) :
					rtn_str = self.get_detail_text_with_strip( content_text )
					detail_page_txt.append( rtn_str )
				
				
				# 순수한 이미지 요소 추출
				img_list = detail_content_ctx.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs) : 
						img_src = img_ctx.attrs['src']
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						detail_page_img.append( self.get_hangul_url_convert( img_link )  )
				
			
				# 링크와 같이 있는 이미지 요소 추출
				img_list = detail_content_ctx.find_all('a', {'data-linktype':'img'})
				for img_ctx in img_list :
					if('data-linkdata' in img_ctx.attrs) : 
						img_text = img_ctx.attrs['data-linkdata']
						img_text_list = img_text.split(', src :')
						if(len(img_text_list) == 2) :
							tmp_img_list = img_text_list[1].strip().split(',')
							img_src = tmp_img_list[0].strip()
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							detail_page_img.append( self.get_hangul_url_convert( img_link )  )

			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
	

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
					
			self.get_detail_brand_data(product_data, html)
			self.get_detail_img_text_data(product_data , html)

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
	