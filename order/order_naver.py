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
#import requests

#from urllib import parse
from util import Util as __UTIL__
from app import config

import log as Log;  Log.Init()


if not sys.warnoptions:
    warnings.simplefilter("ignore")

	

def get_product_no( search_web_str, product_url ) :
	#
	# 일반 쇼핑몰에서 Naver Pay로 결제시 물품리스트를 갖고 오기 위해,
	# 사이트별 구분자를 지정하여 물품 product_no 값을 갖고 온다.
	# 
	# 보통의 경우
	# #if(search_web_str == 'smartstore.naver.com') : split_str = 'products%2F'
	# elif(search_web_str == 'shopping.naver.com') : split_str = 'itemdetail%2F'
	#
	# https://inflow.pay.naver.com/rd?no=510405156&tr=ppc&pType=M&retUrl=https%3A%2F%2Fsmartstore.naver.com%2Fmain%2Fproducts%2F4831126065&vcode=Fhb%2FGBt0p0DRXivjVel1kemF0g3tI732njFSPgWUWcSpFxsxHa1RcRwHVJhfAV0ov7ilUSoYDzaPwlp%2Fa%2BrUNh4f5Hbnr0%2BG4m5d90PoGeq6pbJn22nY9CA8H%2FtbNt9V
	# https://inflow.pay.naver.com/rd?no=510087473&tr=ppc&pType=M&retUrl=https%3A%2F%2Fshopping.naver.com%2Foutlink%2Fitemdetail%2F2626197453&vcode=%2FflhMsWgdm%2BhNZj1B%2F5jkemF0g3tI732njFSPgWUWcQ%2BWKfgG1QMpXloZ4nqu2N2zXTeqPt5qF5fj3w2YHJ%2BXzdlBOUxLPYeFfBW4Js07BgHWleX8QLPREVeLDv1aAHNXfrNQgXxsZZZMpBynk6ktg%3D%3D
	#
	# -------------------------------------------------------------------------------------
	# 일반 쇼핑몰 사이트에서 네이버 Pay 로 결제시
	# https://inflow.pay.naver.com/rd?no=200105165&amp;tr=ppc&amp;pType=M&amp;retUrl=https%3A%2F%2Fbiteme.co.kr%3A443%2Fgoods%2Fgoods_view.php%3Finflow%3DnaverPay%26goodsNo%3D1000001386&amp;vcode=6gkR4f%2BueWCHxh5U7i%2F4D%2BmF0g3tI732njFSPgWUWcTc00A%2BZSmBIKzvs31EWJ%2BKc4sprMR8hEQkHtRUNeehe59hb1OGRgFqwkZxfFL1HHFM7GOsy9uJiNnFA8dqm3kglmoSRIQ4ZOXVr7i%2Fh0w7K2ckzgE48t9M2LoWSnoNmew%3D
	# 
	#<a href="https://m.pay.naver.com/inflow/outlink?url=http%3A%2F%2Fandblank.com%2Fall%2F%3Fidx%3D384&amp;accountid=s_462b7202ce5f" class="N=a:ctm.name">
	#
	# https://m.pay.naver.com/inflow/outlink?url=http%3A%2F%2Fssfw.kr%2Fgoods%2Fgoods_view.php%3Finflow%3DnaverPay%26goodsNo%3D1000000078&amp;accountid=s_3c7b0ac5c58
	#
	# https://m.pay.naver.com/inflow/outlink?url=https%3A%2F%2Fwww.comercotte.com%2Fproduct%2Fcocomeal_horse&accountid=s_502d9f70ac8b
	rtn = ''
	
	__LOG__.Trace( product_url )
	
	'''
	split_str_list = [ 'products%2F', 'itemdetail%2F' ]
	
	if(search_web_str == 'smartstore.naver.com') or (search_web_str == 'shopping.naver.com') :		
		for split_str in split_str_list :
			split_list = product_url.split(split_str)
			if(len( split_list ) == 2 ) :		
				sub_split_list = split_list[1].split('&')
				rtn = sub_split_list[0].strip()
				break
				
	else :		# 일반 쇼핑몰 사이트에서 네이버 Pay 로 결제시
		split_str = 'naverPay%26'
		split_list = product_url.split(split_str)
		if(len( split_list ) == 2 ) :
			sub_split_list = split_list[1].split('&')
			product_no_str = sub_split_list[0].strip()
			product_split_list = product_no_str.split('%3D')
			if(len( product_split_list ) == 2 ) :
				rtn = product_split_list[1].strip()
	'''
	
	if( 0 < product_url.find('inflow.pay.naver.com')) :
		split_list = product_url.split('&vcode=')
		sub_split_list = split_list[0].split('%3D')
		
		product_no_idx = len(sub_split_list) - 1
		if(0 < sub_split_list[product_no_idx].find('%2F')) :
			last_split_list =  sub_split_list[product_no_idx].split('%2F')
			sub_product_no_idx = len(last_split_list) - 1
			rtn = last_split_list[sub_product_no_idx]
		else : 
			rtn = sub_split_list[product_no_idx]
			
	if(rtn == '') :
		if( 0 < product_url.find('m.pay.naver.com/inflow')) :
			split_list = product_url.split('&accountid=')
			sub_split_list = split_list[0].split('%3D')
			
			product_no_idx = len(sub_split_list) - 1
			if(0 < sub_split_list[product_no_idx].find('%2F')) :
				last_split_list =  sub_split_list[product_no_idx].split('%2F')
				sub_product_no_idx = len(last_split_list) - 1
				rtn = last_split_list[sub_product_no_idx]
			else : 
				rtn = sub_split_list[product_no_idx]
				
	
	return rtn

	
	
