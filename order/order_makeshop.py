#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user

특이 사이트
	- oraeorae.com
	
'''
import json
import time
import os, signal, re
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

def get_order_data( order_data, html ) :
	if(order_data.search_web_str == 'ecofoam.co.kr' ) : get_order_data_ecofoam( order_data, html )
	else : get_order_data_second( order_data, html )


def get_order_data_second( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		#<p class="complete-msg"><label id="hname2">고은선</label>님의 주문이 완료되었습니다.<br><br>
		#귀하의 주문확인 번호는 <span style="color: #0000a0; font-weight: bold;">20200625115626-10112259211</span>입니다.<br>
		#귀하의 제품 구입에 따른 적립금 <span style="color: #0000a0;">800원</span>은 배송과 함께 바로 적립됩니다. <br>
		#저희가 확인 후 바로 보내드립니다.<br><br>
		#</p>
		#
		# 20200625115626-10112259211
		# 20200624181552-33516590736
		# 20200625120225-90144716033
		# 20200624181352-40286746788
		#
		# -----------------------------------------------
		# function receipt(temp) {
		# if (temp == '1' || temp == '2') {
		# window.open('http://pg1.makeshop.co.kr/pg/receipt/credit.pg?ordernum=20200625143303leehyunejung&adminuser=affetto','receipt','width=300,height=500,scrollbars=yes');
		# } else if (temp == '3') {   // 간편결제
		# window.open('http://epg.makeshop.co.kr/pg/receipt/credit.pg?ordernum=20200625143303leehyunejung&adminuser=affetto','receipt','width=300,height=500,scrollbars=yes');
		# } else {
		# window.open('http://www.payinfra.com/credit/receipt.pg?ordernum=20200625143303leehyunejung&terminal_id=MSaffetto2','receipt','width=300,height=500,scrollbars=yes');
		# }
		# }
		# 
		######################
		cor_order_no_ctx = soup.find('p', class_='complete-msg')
		if(cor_order_no_ctx != None) :
			text = cor_order_no_ctx.get_text().strip()
			order_data.cor_order_no = get_cor_order_no(text)
		
		# 주문번호를 얻지 못할때, javascript 에서 얻어옴.
		#
		if( order_data.cor_order_no == '' ) :
			split_list = html.split('<script type="text/javascript">')
			for split_data in split_list :
				strip_idx = split_data.find("</script>")
				javascript_str = split_data[:strip_idx]
				if( 0 <= javascript_str.find('window.open(') ) and ( 0 < javascript_str.find('?ordernum=') ) :
					sub_split_list = javascript_str.split('?ordernum=')
					cor_order_no_list = sub_split_list[1].split('&')
					order_data.cor_order_no = cor_order_no_list[0].strip()

		
		######################
		# 결재금액
		# <p class="complete-price">결제금액 <em class="color_f1191f ">18,500</em>원</p>
		#
		# -- oraeorae.com
		# <strong id="mk_totalprice" style="color:;">36,000원</strong>
		######################
		total_price_sum_ctx = soup.find('p', class_='complete-price')
		if(total_price_sum_ctx == None) :
			total_price_sum_ctx = soup.find('strong', id='mk_totalprice')
			if(total_price_sum_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )	
		else :
			em_list = total_price_sum_ctx.find_all('em')
			for em_ctx in em_list :		
				order_data.total_price_sum = int( __UTIL__.get_only_digit( em_ctx.get_text().strip() ) )	
		
		
		######################
		# 물품리스트
		# <div class="title">
		# <a href="/m/product.html?branduid=2117813">블루 소가죽목걸이 <span class="fa fa-angle-right"></span></a>                                    <span class="num">수량 : 2개</span>
		# </div>
		######################
		
		div_list = soup.find_all('div', class_='product_info')
		for div_ctx in div_list :
			product_idx = 0
			cor_content = ''
		
			product_div_list = div_ctx.find_all('div', class_='title')
			for product_div_ctx in product_div_list :
				ea_ctx = product_div_ctx.find('span', class_='num')
				if( ea_ctx != None ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
				product_url_list = product_div_ctx.find_all('a')
				for product_url_ctx in product_url_list :
					if('href' in product_url_ctx.attrs) :
						product_idx += 1
						product_url = product_url_ctx.attrs['href']
						product_no_list = product_url.split('branduid=')
						order_data.cor_goods_code.append( product_no_list[1].strip() )
						if( product_idx == 1 ) : 
							cor_content = product_url_ctx.get_text().strip() 	# 상품명
							order_data.cor_content = cor_content
						else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
						
		
		
		######################
		# 물품리스트
		# -- oraeorae.com
		#
		# <dl class="item clearfix">
		# <dt>
		# <a href="/m/product.html?branduid=615687">
		# [I&amp;G메딕스] 뉴플렉스 카디오 케어                                            <span class="arrow_grey">▶</span></a>
		# </dt>
		# <dd>수량 : 2개</dd>
		# </dl>
		######################
		if(order_data.cor_content ==  '') :
			product_idx = 0
			cor_content = ''
			div_list = soup.find_all('dl', class_='item clearfix')
			for div_ctx in div_list :
				ea_ctx = div_ctx.find('dd')
				if( ea_ctx != None ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
				product_div_ctx = div_ctx.find('dt')
				if( product_div_ctx != None ) : 
					product_url_list = product_div_ctx.find_all('a')
					for product_url_ctx in product_url_list :
						if('href' in product_url_ctx.attrs) :
							product_idx += 1
							product_url = product_url_ctx.attrs['href']
							product_no_list = product_url.split('branduid=')
							order_data.cor_goods_code.append( product_no_list[1].strip() )
							if( product_idx == 1 ) : 
								cor_content = product_url_ctx.get_text().strip() 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
								

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass


def get_order_data_ecofoam( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		#<tr>
		#<th><span class="ft_c_a ft_b_n">주문번호</span></th><td>20200625114756-09879435149</td>
		#</tr>
		#
		# 20200625115626-10112259211
		# 20200624181552-33516590736
		# 20200625120225-90144716033
		# 20200624181352-40286746788
		######################
		cor_order_no_ctx = soup.find('div', class_='pay_info')
		if(cor_order_no_ctx != None) :
			text = cor_order_no_ctx.get_text().strip()
			order_data.cor_order_no = get_cor_order_no(text)
			
		######################
		# 결재금액
		# <p class="complete-price">결제금액 <em class="color_f1191f ">18,500</em>원</p>
		#
		# -- oraeorae.com
		# <strong id="mk_totalprice" style="color:;">36,000원</strong>
		######################
		total_price_sum_ctx = soup.find('p', class_='complete-price')
		if(total_price_sum_ctx == None) :
			total_price_sum_ctx = soup.find('strong', id='mk_totalprice')
			if(total_price_sum_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )	
		else :
			em_list = total_price_sum_ctx.find_all('em')
			for em_ctx in em_list :		
				order_data.total_price_sum = int( __UTIL__.get_only_digit( em_ctx.get_text().strip() ) )	
		
		######################
		# 물품리스트
		# <li>
		# <figure>
		# <div class="basketLeft">
		# <a href="/m/product.html?branduid=841206"><img src="/shopimages/ecofoam/0450010000053.jpg" class="response100" alt="상품명"></a>
		# </div>
		# <figcaption class="basketRight">
		# <p class="pname bold">도그자리 플랫</p>
		# <p>판매가 : 104,000 원</p>
		# <p>수량 : 2개</p>
		# <p>
		# 1,040원 적립
		# </p>
		# <p class="options"><span class="smaller_p ft_eb">옵션</span> 색상 : 마블 화이트, 타입 : A타입 </p>
		# </figcaption>
		# </figure>
		# </li>
		######################
		
		div_list = soup.find_all('div', class_='product_info')
		for div_ctx in div_list :
			product_idx = 0
			cor_content = ''
		
			product_div_list = div_ctx.find_all('li')
			for product_div_ctx in product_div_list :
				
				p_list = product_div_ctx.find_all('p')
				for p_ctx in p_list :
					if('class' in p_ctx.attrs ) :
						class_name_list = p_ctx.attrs['class']
						if(class_name_list[0] == 'pname') : 
							product_idx += 1
							if( product_idx == 1 ) : 
								cor_content = p_ctx.get_text().strip() 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
					else :
						value_str = p_ctx.get_text().strip()
						if(0 <= value_str.find('수량') ) and (0 < value_str.find('개') ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( value_str ) ) )
				
				product_url_ctx = product_div_ctx.find('a')
				if( product_url_ctx != None ) :
					if('href' in product_url_ctx.attrs) :
						product_url = product_url_ctx.attrs['href']
						product_no_list = product_url.split('branduid=')
						order_data.cor_goods_code.append( product_no_list[1].strip() )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_ecofoam')
		__LOG__.Error( ex )
		pass


		
		
		
		
		
		
		
def get_order_status_data( order_status_data, html ) :
	try :
		cor_order_no = ''
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용

		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		MK_orderlist_ctx = soup.find('div', class_='MK_orderlist')
		
		if(MK_orderlist_ctx != None) :
			li_list = MK_orderlist_ctx.find_all('li')
			for li_ctx in li_list :
				if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출

				######################
				# 주문번호
				#
				#<h4><span class="bold">주문번호</span> [20200624181552-33516590736]</h4>
				#
				#---------------------------------
				# <h4><span class="bold">二쇰Ц踰덊샇</span> [20200625143303]</h4>
				######################
				cor_order_no_list = li_ctx.find_all('h4')
				if(len(cor_order_no_list) == 0 ) : cor_order_no_list = li_ctx.find_all('h5')
				for cor_order_no_ctx in cor_order_no_list :
					
					text = cor_order_no_ctx.get_text().replace('[','').replace(']','').strip()
					if(0 <= text.find('주문번호') ) : 
						order_status_data.cos_order_no = get_cor_order_no(text)
						if( order_status_data.cos_order_no == '' ) : 
							cor_order_no = get_cor_order_no_second(text)
							#order_status_data.cos_order_no = get_cor_order_no_second(text)		# 테스트용
				
				#if( True ) :	# 테스트용
				if( cor_order_no == order_status_data.cos_order_no ) :
				
					######################
					# 물품리스트
					#
					# <dt class="product-name">
					# <a href="/m/product.html?branduid=2117813">
					# <span class="delivery_state">(결제대기)</span> 블루 소가죽목걸이                            </a>
					# <span class="listTitleRight">
					# 수량 : 2                                                                <a href="/m/board.html?code=coates1024_board2&amp;page=1&amp;type=i&amp;branduid=2117813&amp;search_type=one_product&amp;ordernum=20200624181552-33516590736_1" class="btn_write">리뷰작성 <span class="fa fa-chevron-right"></span></a>
					# </span>
					# </dt>
					######################
					
					div_list = li_ctx.find_all('dt', class_='product-name')
					for div_ctx in div_list :
						cor_memo_ctx = div_ctx.find('span', class_='delivery_state')
						if(cor_memo_ctx != None) : 
							if( order_status_data.cor_memo == '') : order_status_data.cor_memo = cor_memo_ctx.get_text().replace(')','').replace('(','').strip()
						
						product_url_ctx = div_ctx.find('a')
						if(product_url_ctx != None) : 
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								product_no_list = product_url.split('branduid=')
								order_status_data.cor_goods_code.append( product_no_list[1].strip() )
						
						ea_span_list = div_ctx.find_all('span')
						for ea_span_ctx in ea_span_list :
							ea_span_text = ea_span_ctx.get_text().strip()
							if(0 <= ea_span_text.find('수량')) :
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
								
					######################
					# 물품리스트
					#
					# <dl class="item clearfix">
					# <dt>
					# <a href="/m/product.html?branduid=615687">
					# [I&amp;G메딕스] 뉴플렉스 카디오 케어                                </a>
					# <a class="review" href="/m/review_list.html?branduid=615687&amp;in_product=YES"><span class="blue-btn box-round">리뷰</span></a>
					# </dt>
					# <dd class="item-amount">수량 : 2개</dd>
					# </dl>
					######################			
					if(len(order_status_data.cor_goods_code) == 0) :
						dl_ctx = li_ctx.find('dl', class_='item clearfix')
						if(dl_ctx != None) :
							dt_ctx = dl_ctx.find('dt')
							dd_ctx = dl_ctx.find('dd', class_="item-amount")
							if(dt_ctx != None ) and (dd_ctx != None) :
								ea_span_text = dd_ctx.get_text().strip()
								if(0 <= ea_span_text.find('수량')) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
									
								product_url_ctx = dt_ctx.find('a')
								if(product_url_ctx != None) : 
									if('href' in product_url_ctx.attrs) :
										product_url = product_url_ctx.attrs['href']
										product_no_list = product_url.split('branduid=')
										order_status_data.cor_goods_code.append( product_no_list[1].strip() )


			#
			# 주문상태값이 다른 곳에 있는 경우
			# 
			# <div class="detail pay-detail">
			# <h5><span class="fa fa-credit-card fa-lg"></span> 결제/주문 정보 <a class="btn_White" href="#none"><span class="fa fa fa-chevron-down fa-rotate-180"></span></a></h5>
			# <table style="display: table;">
			# .. 생략
			# <tbody>
			# .. 생략
			# <tr>
			# <th>주문현황</th>
			# <td>결제대기</td>
			# </tr>
			# </tbody>
			# </table>

			if( order_status_data.cor_memo == '' ) :
				#div_list = li_ctx.find_all('div', class_='detail')
				#div_list = li_ctx.find_all('div')
				#for div_ctx in div_list :
				tr_list = li_ctx.find_all('tr')
				for tr_ctx in tr_list :
					title_ctx = tr_ctx.find('th')
					value_ctx = tr_ctx.find('td')
					if( title_ctx != None ) and ( value_ctx != None ) :
						title_str = title_ctx.get_text().strip()
						value_str = value_ctx.get_text().strip()
						if(title_str == '주문현황') and ( order_status_data.cor_memo == '') : order_status_data.cor_memo = value_str
						elif(title_str == '입금현황')  and ( order_status_data.cor_memo == '') : order_status_data.cor_memo = value_str
						 
						
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_second')
		__LOG__.Error( ex )
		pass


####################################################################################################
#
#
####################################################################################################

					
def get_cor_order_no(text) :
	#
	# 문장에서 주문번호 추출 함수
	# - 아래의 형태 14자리-11자리 숫자
	# 20200625115626-10112259211
	# 20200624181552-33516590736
	# 20200625120225-90144716033
	# 20200624181352-40286746788
	# 20200624183646-35425573008
	cor_order_no = ''
	if(text != None) : 
		cor_order_no_re_list = re.compile('\d{14}-\d{11}').finditer( text )
		for cor_order_no_re in cor_order_no_re_list:
			cor_order_no = cor_order_no_re.group()

	return cor_order_no

def get_cor_order_no_second(text) :
	#
	# 문장에서 주문번호 추출 함수
	# - 아래의 형태 14자리
	# 20200 62514 3303
	#
	cor_order_no = ''
	if(text != None) : 
		cor_order_no_re_list = re.compile('\d{14}').finditer( text )
		for cor_order_no_re in cor_order_no_re_list:
			cor_order_no = cor_order_no_re.group()

	return cor_order_no
	
def get_cod_count(text) :
	#
	# 문장에서 수량 추출 함수
	# 수량 : 2   
	#
	cod_count = ''
	if(text != None) : 
		cod_count_re_list = re.compile('\d{1,5}').finditer( text )
		for cod_count_re in cod_count_re_list:
			cod_count = cod_count_re.group()

	return cod_count

	

	