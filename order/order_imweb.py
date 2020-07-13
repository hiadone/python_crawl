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
		
		######################
		# 주문번호 / 가격
		#
		# <div class="table_payment_complete">
		# <table>
		# <tbody><tr>
		# <th>입금계좌 안내</th>
		# <td>
		# kb국민은행<br>
		# 47870101260724<br>
		# 두잇디자인연구소<br>
		# <strong class="text-brand">58,000원</strong>
		# </td>
		# </tr>
		# .. 생략
		#  					<th>주문번호</th>
		# <td>2020062441336</td>
		# </tr>
		# 	
		# ..생략											</tbody></table>
		# .. 생략
		# </div>
		######################

		split_data = html.split("ADVANCED_TRACE.appendCode('payment_complete_code',")

		if(len(split_data) == 2) :
			strip_idx = split_data[1].find(");")
			json_str = split_data[1][:strip_idx]
			json_data = json.loads( json_str )
			
			for json_key in json_data.keys() :
				if(json_key == 'order_no') : order_data.cor_order_no = str(json_data[json_key])
				elif(json_key == 'total_price') : order_data.total_price_sum = json_data[json_key]
				#__LOG__.Trace( ' %s : %s' % (json_key, str(json_data[json_key])) )
				
		######################
		# 상품리스트
		# ADVANCED_TRACE.appendCode('payment_complete_code',{"order_no":2020062430593,"total_price":12500,"currency":"KRW","pay_type":"\uc2e0\uc6a9\uce74\ub4dc"});
		# 
		# GOOGLE_ANAUYTICS.AddorderInfo("1062", "지독 롭 더 마이크로브", "10000", "1");
		# FB_PIXEL.AddOrderInfo("1062", "1", "10000");
		# KAKAO_PIXEL.AddorderInfo("지독 롭 더 마이크로브", "1", "10000");
		# CHANNEL_TRACE.AddorderInfo("지독 롭 더 마이크로브", "1", "10000");
		######################

		split_data = html.split("GOOGLE_ANAUYTICS.AddorderInfo(")
		
		product_idx = -1
		cor_content = ''
		for split_ctx in split_data :
			product_idx += 1
			if(0 < product_idx ) :
				strip_idx = split_data[product_idx].find(");")
				json_str = split_data[product_idx][:strip_idx]
				sub_split_list = json_str.split(',')
				sub_idx = -1
				product_no = ''
				product_ea = 0
				for sub_split_ctx in sub_split_list :
					sub_idx += 1
					if( sub_idx == 0 ) : product_no = sub_split_ctx.replace('"','').strip()			# product_no
					elif( sub_idx == 1 ) :	
						if( product_idx == 1 ) : 
							cor_content = sub_split_ctx.replace('"','').strip() 	# 상품명
							order_data.cor_content = cor_content
						else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
					elif( sub_idx == 3 ) : product_ea = int(sub_split_ctx.replace('"','').strip())	# 수량
					
				order_data.cor_goods_code.append( product_no )
				order_data.cod_count.append( product_ea )
				

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass	
		
		
def get_order_status_data(order_status_data, html ) :
	try :
		
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''			# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호
		#
		# <div class="order_tit clearfix margin-bottom-xl">
		#	<a href="/shop_mypage/?m2=order" class="btl bt-arrow-left hidden-xs hidden-sm" aria-hidden="true"><span class="sr-only">뒤로가기</span></a>
		#	<h6 class="no-margin" style="display: inline-block;">
		#		<span style="padding-right: 5px;">주문번호</span>
		#		<span class="text-brand">2020062430593</span>
		#	</h6>
		######################
		
		div_list = soup.find_all('div', class_='order_tit')
		for div_ctx in div_list :
			h6_list = div_ctx.find_all('h6')
			for h6_ctx in h6_list :
				span_list = h6_ctx.find_all('span', class_='text-brand')
				for span_ctx in span_list :
					cor_order_no = span_ctx.get_text().strip()
					#order_status_data.cos_order_no = span_ctx.get_text().strip()	# 테스트용
					break
		#if( True ) :	# 테스트용
		if( cor_order_no == order_status_data.cos_order_no ) :	
			######################
			# 주문리스트
			# 
			# <div class="item_wrap">
			# <div class="tip-off item">
			# <h6>상품 정보</h6>
			# <div class="row no-padding item_repeat">
			# <div class="col-xs-12 col_ctr ">
			# <div class="shop_item_thumb tabled full-width">
			# <div class="table-cell vertical-middle" style="width: 80%">
			# <a href="/314/?idx=1062" target="_blank" class="tabled full-width">
			# <div class="table-cell vertical-top" style="width: 70px;"><img alt="상품 이미지" src="https://cdn.imweb.me/thumbnail/20200403/1deeda1bc8d6d.jpg" width="58" height="58"></div>
			# <span class="table-cell vertical-top">
			# <div>지독 롭 더 마이크로브</div>
			# <div class="text-13 text-gray-bright">10,000원 / 1 개</div>										</span>
			# </a>
			# </div>
			# <div class="table-cell vertical-middle text-center" style="width: 20%; padding-left: 10px;">
			# <div class="text-brand" style="margin-bottom:5px;">배송중</div>
			# </div>
			# </div>
			# <div style="margin-left: 70px;">
			# <a href="javascript:;" onclick="SITE_SHOP_MYPAGE.trackingParcel('CJ','359042788344');" class="cart-btn-tools btn btn-order-track">배송조회</a>							</div>
			# </div>
			# </div>
			# <div class="row">
			# <div class="col-xs-8 pay-txt col_ctr">
			# <p>상품가격</p><p>배송비</p>					</div>
			# <div class="col-xs-4 pay-number col_ctr">
			# <p>10,000원</p><p>2,500원</p>					</div>
			# </div>
			# ... 생략...
			#</div>
			######################
			div_list = soup.find_all('div', class_='row no-padding item_repeat')
			for div_ctx in div_list :
				# 상태
				cor_memo_div_list = div_ctx.find_all('div', class_='table-cell vertical-middle text-center')
				for cor_memo_div_ctx in cor_memo_div_list :
					cor_memo_list = cor_memo_div_ctx.find_all('div')
					for cor_memo_ctx in cor_memo_list :
						if('class' in cor_memo_ctx.attrs) :
							class_name_list = cor_memo_ctx.attrs['class']
							if( class_name_list[0].startswith('text-') ) : 
								if( order_status_data.cor_memo == '') : order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
				
				# 상품 product no / 갯수 / 운송장
				a_link_list = div_ctx.find_all('a')
				for a_link_ctx in a_link_list :
					a_link_str = a_link_ctx.get_text().strip()

					if(a_link_str != '배송조회') :
						if('href' in a_link_ctx.attrs) :
							product_url = a_link_ctx.attrs['href']
							if(0 < product_url.find('?idx=')) :
								product_split_data = product_url.split('?idx=')
								sub_product_split_data = product_split_data[1].split('&')
								product_no = sub_product_split_data[0].strip()
								order_status_data.cor_goods_code.append( product_no )
								
								product_list = a_link_ctx.find_all('span', class_='table-cell')
								for product_ctx in product_list :
									ea_div_list = product_ctx.find_all('div')
									for ea_div_ctx in ea_div_list :
										if('class' in ea_div_ctx.attrs) :
											tmp_ea_str = ea_div_ctx.get_text().strip()
											if( 0 < tmp_ea_str.find('/')) and ( 0 < tmp_ea_str.find('개')) and ( 0 < tmp_ea_str.find('원')):
												split_data = tmp_ea_str.split('/')
												order_status_data.cod_count.append( int( __UTIL__.get_only_digit( split_data[1].strip() ) ) )
				
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass		
	
	
	