def get_order_data( order_data, html ) :
	try :
	
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호
		######################

		div_list = soup.find_all('div', class_='inf_view')
		for div_ctx in div_list :
			cor_order_no_ctx = div_ctx.find('strong')
			if(cor_order_no_ctx != None) : order_data.cor_order_no = cor_order_no_ctx.get_text().strip()

		######################
		# 결제금액
		######################
		td_list = soup.find_all('td', class_='amount')
		for td_ctx in td_list :
			total_price_sum_list = td_ctx.find_all('strong')
			for total_price_sum_ctx in total_price_sum_list :
				order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )
				
		######################
		# 물품리스트
		# <ul class="ord_plst">
		#					<li>
		#						<div class="ord_pdt">
		#							<a href="https://m.pay.naver.com/inflow/outlink?url=https%3A%2F%2Fsmartstore.naver.com%2Fmain%2Fproducts%2F4465040225&amp;accountid=s_177946496222724208" class="N=a:ctm.image thmb">
		#<img src="https://img.pay.naver.net/o/proxy/phinf/shop1/20190424_298/myfluffy_1556081827320052bU_JPEG/79388127947203564_1285072300.jpg?type=m120" alt="마이플러피 뀰 단품( 삑삑이,노즈워크)" width="65" height="65"><span class="loading _loading" style="display: none;"><span class="blind">로딩중...</span></span>									</a>
		#									<dl>
		#										<dt>
		#											<div class="additional_status">
		#														<span class="ico_npmember type_npay"><span class="blind">네이버플러스 멤버십</span></span>
		#											</div>
		#                                                <strong class="name_seller">[스마트스토어] 마이플러피</strong>
		#											
		#											<a href="https://m.pay.naver.com/inflow/outlink?url=https%3A%2F%2Fsmartstore.naver.com%2Fmain%2Fproducts%2F4465040225&amp;accountid=s_177946496222724208" class="N=a:ctm.name">
		#												마이플러피 뀰 단품( 삑삑이,노즈워크)
		#											</a>
		#										</dt>
		#
		#											<dd>
		#												<ul>
		#
		#																<li>
		#																	<span class="ic ic_green">옵션</span>
		#																	<span>선택: 냠냠이(삑삑이) </span>
		#																</li>
		#												</ul>
		#											</dd>
		#										<dd class="sum"><em>6,000</em>원</dd>
		#									</dl>
		#								</div>
		#							</li>
		#					</ul>
		
		#
		# <a href="https://m.pay.naver.com/inflow/outlink?url=https%3A%2F%2Fshopping.naver.com%2Foutlink%2Fitemdetail%2F4970055927&amp;accountid=s_32148008820823941" class="N=a:ctm.name">
		# 칼리 라텍스 점박이 카멜레온 장난감
		# </a>
		######################
		ul_list = soup.find_all('ul', class_='ord_plst')
		for ul_ctx in ul_list :
			product_idx = 0
			cor_content = ''
			product_list = ul_ctx.find_all('li')

			for product_ctx in product_list :
				
				#
				# 상품갯수 부분은 확인 필요
				# 주문수량이 없는 것도 있음.
				
				cod_count_value = 0
				dd_ctx = product_ctx.find('dd', class_='sum')
				if(dd_ctx != None) :
					cod_count_list = dd_ctx.find_all('span')
					for cod_count_ctx in cod_count_list :
						cod_count_value= int( __UTIL__.get_only_digit( cod_count_ctx.get_text().strip()) )
						break
				
				a_link_ctx = product_ctx.find('a', class_='N=a:ctm.name')
				if( a_link_ctx != None) :
				
					if( cod_count_value == 0 ) : order_data.cod_count.append( 1 )
					else : order_data.cod_count.append( cod_count_value )

					# 컨텐츠
					product_idx += 1
					if( product_idx == 1 ) : 
						cor_content = a_link_ctx.get_text().strip()
						order_data.cor_content = cor_content
					else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
					
					order_data.cor_goods_code.append( get_product_no( order_data.search_web_str, a_link_ctx.attrs['href'] ) )
		
	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass
		


