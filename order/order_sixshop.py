#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user

특이사항
	- 상품리스트에 관한 <script> 문이 없는 경우 상품리스트가 나오지 않음.
	- html 요소에는 상품리스트 정보가 없음.
	
'''

import json
import time
import os, signal
import bs4
import sys
import warnings
from util import Util as __UTIL__
from app import config

import log as Log;  Log.Init()


if not sys.warnoptions:
    warnings.simplefilter("ignore")

	
	
def get_order_data( order_data, html ) :
	try :

		soup = bs4.BeautifulSoup(html, 'lxml')
	
		######################
		# 주문번호 / 가격
		# <div class="payment field">
		# <div id="content_div" class="content_wrapper">
		# <div class="content designSettingElement text-body">
		# <p class="title">결제 요청이 완료되었습니다.</p>
		# <div class="row">
		# <span class="title">주문번호</span>
		# <input type="text" class="designSettingElement shape" value="20200625KFYK3" readonly="">
		# </div>
		# .. 생략
		# <div class="row">
		# <span class="title">결제 금액</span>
		# <input type="hidden" class="designSettingElement shape" value="100,000" readonly="">
		# <input type="text" class="designSettingElement shape" value="100,000원" readonly="">
		# </div>
		# <div class="row">
		# <span class="title">상품 이름</span>
		# <input type="text" class="designSettingElement shape" value="[BIG SALE] 네온 티셔츠 - 반려인용 외 1건" readonly="">
		# </div>
		# </div>
		# .. 생략
		######################
		content_div = soup.find('div', id='content_div')

		if(content_div != None) :
			row_list = content_div.find_all('div', class_='row')
			for row_ctx in row_list :
				title_ctx = row_ctx.find('span', class_='title')
				value_ctx = row_ctx.find('input', {'type':'text'})
				if(title_ctx != None) and (value_ctx != None) :
					title_str = title_ctx.get_text().strip()
					value_str = ''
					if('value' in value_ctx.attrs) :
						value_str = value_ctx.attrs['value'].strip()
					
					if(title_str == '주문번호' ) : order_data.cor_order_no = value_str
					elif(title_str == '결제 금액' ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )
					elif(title_str == '상품 이름' ) : order_data.cor_content = value_str
					
		######################
		# 상품 No / 갯수
		#
		#---------------------------
		# <script>
		# var pageLink = "withoutBankPaySuccess";
		# if (pageLink == "product") {
		# /* Google Enhanced Ecommerce view_item Event*/
		# gtag('event', 'view_item', {
		# ..생략
		# i++;
		# contents.push({
		#            'id': 'blackwhitehoodie',
		#            'name': '[BIG SALE] 블랙 후드 - 화이트 로고 - 사이즈: M',
		#             'brand': '',
		#            "list_position": i,
		#            'quantity': '2',
		#             'price': '23000.0'
		#        });
		#         
		#         i++;
		#         contents.push({
		#             'id': 'untitled-19',
		#             'name': '[BIG SALE] 네온 티셔츠 - 반려인용 - SIZE: FREE',
		#             'brand': '',
		#             "list_position": i,
		#             'quantity': '2',
		#            'price': '28000.0'
		#         });
		#    
		# 
		# ..생략
		# </script>
		#
		######################
	
		split_list = html.split('<script>')
		for split_data in split_list :
			strip_idx = split_data.find("</script>")
			javascript_str = split_data[:strip_idx]
			if( 0 < javascript_str.find('transaction_id') ) and ( 0 < javascript_str.find('contents.push') ) :
				product_idx = -1
				sub_split_list = javascript_str.split('contents.push(')
				for sub_split_data in sub_split_list :
					product_idx += 1
					if( 0 < product_idx ) :
						strip_idx = sub_split_data.find(");")
						json_str = sub_split_data[:strip_idx].replace('"list_position": i,','"list_position": "i",').replace("'","\"")
						json_data = json.loads(json_str )
						for key in json_data.keys() :
							if(key == 'id') : order_data.cor_goods_code.append( json_data[key] ) 
							elif(key == 'quantity') : order_data.cod_count.append( int(__UTIL__.get_only_digit( json_data[key]) ) )		
				
		
	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass
	

		
def get_order_status_data( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호
		#
		# <span id="shopOrderUniqueNo" class="content">20200625KFYK3</span>
		######################
		cor_order_no_list = soup.find_all('span', id='shopOrderUniqueNo')
		for cor_order_no_ctx in cor_order_no_list :
			cor_order_no = cor_order_no_ctx.get_text().strip()
			#order_status_data.cos_order_no = cor_order_no_ctx.get_text().strip()	# 테스트용
		
		#if( True ) :	# 테스트용
		if( cor_order_no == order_status_data.cos_order_no ) :		
			######################
			# 상태
			# <span id="shopOrderStatus" class="content"><div><div>입금 대기</div></div></span>
			######################
			cor_memo_list = soup.find_all('span', id='shopOrderStatus')
			for cor_memo_ctx in cor_memo_list :
				if( order_status_data.cor_memo == '') : 
					cor_memo_str = cor_memo_ctx.get_text().strip()
					split_list = cor_memo_str.split('(')
					order_status_data.cor_memo = split_list[0].strip()
			

			
			######################
			# 물품 리스트
			# <div class="line-items"><div data-orderinfono="6511976" class="info designSettingElement shape"><div class="product"><div class="img"><a href="https://www.guilty-pleasure.co.kr/product/blackwhitehoodie"><img src="https://contents.sixshop.com/thumbnails/uploadedFiles/83291/product/image_1550894169760_750.jpg"></a></div><div class="text"><div class="name"><a href="https://www.guilty-pleasure.co.kr/product/blackwhitehoodie">[BIG SALE] 블랙 후드 - 화이트 로고</a></div><div class="option">사이즈: M</div></div></div><div class="qty">2</div><div class="price">46,000원</div></div><div data-orderinfono="6511977" class="info designSettingElement shape"><div class="product"><div class="img"><a href="https://www.guilty-pleasure.co.kr/product/untitled-19"><img src="https://contents.sixshop.com/thumbnails/uploadedFiles/83291/product/image_1554719899248_750.jpg"></a></div><div class="text"><div class="name"><a href="https://www.guilty-pleasure.co.kr/product/untitled-19">[BIG SALE] 네온 티셔츠 - 반려인용</a></div><div class="option">SIZE: FREE</div></div></div><div class="qty">2</div><div class="price">56,000원</div></div></div>
			######################
			div_list = soup.find_all('div', class_='line-items')
			for div_ctx in div_list :
				product_list = div_ctx.find_all('div')
				for product_ctx in product_list :
					if('data-orderinfono' in product_ctx.attrs ) :
						qty_ctx = product_ctx.find('div', class_='qty')
						if(qty_ctx != None) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( qty_ctx.get_text().strip() ) ) )
						name_ctx = product_ctx.find('div', class_='name')
						if(name_ctx != None) : 
							a_link_list = name_ctx.find_all('a')
							for a_link_ctx in a_link_list :
								if('href' in a_link_ctx.attrs ) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('product/')
									sub_split_list = split_list[1].split('&')
									order_status_data.cor_goods_code.append( sub_split_list[0].strip() )
			

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass
	
