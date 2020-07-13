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

from util import Util as __UTIL__
from app import config

import log as Log;  Log.Init()


if not sys.warnoptions:
    warnings.simplefilter("ignore")

	
	
def get_order_data( order_data, html ) :
	try :

		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호
		#
		# ---- case A 일때
		# <div id="orderfin" class="wrap_inner">
		# .. 생략
		# <table class="tbl_order">
		# .. 생략
		# <tbody>
		# <tr>
		# <th scope="row">주문번호</th>
		# <td><strong>20200630-5352F</strong></td>
		# </tr>
		# .. 생략
		# <tr>
		# .. 생략
		# <th scope="row">총 결제금액</th>
		# <td>21,000</td> <!-- 실결제금액 -->
		# </tr>
		# 	
		# </tbody>
		# </table>
		# </div>
		#
		#
		# ------- case B 일때
		# <div id="orderfin">
		# <div class="box_common">
		# <h3>주문이 완료되었습니다.</h3>
		# <div class="list_common half">
		# <dl>
		# <dt>주문번호</dt>
		# <dd><strong>20200630-6B041</strong></dd>
		# .. 생략	
		# <dt>총 주문금액</dt>
		# <dd>KRW34,500</dd>
		# <dt>총 결제금액</dt>
		# <dd>KRW34,500</dd>
		# </dl>
		# </div>
		######################
		
		cor_order_no_ctx = soup.find('div', id='orderfin')
		if(cor_order_no_ctx != None) :
			# case A 일때
			table_ctx = cor_order_no_ctx.find('table', class_='tbl_order')
			if( table_ctx != None ) :
				tr_list = table_ctx.find_all('tr')
				for tr_ctx in tr_list :
					title_ctx = tr_ctx.find('th')
					value_ctx = tr_ctx.find('td')
					if( title_ctx != None) and ( value_ctx != None) :
						title_str = title_ctx.get_text().strip()
						value_str = value_ctx.get_text().strip()
						
						if(title_str == '주문번호') : order_data.cor_order_no = value_str
						elif(title_str == '총 결제금액') : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )	
		
			# case B 일때
			if( order_data.cor_order_no == '') :
				div_ctx = cor_order_no_ctx.find('div', class_='list_common half')
				if( div_ctx != None ) :
					dl_list = div_ctx.find_all('dl')
					for dl_ctx in dl_list :
						dt_list = dl_ctx.find_all('dt')
						dd_list = dl_ctx.find_all('dd')
						dt_idx = -1
						for dt_ctx in dt_list :
							dt_idx += 1
							title_str = dt_ctx.get_text().strip()
							value_str = dd_list[dt_idx].get_text().strip()
							
							if(title_str == '주문번호') : order_data.cor_order_no = value_str
							elif(title_str == '총 결제금액') : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )

		
			######################
			# 물품 리스트
			#
			# ---- case A 일때
			# <ul class="list_cart orderfin"><li>
			# <div class="box">
			# <div class="img"><a href="https://m.howlpot.com/shop/detail.php?pno=F7664060CC52BC6F3D620BCEDC94A4B6&amp;rURL=https%3A%2F%2Fm.howlpot.com%2Fshop%2Forder_finish.php&amp;ctype=1&amp;cno1="><img src="https://howlpotdesign.wisacdn.com/_data/product/e4fc17c8c0bdde6a3f1109b8b43ff576.jpg" width="80" height="80"></a></div>
			# <div class="info">
			# <p><a href="https://m.howlpot.com/shop/detail.php?pno=F7664060CC52BC6F3D620BCEDC94A4B6&amp;rURL=https%3A%2F%2Fm.howlpot.com%2Fshop%2Forder_finish.php&amp;ctype=1&amp;cno1=">노즈워크 토이_라면</a></p>
			# <p>
			# <strong>18,000</strong> | 1 개
			# <span>(적립금 : 180)</span>
			# </p>
			# <div> </div>
			# </div>
			# </div>
			# <div class="total">
			# 총금액 <strong>18,000</strong>
			# </div>
			# </li>
			# </ul>
			#
			#
			# ------- case B 일때
			# <table class="tbl_col">
			# .. 생략 ..
			# <tbody><tr>
			# <td class="img"><a href="https://m.smallstuff.kr/shop/detail.php?pno=5EF698CD9FE650923EA331C15AF3B160&amp;rURL=https%3A%2F%2Fm.smallstuff.kr%2Fshop%2Forder_finish.php&amp;ctype=1&amp;cno1="><img src="https://img.mywisa.com/freeimg/smallstuff/_data/product/202002/22/d072c69c9ca146873179a338bf53065f.jpg" width="80" height="80"></a></td>
			# <td class="left">
			# <b><a href="https://m.smallstuff.kr/shop/detail.php?pno=5EF698CD9FE650923EA331C15AF3B160&amp;rURL=https%3A%2F%2Fm.smallstuff.kr%2Fshop%2Forder_finish.php&amp;ctype=1&amp;cno1=">PAPER CUP TOY 3PACK</a></b><br>
			# MENU : SMILE, MILK, COCOA<br>
			# 가격 : KRW32,000<br>
			# 수량 : 1<br>
			# 총 금액 : <b>KRW32,000</b><br>
			# 적립금 : KRW320
			# </td>
			# </tr><tr>
			# </tr></tbody>
			# </table>
			######################
			
			# case A 일때
			ul_ctx = cor_order_no_ctx.find('ul', class_='list_cart orderfin')
			if( ul_ctx != None ) :
				product_idx = 0
				cor_content = ''
				li_list = ul_ctx.find_all('li')
				for li_ctx in li_list :
					p_list = li_ctx.find_all('p')
					for p_ctx in p_list :
						ea_str = p_ctx.get_text().strip()
						if(0 < ea_str.find('|') ) and (0 < ea_str.find('개') ) :
							split_list = ea_str.split('|')
							sub_split_list = split_list[1].split('(')
							order_data.cod_count.append( int( __UTIL__.get_only_digit( sub_split_list[0].strip() ) ) )
							
						product_url_ctx= p_ctx.find('a')
						if(product_url_ctx != None ) :
							if('href' in product_url_ctx.attrs) :
								product_idx += 1
								product_url = product_url_ctx.attrs['href']
								url_split_list = product_url.split('?pno=')
								sub_split_list = url_split_list[1].split('&')
								order_data.cor_goods_code.append( sub_split_list[0].strip() )
								if( product_idx == 1 ) : 
									cor_content = product_url_ctx.get_text().strip() 	# 상품명
									order_data.cor_content = cor_content
								else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
			# case B 일때			
			if(order_data.cor_content == '') :
				product_idx = 0
				cor_content = ''
				table_ctx = cor_order_no_ctx.find('table', class_='tbl_col')
				if( table_ctx != None ) :
					tr_list = table_ctx.find_all('tr')
					for tr_ctx in tr_list :
						td_ctx = tr_ctx.find('td', class_='left')
						if( td_ctx != None) :
							# 수량 추출
							value_str = td_ctx.get_text().strip()
							split_list = value_str.split('수량 :')
							sub_split_list = split_list[1].split(':')
							order_data.cod_count.append( int( __UTIL__.get_only_digit( sub_split_list[0].strip() ) ) )
							
							# 상품 no 추출
							product_url_ctx = td_ctx.find('a')
							if(product_url_ctx != None ) :
								if('href' in product_url_ctx.attrs) :
									product_idx += 1
									product_url = product_url_ctx.attrs['href']
									url_split_list = product_url.split('?pno=')
									sub_split_list = url_split_list[1].split('&')
									order_data.cor_goods_code.append( sub_split_list[0].strip() )
									if( product_idx == 1 ) : 
										cor_content = product_url_ctx.get_text().strip() 	# 상품명
										order_data.cor_content = cor_content
									else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
			

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
		
		order_detail_ctx = soup.find('div', id='order_detail')
		if( order_detail_ctx != None) :
			######################
			# 주문번호
			#
			# <p class="order_no">20200630-5352F</p>
			#---------------------------------------------
			# <p class="info">주문번호 <strong>20200630-6B041</strong> 상세 내역입니다. </p>
			######################
					
			div_list = order_detail_ctx.find_all('p', class_='order_no')
			for div_ctx in div_list :
				cor_order_no = div_ctx.get_text().strip()
				#order_status_data.cos_order_no = div_ctx.get_text().strip()	# 테스트용
			
			if( order_status_data.cos_order_no == '' ) :
				div_list = order_detail_ctx.find_all('p', class_='info')
				for div_ctx in div_list :
					strong_ctx = div_ctx.find('strong')
					if( strong_ctx != None ) : 
						cor_order_no = strong_ctx.get_text().strip()
						#order_status_data.cos_order_no = strong_ctx.get_text().strip()		# 테스트용
			
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				######################
				# 주문리스트
				#
				# ㈜하울팟 - HOWLPOT
				# ------------------------------------
				# 상품 no
				# <ul class="list_cart order"><li>
				# <div class="box">
				# <div class="img"><a href="https://m.howlpot.com/shop/detail.php?pno=F7664060CC52BC6F3D620BCEDC94A4B6"><img src="https://howlpotdesign.wisacdn.com/_data/product/e4fc17c8c0bdde6a3f1109b8b43ff576.jpg" width="50" height="50" barder="0"></a></div>
				# <div class="info">
				# <p><a href="https://m.howlpot.com/shop/detail.php?pno=F7664060CC52BC6F3D620BCEDC94A4B6">노즈워크 토이_라면</a></p>
				# <p>
				# <strong>18,000</strong> | 1 개
				# <span>(적립금 : 180)</span>
				# </p>
				# <p></p>
				# <p></p>
				# </div>
				# </div>
				# <div class="total">
				# 총 합계금액 <strong>18,000</strong>
				# </div>
				# <div class="stat">
				# 미입금 <span class="box_btn small"><a href="https://m.howlpot.com/shop/product_review.php?pno=F7664060CC52BC6F3D620BCEDC94A4B6&amp;startup=true" class="crema-new-review-link" data-product-code="266">후기작성</a></span>
				# </div>
				# </li>
				# </ul>
				######################
				ul_ctx = order_detail_ctx.find('ul', class_="list_cart order")
				if( ul_ctx != None) :
						
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						stat_div_ctx = li_ctx.find('div', class_='stat')
						if( stat_div_ctx != None ) :
							stat_str = stat_div_ctx.get_text().strip()
							split_list = stat_str.split(' ')
							if( order_status_data.cor_memo == '') : order_status_data.cor_memo = split_list[0].strip()
							
						info_div_ctx = li_ctx.find('div', class_='info')
						if( info_div_ctx != None ) :
							ea_str = info_div_ctx.get_text().strip()
							split_list = ea_str.split('|')
							if(len(split_list) == 2) :
								sub_split_list = split_list[1].split('개')
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( sub_split_list[0].strip() ) ) )
							
							a_link_ctx = info_div_ctx.find('a')
							if( a_link_ctx != None) :
								if('href' in a_link_ctx.attrs ) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('pno=')
									sub_split_list = split_list[1].split('&')
									order_status_data.cor_goods_code.append( sub_split_list[0].strip() )
									
									
				######################
				# 주문리스트
				#
				# small stuff
				# ---------------------------
				# 상품 no
				# <ul class="list_prd"><li>
				# <div class="box">
				# <div class="prd_detail">
				# <div class="img"><a href="https://m.smallstuff.kr/shop/detail.php?pno=5EF698CD9FE650923EA331C15AF3B160"><img src="https://img.mywisa.com/freeimg/smallstuff/_data/product/202002/22/d072c69c9ca146873179a338bf53065f.jpg" width="50" height="50" barder="0"></a></div>
				# <p class="name"><a href="https://m.smallstuff.kr/shop/detail.php?pno=5EF698CD9FE650923EA331C15AF3B160">PAPER CUP TOY 3PACK</a></p>
				# <p>(MENU:SMILE, MILK, COCOA)</p>
				# <p></p>
				# </div>
				# <div class="price">
				#  <p>적립금 : KRW320</p>
				# <p>상품가격 : KRW32,000</p>
				# <p>구매수량 : 1 개</p>
				# <p class="pay">총 합계금액 : <strong>KRW32,000</strong></p>
				# </div>
				# <div class="delivery">
				# <p class="stat">미입금</p>
				# <p class="confirm"><a href="https://m.smallstuff.kr/shop/product_review.php?pno=5EF698CD9FE650923EA331C15AF3B160&amp;startup=true" class="crema-new-review-link" data-product-code="366">후기작성</a></p>
				# </div>
				# </div>
				# </li>
				# </ul>
				######################
				ul_ctx = order_detail_ctx.find('ul', class_="list_prd")
				if( ul_ctx != None) :
						
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						stat_div_ctx = li_ctx.find('p', class_='stat')
						if( stat_div_ctx != None ) : order_status_data.cor_memo = stat_div_ctx.get_text().strip()
						
						info_div_ctx = li_ctx.find('p', class_='name')
						if( info_div_ctx != None ) :						
							a_link_ctx = info_div_ctx.find('a')
							if( a_link_ctx != None) :
								if('href' in a_link_ctx.attrs ) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('pno=')
									sub_split_list = split_list[1].split('&')
									order_status_data.cor_goods_code.append( sub_split_list[0].strip() )
									
						price_div_ctx = li_ctx.find('div', class_='price')
						if( price_div_ctx != None ) :
							p_list = price_div_ctx.find_all('p')
							for p_ctx in p_list :
								ea_str = p_ctx.get_text().strip()
								if(0 <= ea_str.find('구매수량') ) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( ea_str ) ) )

							

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data')
		__LOG__.Error( ex )
		pass

	