def get_order_status_data( order_status_data, html ) :
	try :
	
		cor_order_no = ''

		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''			# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		orderlist_div_list = soup.find_all('div', id='content')
		for orderlist_div_ctx in orderlist_div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			
			######################
			# 주문번호
			######################
			div_ctx = orderlist_div_ctx.find('div', class_='ordernum')
			if( div_ctx != None) :
				cor_order_no_ctx = div_ctx.find('p', class_='number')
				cor_order_no = cor_order_no_ctx.get_text().strip()
				#order_status_data.cos_order_no = cor_order_no_ctx.get_text().strip()		# 테스트용
			
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	

				######################
				# 주문리스트
				######################
				ul_ctx = orderlist_div_ctx.find('ul', class_='order_list')
				if( ul_ctx != None) :
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						product_ctx = li_ctx.find('div', class_='product_info')
						if( product_ctx != None) :
							#
							# 상품 구매 개수
							cod_count_list = product_ctx.find_all('p', class_='ordernum')
							for cod_count_ctx in cod_count_list :
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( cod_count_ctx.get_text().strip() ) ) )
							
							#
							# 상품 product_no / 주문 상태 현황
							a_link_list = product_ctx.find_all('a')
							for a_link_ctx in a_link_list :
								if('class' in a_link_ctx.attrs ) :
									class_name_list = a_link_ctx.attrs['class']
									class_name = class_name_list[0]
									if(class_name.startswith('N=a:')) and (class_name.endswith('prodname')) :
										
										# 상품 product_no
										order_status_data.cor_goods_code.append( get_product_no( order_status_data.search_web_str, a_link_ctx.attrs['href'] ) )

										# 주문 상태 현황
										cor_memo_list = a_link_ctx.find_all('span', class_='icon_text')
										for cor_memo_ctx in cor_memo_list :
											order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
						

			
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass
	

	
	