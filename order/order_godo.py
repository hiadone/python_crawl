#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user

택배사 SNO 번호 확인 필요.
	- 8 : CJ대한통운

	
특이사항
	- 상품리스트에 hidden 으로 없는 경우에는 상품리스트 정보가 없음.
	
	
	
'''
import json
import time, re
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


INVOICE_COMPANY_SNO_HASH = { '8':'CJ대한통운' }

ORDER_STATUS_HASH = { 'o1':'입금대기' }

def get_invoice_company_name( company_name_sno ) :
	global INVOICE_COMPANY_SNO_HASH
	
	company_name = company_name_sno
	if( INVOICE_COMPANY_SNO_HASH.get( company_name_sno, -1) != -1) : company_name = INVOICE_COMPANY_SNO_HASH[company_name_sno]
	
	return company_name

def get_cor_order_no(text) :
	#
	# 문장에서 주문번호 추출 함수
	# - 아래의 형태 16자리 숫자
	# 20062 31539 301993

	cor_order_no = ''
	if(text != None) : 
		cor_order_no_re_list = re.compile('\d{16}').finditer( text )
		for cor_order_no_re in cor_order_no_re_list:
			cor_order_no = cor_order_no_re.group()

	return cor_order_no
	

def get_product_list(soup, order_data  ) :
	try :
		######################
		# 물품 리스트
		#
		# 물품리스트가 없는 사이트
		#
		# -- 물품별 상품번호 및 상품명, 갯수
		# <input type="hidden" name="naver-common-inflow-script-order-item" value="{sno:'3939',ordno:'2006231621317160',goodsno:'1000000060',optno:'376',goodsnm:'랑코 LANCO - 삐에로라니',ea:2,price:20000,is_parent:true}">
		#
		# -- 배송비를 제외한 물건값
		# <input type="hidden" id="naver-common-inflow-script-order" value="{goodsprice:20000}">
		######################
		product_list = soup.find_all('input', {'name':'naver-common-inflow-script-order-item'})
		product_idx = 0
		cor_content = ''
		for product_ctx in product_list :
			if('value' in product_ctx.attrs ) :
				product_idx += 1
				value_str = product_ctx.attrs['value']
				split_list = value_str.split(',')
				for split_ctx in split_list :
					# product no / 갯수
					if( split_ctx.strip().startswith('goodsno:') ) : order_data.cor_goods_code.append( split_ctx.replace('goodsno:','').replace("'","").strip() )
					if( split_ctx.strip().startswith('ea:') ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( split_ctx.replace('ea:','').replace("'","").strip()) ))
					
					# 컨텐츠
					if( split_ctx.strip().startswith('goodsnm:') ) : 
						if( product_idx == 1 ) : 
							cor_content = split_ctx.replace('goodsnm:','').replace("'","").strip()
							order_data.cor_content = cor_content
						else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
		
		#
		# 결제금액이 표시 되어 있지 않을때, 배송비를 뺀 가격 넣기.

		if(order_data.total_price_sum == 0 ) :
			total_price_list = soup.find_all('input', id='naver-common-inflow-script-order')
			for total_price_ctx in total_price_list :
				if('value' in total_price_ctx.attrs) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_ctx.attrs['value'] ) )
				
						
	except Exception as ex:
		__LOG__.Error('에러 : get_product_list')
		__LOG__.Error( ex )
		pass					



	
def get_order_data( order_data, html ) :
	try :
	
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호
		# <h2>주문번호 <strong>2006231621317160</strong></h2>
		######################

		div_list = soup.find_all('div', id='contents_wrap')
		if(len(div_list) == 0 ) : div_list = soup.find_all('div', id='content')
		
		for div_ctx in div_list :
			h2_list = div_ctx.find_all('h2')
			for h2_ctx in h2_list :
				cor_order_no_ctx = h2_ctx.find('strong')
				if(cor_order_no_ctx != None) : 
					order_data.cor_order_no = cor_order_no_ctx.get_text().strip()
					break

			######################
			# 결제금액
			# <li>금액 :
			#		<span class="prc">22,500원</span>
			#	</li>
			######################
			li_list = div_ctx.find_all('li')
			for li_ctx in li_list :
				total_price_sum_list = li_ctx.find_all('span', class_='prc')
				for total_price_sum_ctx in total_price_sum_list :
					order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )
			
					
		
		if(order_data.cor_order_no == '') :
			######################
			# 주문번호 / 주문금액
			#
			# -- mytrianon.co.kr 사이트
			#
			# <tr>
			# <th class="topline">주문번호</th>
			# <td class="topline">1593049514049</td>
			# </tr>
			# <tr>
			# <th>주문금액</th>
			# <td>45,000원</td>
			# </tr>
			######################

			div_list = soup.find_all('div', id='s_container')
			
			for div_ctx in div_list :
				tr_list = div_ctx.find_all('tr')

				for tr_ctx in tr_list :
					title_ctx = tr_ctx.find('th')
					value_ctx = tr_ctx.find('td')
					if( title_ctx != None) and ( value_ctx != None) :
						title_str = title_ctx.get_text().strip()
						value_str = value_ctx.get_text().strip()
						
						if(title_str == '주문번호') : order_data.cor_order_no = value_str
						elif(title_str == '주문금액') : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )
			
				#
				# 결제금액이 표시 되어 있지 않을때, 배송비를 뺀 가격 넣기.
				if(order_data.total_price_sum == 0 ) :
					total_price_list = div_ctx.find_all('input', id='naver-common-inflow-script-order')
					for total_price_ctx in total_price_list :
						if('value' in total_price_ctx.attrs) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_ctx.attrs['value'] ) )
						
		# 물품리스트				
		get_product_list(soup, order_data  )
		
		
	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass
	

def get_order_status_data( order_status_data, html ) :
	if(order_status_data.search_web_str == 'mytrianon.co.kr' ) : get_order_status_data_mytrianon( order_status_data, html )
	else : get_order_status_data_second( order_status_data, html )

		
def get_order_status_data_second( order_status_data, html ) :
	try :
	
		cor_order_no = ''

		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''			# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		orderlist_div_list = soup.find_all('div', class_='orderlist_wrap')
		if(len(orderlist_div_list) == 0 ) : orderlist_div_list = soup.find_all('div', id='content')
		
		for order_div_ctx in orderlist_div_list :
			if( cor_order_no != '') and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			
			######################
			# 주문번호
			#
			# <div class="order_number">
			# <div class="order_number_left">
			# 주문번호
			# 2006231539301993
			# </div>
			# <div class="order_number_right"><span class="order_date">2020-06-23</span></div>			</div>
			######################
			order_number_ctx = order_div_ctx.find('div', class_='order_number')
			if(order_number_ctx != None) :
				text = order_number_ctx.get_text().strip()
				cor_order_no = get_cor_order_no(text)
				#order_status_data.cos_order_no = get_cor_order_no(text)			# 테스트용
			else :
				order_number_ctx = order_div_ctx.find('h2', class_='my_tit')
				if(order_number_ctx != None) :
					text = order_number_ctx.get_text().strip()
					cor_order_no = get_cor_order_no(text)
					#order_status_data.cos_order_no = get_cor_order_no(text)			# 테스트용
				
				
				
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				ul_list = order_div_ctx.find_all('ul', class_='my_goods')
				for ul_ctx in ul_list :
					######################
					# 주문리스트
					# 상품 no
					# <ul class="my_goods" data-order-no="2006231539301993" data-order-goodsno="" data-order-status="o1">
					# <li>
					# <div class="info">
					# <a href="../goods/goods_view.php?goodsNo=1000001766">
					# <div class="itemhead">
					# <div class="img"><img src="/data/goods/20/06/24/1000001766/1000001766_list_089.jpg" width="50" alt="펫퍼로니 피자 장난감 (삑삑/바스락)" title="펫퍼로니 피자 장난감 (삑삑/바스락)" class="middle"></div>
					# </div>
					# <div class="itembody">
					# <dl>
					# <dt class="prd_name">펫퍼로니 피자 장난감 (삑삑/바스락)</dt>
					# <div class="order_info">
					# <div class="info_box">
					# <div class="info2">
					# 수량 : 2 | 13,800원
					# </div>
					# <div class="ing_chk">
					# <strong class="order_ing_btn">입금대기</strong>
					# </div>
					# .. 생략 </li>
					# </ul>
					######################
					a_link_list = ul_ctx.find_all('a')
					
					cor_goods_code_idx = 0		# 중복입력 방지
					for a_link_ctx in a_link_list : 
						if('href' in a_link_ctx.attrs ) :
							product_url = a_link_ctx.attrs['href']
							if(0 < product_url.find('goodsNo=') ) :
								split_list = product_url.split('goodsNo=')
								sub_split_list = split_list[1].split('&')
								if(cor_goods_code_idx == 0 ) : 
									order_status_data.cor_goods_code.append( sub_split_list[0].strip() )
									cor_goods_code_idx += 1
							
							# 주문 현황이 'a' 링크에 있는 경우
							# <a href="../mypage/order_view.php?orderNo=2006231713093613">
							# <span>
							# 주문상품
							# </span>
							# <strong class="icon_deli ing">입금대기</strong>
							# </a>
							if(0 < product_url.find('orderNo=') ) :
								title_ctx = a_link_ctx.find('span')
								value_ctx = a_link_ctx.find('strong')
								if(title_ctx != None) and (value_ctx != None) :
									title_str = title_ctx.get_text().strip()
									if(title_str == '주문상품') : order_status_data.cor_memo = value_ctx.get_text().strip()
								
					
					
					div_list = ul_ctx.find_all('div', class_='order_info')
					for div_ctx in div_list :
					
						######################
						# 구매갯수
						# <div class="info2">
						#					수량 : 2 | 46,000원
						#				</div>
						######################
						ea_list = div_ctx.find_all('div', class_='info2')
						for ea_ctx in ea_list :
							ea_str = ea_ctx.get_text().strip()
							if(0 == ea_str.find('수량') ) :
								split_list = ea_str.split('|')
								split_list[0].strip()
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( split_list[0].strip() ) ) )
						
						######################
						# 상태
						# <div class="ing_chk">
						#<strong class="order_ing_btn">입금대기</strong>
						#			</div>
						######################
						cor_memo_list = div_ctx.find_all('div', class_='ing_chk')
						for cor_memo_ctx in cor_memo_list :
							order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
							
							
					######################
					# 구매갯수
					#
					# <p class="hd v2">
					# <span class="info">
					# 수량 : 2 | 28,000원
					# </span>
					# <strong class="icon_deli ing">입금대기</strong>
					# </p>
					######################
					if(order_status_data.cor_memo == '') and (len(order_status_data.cod_count) == 0 ) :
						p_ctx = ul_ctx.find('p', class_='hd v2')
						if(p_ctx != None) :
							cor_memo_ctx = p_ctx.find('strong')
							if(cor_memo_ctx != None) : order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
							
							ea_ctx = p_ctx.find('span', class_='info')
							if(ea_ctx != None) :
								ea_str = ea_ctx.get_text().strip()
								if(0 == ea_str.find('수량') ) :
									split_list = ea_str.split('|')
									split_list[0].strip()
									order_status_data.cod_count.append( int( __UTIL__.get_only_digit( split_list[0].strip() ) ) )		
		
		# 상품 수량에 대한 정보가 없을때, 수량을 1로 넣어줌
		if(len(order_status_data.cod_count) == 0 ) :
			for i in range( len(order_status_data.cor_goods_code)) :
				order_status_data.cod_count.append(1)

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass

		

###############################################
#
# mytrianon.co.kr 에서만 사용
#
###############################################

def get_order_status_data_mytrianon( order_status_data, html ) :
	try :
	
		cor_order_no = ''


		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''			# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		#__LOG__.Trace( soup )
		orderlist_div_list = soup.find_all('div', class_='content_box')
		
		for order_div_ctx in orderlist_div_list :
			if( cor_order_no != '') and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <input name="ordno" type="hidden" value="1593049514049"/>
			######################
			order_number_ctx = order_div_ctx.find('input', {'name':'ordno'})
			if(order_number_ctx != None) :
				if('value' in order_number_ctx.attrs) :
					cor_order_no = order_number_ctx.attrs['value']
					#order_status_data.cos_order_no = order_number_ctx.attrs['value']		# 테스트용
				
				
				
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				table_ctx = order_div_ctx.find('table', class_='orderitem-list')
				if( table_ctx != None) :
					tr_list = table_ctx.find_all('tr')
					for tr_ctx in tr_list :
						######################
						# 주문리스트
						# 상품 no
						# <tr>
						# <td align="center" height="60" width="60"><a href="/shop/goods/goods_view.php?&amp;goodsno=114"><img onerror="this.src='/shop/data/skin/newskin/img/common/noimg_100.gif'" src="../data/goods/1574345326256s0.jpg" width="50"/></a></td>
						# <td>
						# <a href="/shop/goods/goods_view.php?&amp;goodsno=114">[원목 플레이하우스] 플레이 캐슬_독서 &amp; 미술책상 변신 어린이텐트
						#     [프티베어 의자/프티베어 의자]</a>
						# </td>
						# <td align="center">42,000원</td>
						# <td align="center">1개</td>
						# <td align="center" class="stxt"><font color="#14a83b">주문접수</font></td>
						# <td align="center">
						# </td>
						# </tr>
						######################
						
						td_list = tr_ctx.find_all('td')
						td_idx = -1
						for td_ctx in td_list :
							td_idx += 1
							if(td_idx == 3 ) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( td_ctx.get_text().strip() ) ) )
							elif(td_idx == 4 ) : order_status_data.cor_memo = td_ctx.get_text().strip()
							elif(td_idx == 1 ) :
								a_link_ctx = td_ctx.find('a')
								if( a_link_ctx != None ) :
									if('href' in a_link_ctx.attrs ) :
										product_url = a_link_ctx.attrs['href']
										if(0 < product_url.find('goodsno=') ) :
											split_list = product_url.split('goodsno=')
											sub_split_list = split_list[1].split('&')
											order_status_data.cor_goods_code.append( sub_split_list[0].strip() )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass		
	