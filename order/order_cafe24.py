#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user

	
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
	if(0 < html.find('var EC_FRONT_EXTERNAL_SCRIPT_VARIABLE_DATA =') ) : get_order_data_fourth( order_data, html )
	elif(0 < html.find('cpa["order"]=[') ) and (0 < html.find('_nao["cnv"]') ) : get_order_data_third( order_data, html )
	else : get_order_data_second( order_data, html )

	
def get_cor_order_no_value( soup, order_data ) :
	try :
	
		######################
		# 주문번호
		#
		# <div class="infomation">
		# <p><strong>고객님의 주문이 <br>정상적으로 완료되었습니다.</strong></p>
		# <p>(주문번호: 20200626-0000066)</p>
		# </div>
		#------------------------------------------------------
		# <div class="orderInfo">
		# <p>
		# <strong>고객님의 주문이 완료 되었습니다.</strong>
		# 주문내역 및 배송에 관한 안내는 <a href="/myshop/order/list.html">주문조회</a> 를 통하여 확인 가능합니다.
		# </p>
		# <ul>
		# <li>주문번호 : <strong>20200630-0000016</strong>
		# </li>
		# .. 생략
		# </ul>
		# </div>
		######################
		if( order_data.cor_order_no == '' ) :
			cor_order_no_ctx = soup.find('div', class_='infomation')
			if(cor_order_no_ctx != None) :
				text = cor_order_no_ctx.get_text().strip()
				order_data.cor_order_no = get_cor_order_no(text)
			
		if( order_data.cor_order_no == '' ) :	
			cor_order_no_ctx = soup.find('div', class_='orderInfo')
			if(cor_order_no_ctx != None) : 
				text = cor_order_no_ctx.get_text().strip()
				order_data.cor_order_no = get_cor_order_no(text)
		
		######################
		# 주문번호
		#
		# <li class="number">
		# <strong>ORDER NUMBER</strong><span>20200626-0000072</span>
		# </li>
		######################
		if( order_data.cor_order_no == '' ) :	
			cor_order_no_ctx = soup.find('div', class_='orderInfo')
			if(cor_order_no_ctx != None) :
				order_data.cor_order_no = get_cor_order_no( cor_order_no_ctx.get_text().strip() )
				
				
		######################
		# 주문번호 / 결재금액
		#
		# <tr>
		# <th scope="row">주문번호</th>
		# <td class="right"><span class="txtEm">20200626-0009337</span></td>
		# </tr>
		#<tr>
		#<th scope="row">결제금액</th>
		#<td class="right">
		#<span class="txtEm">
		#88,600원                                        <span class="refer displaynone">()</span>
		#</span>
		#</td>
		#</tr>
		######################
		if( order_data.cor_order_no == '' ) :	
			cor_order_no_ctx = soup.find('div', class_='resultInfo')
			if(cor_order_no_ctx != None) :
				tr_list = cor_order_no_ctx.find_all('tr')
				for tr_ctx in tr_list :
					title_ctx = tr_ctx.find('th')
					value_ctx = tr_ctx.find('td')
					if( title_ctx != None) and ( value_ctx != None) :
						title_str = title_ctx.get_text().strip()
						value_str = value_ctx.get_text().strip()
						
						if(title_str == '주문번호') : order_data.cor_order_no = get_cor_order_no(value_str)
						elif(title_str == '결제금액') : 
							split_data = value_str.split('원')
							order_data.total_price_sum = int( __UTIL__.get_only_digit( split_data[0].strip() ) )
	except Exception as ex:
		__LOG__.Error('에러 : get_cor_order_no')
		__LOG__.Error( ex )
		pass			

		

def get_total_price_sum( soup, order_data ) :
	try :
		######################
		# 결재금액
		# <tr class="totalPay">
		# <th scope="row"><strong>최종결제금액</strong></th>
		# <td class="price">
		# 42,000원 <span class="tail displaynone"></span>
		# </td>
		# </tr>
		#
		# ----------------------------------------
		# <strong class="total">42,000</strong>
		#----------------------------------------
		#
		# <div id="order_layer_detail" class="totalDetail ec-base-layer">
		# <div class="header">
		# <h3>총 주문금액 상세내역</h3>
		# </div>
		# <div class="content">
		# <p>KRW 17,500</p>
		# <ul class="ec-base-desc typeDot gLarge rightDD">
		# </div>
		######################
		
		if( order_data.total_price_sum == 0 ) :
			total_price_sum_rt_ctx = soup.find('tr', class_='totalPay')
			if(total_price_sum_rt_ctx != None) :
				total_price_sum_ctx = total_price_sum_rt_ctx.find('td', class_='price')
				if(total_price_sum_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )	
		
		if( order_data.total_price_sum == 0 ) :
			total_price_sum_rt_ctx = soup.find('div', class_='contents')
			if(total_price_sum_rt_ctx != None) :
				total_price_sum_ctx = total_price_sum_rt_ctx.find('strong', class_='total')
				if(total_price_sum_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_ctx.get_text().strip() ) )	
				
				
		if( order_data.total_price_sum == 0 ) :
			total_price_sum_rt_ctx = soup.find('div', id='order_layer_detail')
			if(total_price_sum_rt_ctx != None) :
				total_price_sum_ctx = total_price_sum_rt_ctx.find('div', class_='content')
				if(total_price_sum_ctx != None) : 
					price_ctx = total_price_sum_ctx.find('p')
					if(price_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( price_ctx.get_text().strip() ) )	

	except Exception as ex:
		__LOG__.Error('에러 : get_total_price_sum')
		__LOG__.Error( ex )
		pass


		
def get_order_data_second( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		# 주문번호
		get_cor_order_no_value( soup, order_data )
		
		# 결제 금액
		get_total_price_sum( soup, order_data )
		
		######################
		# 물품리스트
		#
		# <div class="xans-element- xans-order xans-order-normalresultlist orderArea"><div class="prdInfo xans-record-">
		# <div class="description">
		# <p class="prdImg"><a href="/product/detail.html?product_no=780&amp;cate_no=53"><img src="//m.rudolphshop.kr/web/product/tiny/20200308/7b8e7b4936c2f704f7309901a54c8748.jpg" onerror="this.src='//img.echosting.cafe24.com/thumb/img_product_small.gif';" width="73" height="73" alt=""></a></p>
		# <strong class="prdName" title="상품명"><a href="/product/detail.html?product_no=780&amp;cate_no=53">[프로덴] 플라그오프 덴탈케어본 482g</a></strong><ul class="info">
		# <li class="displaynone">무이자할부 상품</li>
		# <li title="적립금" class="mileage">-</li>
		# <li>기본배송<span class="displaynone">(해외배송가능)</span>
		# </li>
		# <li class="price">
		# <span title="판매가"><span class=""><strong>35,000</strong>원 <span class="displaynone"></span> </span><span class="displaynone"><strong>35,000</strong>원 <span class="displaynone"></span> </span></span><strong title="수량" class="quantity">2개</strong>
		# </li>
		# </ul>
		# </div>
		# <p class="option ">[옵션: 호박&amp;치킨]</p>
		# <p class="prdTotal"><strong>70,000</strong>원 <span class="displaynone"></span></p>
		# </div>
		# <div class="prdInfo xans-record-">
		# <div class="description">
		# <p class="prdImg"><a href="/product/detail.html?product_no=567&amp;cate_no=80"><img src="//m.rudolphshop.kr/web/product/tiny/20191125/4af47eda02fb14d686a5f419d3aa602b.jpg" onerror="this.src='//img.echosting.cafe24.com/thumb/img_product_small.gif';" width="73" height="73" alt=""></a></p>
		# <strong class="prdName" title="상품명"><a href="/product/detail.html?product_no=567&amp;cate_no=80">[릴라러브스잇] 아이케어/이어클렌저</a></strong><ul class="info">
		# <li class="displaynone">무이자할부 상품</li>
		# <li title="적립금" class="mileage">-</li>
		# <li>기본배송<span class="displaynone">(해외배송가능)</span>
		# </li>
		# <li class="price">
		# <span title="판매가"><span class=""><strong>25,000</strong>원 <span class="displaynone"></span> </span><span class="displaynone"><strong>25,000</strong>원 <span class="displaynone"></span> </span></span><strong title="수량" class="quantity">2개</strong>
		# </li>
		# </ul>
		# </div>
		# <p class="option ">[옵션: 아이케어]</p>
		# <p class="prdTotal"><strong>50,000</strong>원 <span class="displaynone"></span></p>
		# </div>
		# </div>
		######################
		product_idx = 0
		cor_content = ''
			
		div_list = soup.find_all('div', class_='xans-element- xans-order xans-order-normalresultlist orderArea')
		for div_ctx in div_list :
			product_div_list = div_ctx.find_all('div', class_='prdInfo xans-record-')
			for product_div_ctx in product_div_list :
				product_idx += 1
				ea_ctx = product_div_ctx.find('strong', class_='quantity')
				if( ea_ctx != None ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
				
				product_name_ctx = product_div_ctx.find('strong', class_='prdName')
				if(product_name_ctx != None ) :
					product_url_list = product_name_ctx.find_all('a')
					for product_url_ctx in product_url_list :
						if('href' in product_url_ctx.attrs) :
							product_url = product_url_ctx.attrs['href']
							product_no_list = product_url.split('product_no=')
							
							if(len(product_no_list) == 1 ) :	# <a href="/product/욜로홀로-푸룸-칙펫-무향-안전하고-깨끗한-살균-탈취-소독수-650ml/443/category/27/" 
								sub_product_no_list = product_url.split('/')
								order_data.cor_goods_code.append( sub_product_no_list[3].strip() )
								
							elif(len(product_no_list) == 2 ) :
								sub_product_no_split_data = product_no_list[1].split('&')
								order_data.cor_goods_code.append( sub_product_no_split_data[0].strip() )
								
							if( product_idx == 1 ) : 
								cor_content = product_url_ctx.get_text().strip() 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
						
		######################
		# 물품리스트
		#
		# <div class="xans-element- xans-order xans-order-normalresultlist"><div class="ec-base-prdInfo xans-record-">
		# <div class="prdBox">
		# <div class="thumbnail"><a href="/product/detail.html?product_no=20&amp;cate_no=24"><img src="//m.pethroom.com/web/product/tiny/20200519/542bf3a07b519c4b67f1a16a37416fa3.png" alt="" width="90" height="90"></a></div>
		# <div class="description">
		# <strong class="prdName" title="상품명"> <a href="/product/relax-shower/20/category/24/" class="ec-product-name">RELAX SHOWER</a></strong>
		# <ul class="info">
		# <li class="displaynone">무이자할부 상품</li>
		# <li title="유효기간" class="displaynone"> 내 사용</li>
		# <li title="옵션">
		# <p class="option displaynone"></p>                                    
		# </li>
		# <li class="price">
		# <span class="priceValue " title="판매가">
		# 27,900원                                                    <span class="refer displaynone">()</span>
		# </span>
		# <span class="displaynone" title="할인판매가">27,900원 <span class="refer displaynone">()</span></span>
		# <span title="수량" class="quantity">2개</span>
		# ... 생략
		# <div class="ec-base-prdInfo xans-record-">
		# <div class="prdBox">
		# <div class="thumbnail"><a href="/product/detail.html?product_no=47&amp;cate_no=57"><img src="//m.pethroom.com/web/product/tiny/20200519/d1f56a742c8ab755427d8ec61142dbab.png" alt="" width="90" height="90"></a></div>
		# <div class="description">
		# <strong class="prdName" title="상품명"> <a href="/product/pet-doctor-spray-plus-set/47/category/57/" class="ec-product-name">PET-DOCTOR SPRAY PLUS+ SET</a></strong>
		# <ul class="info">
		# ...생략
		# <span class="displaynone" title="할인판매가">32,800원 <span class="refer displaynone">()</span></span>
		# <span title="수량" class="quantity">1개</span>
		# ... 생략
		# </div>
		######################
		
		if( order_data.cor_content == '') :
			product_idx = 0
			cor_content = ''
			div_list = soup.find_all('div', class_='xans-element- xans-order xans-order-normalresultlist')
			for div_ctx in div_list :
				product_div_list = div_ctx.find_all('div', class_='ec-base-prdInfo xans-record-')
				for product_div_ctx in product_div_list :
					product_idx += 1
					__LOG__.Trace('product_idx : %d' % (product_idx))
					ea_ctx = product_div_ctx.find('span', class_='quantity')
					if( ea_ctx != None ) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
					
					product_name_ctx = product_div_ctx.find('strong', class_='prdName')
					if(product_name_ctx != None ) :
						product_url_ctx= product_name_ctx.find('a')
						if(product_url_ctx != None ) :
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								product_no_list = product_url.split('/')
								order_data.cor_goods_code.append( product_no_list[3].strip() )
								if( product_idx == 1 ) : 
									cor_content = product_url_ctx.get_text().strip() 	# 상품명
									order_data.cor_content = cor_content
								else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
							
	except Exception as ex:
		__LOG__.Error('에러 : get_order_data')
		__LOG__.Error( ex )
		pass



def get_order_data_third( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		get_cor_order_no_value( soup, order_data )
		
		
		######################
		# 물품리스트
		# <script type="text/javascript">
		# // Account ID 적용
		# if (!wcs_add) var wcs_add = {};
		# wcs_add["wa"] = "s_248291d0a81c";
		# 
		# // 추가 정보로 넣을 객체 생성
		# var cpa={};
		# var _nao={};
		# 
		# if (wcs.isCPA) {
		# // 주문채널 정보 추가
		# cpa["chn"] = "AD";
		# 
		# // 주문 정보 추가
		# cpa["order"]=[{"oid":"20200626-0000072","poid":"","pid":1154,"parpid":"","name":"HB Cooling Vest Lemon","cnt":1,"price":34000},{"oid":"20200626-0000072","poid":"","pid":661,"parpid":"","name":"\ub124\ucd94\ub7f4 \uc19d [\ub2e8\ubaa8\uc6a9]","cnt":1,"price":33000}];
		# 
		# // wcs.CPAOrder 함수 호출 - _nao를 인자로 입력함.
		# wcs.CPAOrder(cpa);
		# }
		# 
		# // 총 구매액을 셋팅
		# _nao["cnv"] = wcs.cnv("1", 67000);
		# 
		# wcs_do(_nao);
		# 
		# </script>
		######################

		split_list = html.split('<script type="text/javascript">')
		for split_data in split_list :
			if(0 < split_data.find('cpa["order"]=[') ) and (0 < split_data.find('_nao["cnv"]') ) :
				strip_idx = split_data.find("</script>")
				javascript_str = split_data[:strip_idx]
				
				# 결제금액
				sub_split_list = javascript_str.split('wcs.cnv(')
				strip_idx = sub_split_list[1].find(";")
				json_str = sub_split_list[1][:strip_idx]
				price_list = json_str.split(',')
				if(len(price_list) == 2 ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( price_list[1].strip() ) )	
				
				# 물품리스트
				sub_split_list = javascript_str.split('cpa["order"]=')
				strip_idx = sub_split_list[1].find(";")
				json_str = sub_split_list[1][:strip_idx]
				
				json_data_list = json.loads( json_str )
				product_idx = 0
				cor_content = ''
				for json_data in json_data_list :
					product_idx += 1
					for json_key in json_data.keys() :
						if(json_key == 'pid') : order_data.cor_goods_code.append( json_data[json_key] )
						elif(json_key == 'cnt') : order_data.cod_count.append( int( json_data[json_key] ) )
						elif(json_key == 'name') : 
							if( product_idx == 1 ) : 
								cor_content = json_data[json_key] 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )

						#__LOG__.Trace( ' %s : %s' % (json_key, str(json_data[json_key])) )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_third')
		__LOG__.Error( ex )
		pass

		

def get_order_data_fourth( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호 / 결제금액 / 물품리스트
		#
		# <script type="text/javascript">
		# var EC_FRONT_EXTERNAL_SCRIPT_VARIABLE_DATA = {"total_basic_ship_fee":3000,"payed_amount":43000,"order_id":"20200701-0000024","order_product":[{"product_name":"\uc904\ub9ac\uc5e3 \ud380\uce6d \ucf00\uc774\ud504 ( 2 color )","product_price":40000,"quantity":1,"product_no":281,"product_code":"P00000KV","sub_total_price":40000,"category_no_1":25,"category_name_1":"CAPE ","sum_total_opt_price":42000}],"member_id_crypt":"66d19aa6c39baf4465a66bc94915384d577c4e538180fe1f43f288c6e921f588","common_member_id_crypt":"66d19aa6c39baf4465a66bc94915384d577c4e538180fe1f43f288c6e921f588"};
		# </script>
		######################
		split_list = html.split('<script type="text/javascript">')
		for split_data in split_list :
			if(0 < split_data.find('var EC_FRONT_EXTERNAL_SCRIPT_VARIABLE_DATA =') ) :
				strip_idx = split_data.find("</script>")
				javascript_str = split_data[:strip_idx]
				sub_split_list = javascript_str.split('var EC_FRONT_EXTERNAL_SCRIPT_VARIABLE_DATA =')
				strip_idx = sub_split_list[1].find(";")
				json_str = sub_split_list[1][:strip_idx]
				
				json_data = json.loads( json_str )
				product_idx = 0
				cor_content = ''
						
				for json_key in json_data.keys() :
					#__LOG__.Trace( ' %s : %s' % (json_key, str(json_data[json_key])) )
					if(json_key == 'order_id') : order_data.cor_order_no = json_data[json_key]
					elif(json_key == 'payed_amount') : order_data.total_price_sum = int( json_data[json_key] )	
					elif(json_key == 'order_product') : 
						array_list = json_data[json_key]
						for array_ctx in array_list :
							product_idx += 1
							for key in array_ctx.keys() :
								#__LOG__.Trace( ' %s : %s' % (key, array_ctx[key]) )
								if(key == 'quantity') : order_data.cod_count.append( int( array_ctx[key] ) )
								elif(key == 'product_no') : order_data.cor_goods_code.append( array_ctx[key] )
								elif(key == 'product_name') : 
									if( product_idx == 1 ) : 
										cor_content = array_ctx[key] 	# 상품명
										order_data.cor_content = cor_content
									else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
								
	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_fourth')
		__LOG__.Error( ex )
		pass





##############################################################
#
# 주문결과
##############################################################		
def get_order_status_data( order_status_data, html ) :
	#__LOG__.Trace( order_status_data.search_web_str )
	
	if(order_status_data.search_web_str == 'yolohollo.com' ) : get_order_status_data_yolohollo( order_status_data, html )
	
	elif(order_status_data.search_web_str == 'j-o-yi.com' ) : get_order_status_data_third( order_status_data, html )
	elif(order_status_data.search_web_str == 'ba-ttang.com' ) : get_order_status_data_third( order_status_data, html )
	elif(order_status_data.search_web_str == 'bokseul.com' ) : get_order_status_data_third( order_status_data, html )
	elif(order_status_data.search_web_str == 'oneofus.co.kr' ) : get_order_status_data_third( order_status_data, html )
	elif(order_status_data.search_web_str == 'boondog.co.kr' ) : get_order_status_data_third( order_status_data, html )
	elif(order_status_data.search_web_str == 'studioaloitti.com' ) : get_order_status_data_third( order_status_data, html )
	
	elif(order_status_data.search_web_str == 'hutsandbay.com' ) : get_order_status_data_hutsandbay( order_status_data, html )
	elif(order_status_data.search_web_str == 'babiana.co.kr' ) : get_order_status_data_babiana( order_status_data, html )
	elif(order_status_data.search_web_str == 'studioalive.co.kr' ) : get_order_status_data_studioalive( order_status_data, html )
	
	elif(order_status_data.search_web_str == 'vemvem.com' ) : get_order_status_data_vemvem( order_status_data, html )
	else : get_order_status_data_second( order_status_data, html )

	
def get_order_status_data_second( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		div_list = soup.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetail xans-record-')
		#if(len(div_list) == 0 ) : div_list = soup.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetail xans-record-')
		if(len(div_list) == 0 ) : div_list = soup.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetail p25 xans-record-')

		#__LOG__.Trace( len(div_list) )
		#if( len(div_list) == 0 ) : __LOG__.Trace( html )
		
		for div_ctx in div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <tr>
			# <th scope="row">주문번호</th>
			# <td>20200629-0000058</td>
			# </tr>
			######################
			cor_order_no_ctx = div_ctx.find('div', class_='contents')
			if( cor_order_no_ctx != None ) :
				text = cor_order_no_ctx.get_text().strip()
				if(0 <= text.find('주문번호') ) : 
					cor_order_no = get_cor_order_no(text)
					#order_status_data.cos_order_no = get_cor_order_no(text)		# 테스트용

			
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				######################
				# 물품리스트
				#
				# <div class="prdInfo xans-record-">
				# <div class="description">
				# <p class="prdImg"><a href="/product/detail.html?product_no=3806&amp;cate_no=6189"><img src="http://img.echosting.cafe24.com/thumb/img_product_small.gif" alt="" onerror="this.src='http://img.echosting.cafe24.com/thumb/img_product_small.gif';" width="73" height="73"></a></p>
				# <strong class="prdName" title="상품명"><a href="/product/detail.html?product_no=3806&amp;cate_no=6189">별빛 바다 COOL MAX 탱크탑 (블루)</a></strong>
				# <ul class="info">
				# <li class="displaynone"><a href="#" target="_self"></a></li>
				# <li class="displaynone"><a href="#none" class="line" onclick="">[]</a></li>
				# <li>배송 : 기본배송 <span class="displaynone">(해외배송가능)</span>
				# </li>
				# <li class="displaynone">무이자할부 상품</li>
				# </ul>
				# <p class="prdTotal">
				# <span title="판매가">
				# <span class="discount">
				# <strong>21,100</strong>원                                        <span class="displaynone"></span>
				# </span>
				# <span class="">
				# <strong>10,100</strong>원                                        <span class="displaynone"></span>
				# </span>
				# </span>
				# <strong title="수량" class="quantity">2</strong>개
				# </p>
				# </div>
				# <p class="option ">[옵션: S]</p>
				# <p class="status" title="주문처리상태">
				# 입금전                            <span class="store"></span>
				# <span class="addition displaynone"><strong class="cancel"><a href="order_detail_cs.html?product_no=3806&amp;order_id=20200629-0000058&amp;ord_item_code=20200629-0000058-01" target="_blank">[상세정보]</a></strong></span>
				# <span class="button">
				# <a href="/board/product/write.html?board_no=4&amp;product_no=3806&amp;order_id=20200629-0000058" class="btnBasic displaynone">구매후기</a>
				# <a href="#none" class="btnBasic displaynone" onclick="OrderHistory.withdraw('C','20200629-0000058|3806|000A|47271','', 'F')">취소철회</a>
				# <a href="#none" class="btnBasic displaynone" onclick="OrderHistory.withdraw('E','20200629-0000058|3806|000A|47271','', 'F')">교환철회</a>
				# <a href="#none" class="btnBasic displaynone" onclick="OrderHistory.withdraw('R','20200629-0000058|3806|000A|47271','', 'F')">반품철회</a>
				# </span>
				# </p>
				# </div>
				#
				#-----------------------------------------------------------
				# <div class="prdFoot" title="주문처리상태">
				# <div class="gLeft">
				# 입금전                                <span class="store"></span>
				# <span class="ec-base-qty displaynone"><strong class="cancel"><a href="order_detail_cs.html?product_no=19&amp;order_id=20200626-0000179&amp;ord_item_code=20200626-0000179-01" target="_blank">[상세정보]</a></strong></span>
				# </div>
				# <div class="gRight">
				#  <a href="#none" onclick="" class="btnStrong displaynone">리뷰작성</a>
				# <a href="/board/smartreview/read.html" onclick="" class="btnBasic displaynone">리뷰확인</a>
				# </span>                                <a href="#none" class="btnNormal mini displaynone" onclick="OrderHistory.withdraw('C','20200626-0000179|19|000K|14363','', 'F')">취소철회</a>
				# <a href="#none" class="btnNormal mini displaynone" onclick="OrderHistory.withdraw('E','20200626-0000179|19|000K|14363','', 'F')">교환철회</a>
				# <a href="#none" class="btnNormal mini displaynone" onclick="OrderHistory.withdraw('R','20200626-0000179|19|000K|14363','', 'F')">반품철회</a>
				# </div>
				# </div>
				######################
				
				product_list = div_ctx.find_all('div', class_='prdInfo xans-record-')
				if(len(product_list) == 0 ) : product_list = div_ctx.find_all('div', class_='ec-base-prdInfo xans-record-')
				
				
				for product_ctx in product_list :
					#__LOG__.Trace( product_ctx )
					cor_memo_ctx = div_ctx.find('span', class_='delivery_state')
					if(cor_memo_ctx != None) : order_status_data.cor_memo = cor_memo_ctx.get_text().replace(')','').replace('(','').strip()
					
					prdname_list = product_ctx.find_all('p', class_='prdImg')		
					if(len(prdname_list) == 0 ) : prdname_list = product_ctx.find_all('div', class_='thumbnail')
					add_product_cnt = 0
					for prdname_ctx in prdname_list :
						product_url_ctx = prdname_ctx.find('a')
						if(product_url_ctx != None) : 
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								product_no_list = product_url.split('product_no=')
								if(len(product_no_list) == 2 ) :
									sub_product_no_list = product_no_list[1].split('&')
									order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )
									add_product_cnt += 1
					
					if(add_product_cnt == 0 ) :
						prdname_list = product_ctx.find_all('strong', class_='prdName')					
						for prdname_ctx in prdname_list :
							product_url_ctx = prdname_ctx.find('a')
							if(product_url_ctx != None) : 
								if('href' in product_url_ctx.attrs) :
									product_url = product_url_ctx.attrs['href']
									product_no_list = product_url.split('/')
									if(3 <= len(product_no_list) ) :
										order_status_data.cor_goods_code.append( product_no_list[3].strip() )
									
									
					ea_span_ctx = product_ctx.find('strong', class_='quantity')
					if( ea_span_ctx == None ) : ea_span_ctx = product_ctx.find('span', class_='quantity')
					if( ea_span_ctx != None ) :
						ea_span_text = ea_span_ctx.get_text().strip()
						order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
						
					status_list = product_ctx.find_all('p', class_='status')
					if(len(status_list) == 0 ) : status_list = product_ctx.find_all('div', class_='prdFoot')
					for status_ctx in status_list :
						if('title' in status_ctx.attrs) :
							if( status_ctx.attrs['title'] == '주문처리상태' ) :
								status_text = status_ctx.get_text().strip()
								#__LOG__.Trace(status_text)
								split_list = status_text.split('\n')
								sub_split_list = split_list[0].strip().split(' ')
								order_status_data.cor_memo = sub_split_list[0].strip()
		

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_second')
		__LOG__.Error( ex )
		pass


		
def get_order_status_data_third( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		div_list = soup.find_all('div', class_='orderList')

		for div_ctx in div_list :
			li_list = div_ctx.find_all('div', class_='order xans-record-')
			for li_ctx in li_list :
				if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
				######################
				# 주문번호
				#
				# <span class="orderNum">2020.06.29<br>20200629-RA22K</span>
				######################
				cor_order_no_ctx = li_ctx.find('span', class_='number')
				if( cor_order_no_ctx != None ) :
					text = cor_order_no_ctx.get_text().strip()
					cor_order_no = get_cor_order_no(text)
					#order_status_data.cos_order_no = get_cor_order_no(text)		# 테스트용
				
				#if( True ) :	# 테스트용
				if( cor_order_no == order_status_data.cos_order_no ) :	
					######################
					# 물품리스트
					#
					# <div class="description">
					# <p class="prdImg"><a href="/product/detail.html?product_no=197&amp;cate_no=54"><img src="http://img.echosting.cafe24.com/thumb/img_product_small.gif" onerror="this.src='http://img.echosting.cafe24.com/thumb/img_product_small.gif';" width="73" height="73" alt=""></a></p>
					# <strong class="prdName" title="상품명"><a href="/product/detail.html?product_no=197&amp;cate_no=54">Crochet Crop dress - Pink</a></strong>
					# <ul class="info">
					# <li>
					# <span class="price" title="판매가"><strong>78,000</strong>원<span class="displaynone"> </span></span>
					# <span class="quantity" title="수량"><strong>1</strong>개</span>
					# </li>
					# <li class="displaynone">무이자할부 상품</li>
					# </ul>
					# </div>
					######################
					
					product_list = li_ctx.find_all('strong', class_='prdName')
					if(len(product_list) == 0 ) : product_list = li_ctx.find_all('p', class_='prdName')
					
					for product_ctx in product_list :						
						product_url_list = product_ctx.find_all('a')
						for product_url_ctx in product_url_list :
							
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								if( 0 < product_url.find('product_no=') ) :
									product_no_list = product_url.split('product_no=')
									if(len(product_no_list) == 2 ) :
										sub_product_no_list = product_no_list[1].split('&')
										order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )
								else :
									product_no_list = product_url.split('/')
									order_status_data.cor_goods_code.append( product_no_list[3].strip() )
						
					ea_span_list = li_ctx.find_all('span', class_='quantity')
					for ea_span_ctx in ea_span_list :
						ea_span_text = ea_span_ctx.get_text().strip()
						order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
							
					status_div_ctx = li_ctx.find('p', class_='status')
					if( status_div_ctx != None) : 
						if(order_status_data.cor_memo == '') : 
							split_list = status_div_ctx.get_text().strip().split('\n')
							order_status_data.cor_memo = split_list[0].strip()
					
					

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_third')
		__LOG__.Error( ex )
		pass

		
		
		
def get_order_status_data_vemvem( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		div_list = soup.find_all('li', class_='list-item xans-record-')

		for div_ctx in div_list :
			#if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <tr>
			# <th scope="row">주문번호</th>
			# <td>20200629-0000058</td>
			# </tr>
			######################
			cor_order_no_list = div_ctx.find_all('div', class_='col col70 floatleft')
			for cor_order_no_ctx in cor_order_no_list :
				text = cor_order_no_ctx.get_text().strip()
				if(text != '주문번호') : 
					cor_order_no = get_cor_order_no(text)
					#order_status_data.cos_order_no = get_cor_order_no(text)		# 테스트용

			
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				######################
				# 물품리스트
				#
				# <li class="list-item xans-record-">
				# <div class="col col40 floatleft list-col">
				# <div class="col col30 floatleft">2020-08-05</div>
				# <div class="col col70 floatleft">
				# <a href="detail.html?order_id=20200805-0000024&amp;page=1&amp;history_start_date=2020-05-07&amp;history_end_date=2020-08-05">20200805-0000024</a>
				# <p>Layer: Freezing Cut - Shark Silver</p>
				# </div>
				# </div>
				# <div class="col col60 floatleft list-col">
				# <div class="col col25 floatleft alignright">1</div>
				# <div class="col col25 floatleft alignright">KRW 34,000</div>
				# <div class="col col25 floatleft alignright">입금전</div>
				# <div class="col col25 floatleft alignright">
				# <p class="displaynone"><a href="#none" class="line" onclick="OrderHistory.getDetailInfo('?product_no=83&amp;cate_no=42&amp;order_id=20200805-0000024&amp;ord_item_code=20200805-0000024-01');">[상세정보]</a></p>
				# <p class="">-</p>
				# </div>
				# </div>
				# </li>
				######################
				
				product_list = div_ctx.find_all('div', class_='col col60 floatleft list-col')
				
				for product_ctx in product_list :
					prdname_list = product_ctx.find_all('div')		
					idx = 0
					for prdname_ctx in prdname_list :
						idx += 1
						if(idx == 1) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( prdname_ctx.get_text().strip() )) )
						elif(idx == 3) :
							split_list = prdname_ctx.get_text().strip().split('\n')
							if( order_status_data.cor_memo == '') : order_status_data.cor_memo = split_list[0].strip()
						elif(idx == 4) :
							product_url_ctx = prdname_ctx.find('a')
							if(product_url_ctx != None) : 
								if('onclick' in product_url_ctx.attrs) :
									product_url = product_url_ctx.attrs['onclick']
									product_no_list = product_url.split('product_no=')
									if(len(product_no_list) == 2 ) :
										sub_product_no_list = product_no_list[1].split('&')
										order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_vemvem')
		__LOG__.Error( ex )
		pass		
		
		
		
def get_order_status_data_studioalive( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		div_list = soup.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetail cart-wrap xans-record-')

		
		for div_ctx in div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <tr>
			# <th scope="row">주문번호</th>
			# <td>20200629-0000058</td>
			# </tr>
			######################
			board_div_ctx = div_ctx.find('div', class_='board')
			if( board_div_ctx != None) :
				cor_order_no_list = board_div_ctx.find_all('li', class_='subject')
				for cor_order_no_ctx in cor_order_no_list :
					text = cor_order_no_ctx.get_text().strip()
					if(text != '주문번호') : 
						cor_order_no = get_cor_order_no(text)
						#order_status_data.cos_order_no = get_cor_order_no(text)		# 테스트용

			
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :	
				######################
				# 물품리스트
				#
				# <div class="xans-element- xans-myshop xans-myshop-orderhistorydetailbasic"><ul class="xans-record-">
				# <li class="thumb"><a href="/product/detail.html?product_no=67&amp;cate_no=52"><img src="http://img.echosting.cafe24.com/thumb/img_product_small.gif" alt="달걀판 먹이퍼즐식기 S" onerror="this.src='http://img.echosting.cafe24.com/thumb/img_product_small.gif';"></a></li>
				# <li class="subject product">
				# <a href="/product/detail.html?product_no=67&amp;cate_no=52"><strong>달걀판 먹이퍼즐식기 S</strong></a>
				# <div class="option">프레임 사이즈=먹이퍼즐식기_S10, 색상=화이트  <span class="displaynone">(+0원)</span>
				# </div>
				# <br><a href="/board/product/write.html?board_no=4&amp;product_no=67&amp;order_id=20200805-0000013"><span class="btn3">REVIEW</span></a>
				# </li>
				# <li class="quantity">1</li>
				# <li class="price"><strong>57,000</strong></li>
				# <li class="state">
				# <p>입금전</p>
				# <p></p>
				# <p><a href="#none" onclick="" class="displaynone"><img src="http://img.echosting.cafe24.com/skin/base_ko_KR/myshop/btn_order_delivery.gif" alt="배송추적"></a></p>
				# </li>
				# </ul>
				# </div>
				######################
				
				product_list = div_ctx.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetailbasic')
				
				for product_ctx in product_list :

					cor_memo_ctx = product_ctx.find('li', class_='state')
					if(cor_memo_ctx != None) : 
						split_list = cor_memo_ctx.get_text().strip().split('\n')
						if( order_status_data.cor_memo == '') : order_status_data.cor_memo = split_list[0].strip()
						
					
					prdname_list = product_ctx.find_all('li', class_='subject product')		

					for prdname_ctx in prdname_list :
						product_url_ctx = prdname_ctx.find('a')
						if(product_url_ctx != None) : 
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								product_no_list = product_url.split('product_no=')
								if(len(product_no_list) == 2 ) :
									sub_product_no_list = product_no_list[1].split('&')
									order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )
									
									
					ea_span_list = product_ctx.find_all('li', class_='quantity')
					for ea_span_ctx in ea_span_list :
						ea_span_text = ea_span_ctx.get_text().strip()
						order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
						

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_studioalive')
		__LOG__.Error( ex )
		pass		
		
		
def get_order_status_data_babiana( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		div_list = soup.find_all('div', class_='xans-element- xans-myshop xans-myshop-orderhistorydetail mResult xans-record-')

		for div_ctx in div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			# <tr>
			# <th scope="row">주문번호</th>
			# <td>20200804-0000050</td>
			# </tr>
			######################
			cor_order_no_list = div_ctx.find_all('table')
			for cor_order_no_ctx in cor_order_no_list :
				tr_list = cor_order_no_ctx.find_all('tr')
				for tr_ctx in tr_list :
					th_ctx = tr_ctx.find('th')
					td_ctx = tr_ctx.find('td')
					if(th_ctx != None ) and (td_ctx != None) :
						th_text = th_ctx.get_text().strip()
						td_text = td_ctx.get_text().strip()
						if(th_text == '주문/배송상태') :
							order_status_data.cor_memo = td_text
						if(th_text == '주문번호') :
							cor_order_no = td_text
							#order_status_data.cos_order_no = td_text		# 테스트용

			#if( True ) :	# 테스트용	
			if( cor_order_no == order_status_data.cos_order_no ) :	
			
				table_ctx = div_ctx.find('table', id='order_cart_table')
				'''
				if( table_ctx != None) :
					######################
					# 물품리스트
					#
					# <tr class="xans-record-">
					# <td class="thumb"><a href="/product/detail.html?product_no=1154&amp;cate_no=44"><img src="//m.hutsandbay.com/web/product/tiny/20200518/8fb8f618867836da0c61df7ed04c2c66.jpg" alt="HB Cooling Vest Lemon"></a></td>
					# <td class="item">
					# <a href="/product/detail.html">HB Cooling Vest Lemon</a><br>[옵션: L]<br><a href="http://review5.cre.ma/hutsandbay.com/mobile/reviews/new?product_code=1154&amp;review_source=15&amp;close_url=http%3A%2F%2Fm.hutsandbay.com%2Fmyshop%2Forder%2Fdetail.html%3Forder_id%3D20200626-0000072%26page%3D1&amp;app=0&amp;device=mobile&amp;secure_username=V271172322df31144f483e1afbbbc01eba&amp;secure_user_name=V267587aa4446ea9f50736c428a939e895&amp;widget_env=100" class="crema-new-review-link crema-applied" data-cafe24-product-link="?board_no=4&amp;product_no=1154&amp;order_id=20200626-0000072" data-review-source="mobile_my_orders">구매후기</a>
					# </td>
					# <td>34,000</td>
					# <td>340</td>
					# <td>1</td>
					# <td class="state">입금전</td>
					# <td><a href="#none" onclick="" class="displaynone"><img src="http://img.echosting.cafe24.com/design/skin/default/myshop/btn_delivery.gif" alt="배송추적"></a></td>
					# </tr>
					######################
					
					product_list = table_ctx.find_all('tr', class_='xans-record-')
					
					for product_ctx in product_list :						
						prdname_list = product_ctx.find_all('td')
						td_idx = -1
						for prdname_ctx in prdname_list :
							td_idx += 1
							if(td_idx == 4 ) : 
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( prdname_ctx.get_text().strip() )) )
							elif(td_idx == 5 ) : 
								order_status_data.cor_memo = prdname_ctx.get_text().strip()
							elif(td_idx == 0 ) : 
								product_url_list = prdname_ctx.find_all('a')
								for product_url_ctx in product_url_list :
									if('href' in product_url_ctx.attrs) :
										product_url = product_url_ctx.attrs['href']
										product_no_list = product_url.split('product_no=')
										if(len(product_no_list) == 2 ) :
											sub_product_no_list = product_no_list[1].split('&')
											order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )
				'''
				
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_babiana')
		__LOG__.Error( ex )
		pass
		
		
		


		
def get_order_status_data_yolohollo( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		div_list = soup.find_all('div', class_='orderList')

		for div_ctx in div_list :
			li_list = div_ctx.find_all('li')
			for li_ctx in li_list :
				if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
				######################
				# 주문번호
				#
				# <span class="orderNum">2020.06.29<br>20200629-RA22K</span>
				######################
				cor_order_no_ctx = li_ctx.find('span', class_='orderNum')
				if( cor_order_no_ctx != None ) :
					text = cor_order_no_ctx.get_text().strip()
					cor_order_no = text[10:]
					#order_status_data.cos_order_no = text[10:]		# 테스트용
				
				#if( True ) :	# 테스트용
				if( cor_order_no == order_status_data.cos_order_no ) :	
					######################
					# 물품리스트
					#
					# <div class="orderItem">
					# <div class="itemWrap">
					# <div class="info1">
					# <div class="imgW">
					# <a href="/m/view/product/IPLOI47EB" class="itemImg" title="오리안심&amp;채소 오리지널 50g">
					# <img src="http://www.dhuman.co.kr/static-root/prdct/2020/03/25/f05314d0ee544372a5c11e30eac27c43.jpg" alt="오리안심&amp;채소 오리지널 50g" class="" loading="lazy">
					# </a>
					# </div>
					# <div class="infoW">
					# <a href="/m/view/product/IPLOI47EB" class="tit" title="오리안심&amp;채소 오리지널 50g">오리안심&amp;채소 오리지널 50g</a>
					# <div class="priceW">
					# <div><span class="price">
					# <strong>4,000</strong>원
					# </span></div>
					# </div>
					# </div>
					# </div><!-- //info1 -->
					# <div class="selectedItem">
					# <ul>
					# <li>
					# <div class="itemInfoWrap">
					# <div class="itemName">
					# <p>[듀먼] 오리안심&amp;채소 오리지널 50g 1팩</p>
					# </div>
					# <div class="itemQuantity">2개</div>
					# <div class="itemPrice">
					# <span class="price">
					# </span>
					# </div>
					# </div>
					# </li>
					# </ul>
					# </div>
					# </div>
					# </div>
					######################
					
					product_list = li_ctx.find_all('div', class_='orderItem')
					
					for product_ctx in product_list :						
						prdname_list = product_ctx.find_all('div', class_='imgW')							
						for prdname_ctx in prdname_list :
							product_url_list = prdname_ctx.find_all('a')
							for product_url_ctx in product_url_list :
								if('href' in product_url_ctx.attrs) :
									product_url = product_url_ctx.attrs['href']
									product_no_list = product_url.split('/')
									order_status_data.cor_goods_code.append( product_no_list[4].strip() )
						
						ea_span_ctx = product_ctx.find('div', class_='itemQuantity')
						if( ea_span_ctx != None ) :
							ea_span_text = ea_span_ctx.get_text().strip()
							order_status_data.cod_count.append( int( __UTIL__.get_only_digit( get_cod_count(ea_span_text) )) )
							
					status_div_ctx = li_ctx.find('div', class_='orderSum')
					if( status_div_ctx != None) :
						status_ctx = status_div_ctx.find('p', class_='tit')
						if( status_ctx != None) : order_status_data.cor_memo = status_ctx.get_text().strip()

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_yolohollo')
		__LOG__.Error( ex )
		pass

		
	
def get_order_status_data_hutsandbay( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		div_list = soup.find_all('div', id='order_wrap')

		for div_ctx in div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <span class="orderNum">2020.06.29<br>20200629-RA22K</span>
			######################
			cor_order_no_ctx = div_ctx.find('table', id='order_orderer_table')
			if( cor_order_no_ctx != None ) :
				td_ctx = cor_order_no_ctx.find('td')
				if( td_ctx != None ) :
					cor_order_no = td_ctx.get_text().strip()
					#order_status_data.cos_order_no = td_ctx.get_text().strip()		# 테스트용
					
			#if( True ) :	# 테스트용	
			if( cor_order_no == order_status_data.cos_order_no ) :	
			
				table_ctx = div_ctx.find('table', id='order_cart_table')
				if( table_ctx != None) :
					######################
					# 물품리스트
					#
					# <tr class="xans-record-">
					# <td class="thumb"><a href="/product/detail.html?product_no=1154&amp;cate_no=44"><img src="//m.hutsandbay.com/web/product/tiny/20200518/8fb8f618867836da0c61df7ed04c2c66.jpg" alt="HB Cooling Vest Lemon"></a></td>
					# <td class="item">
					# <a href="/product/detail.html">HB Cooling Vest Lemon</a><br>[옵션: L]<br><a href="http://review5.cre.ma/hutsandbay.com/mobile/reviews/new?product_code=1154&amp;review_source=15&amp;close_url=http%3A%2F%2Fm.hutsandbay.com%2Fmyshop%2Forder%2Fdetail.html%3Forder_id%3D20200626-0000072%26page%3D1&amp;app=0&amp;device=mobile&amp;secure_username=V271172322df31144f483e1afbbbc01eba&amp;secure_user_name=V267587aa4446ea9f50736c428a939e895&amp;widget_env=100" class="crema-new-review-link crema-applied" data-cafe24-product-link="?board_no=4&amp;product_no=1154&amp;order_id=20200626-0000072" data-review-source="mobile_my_orders">구매후기</a>
					# </td>
					# <td>34,000</td>
					# <td>340</td>
					# <td>1</td>
					# <td class="state">입금전</td>
					# <td><a href="#none" onclick="" class="displaynone"><img src="http://img.echosting.cafe24.com/design/skin/default/myshop/btn_delivery.gif" alt="배송추적"></a></td>
					# </tr>
					######################
					
					product_list = table_ctx.find_all('tr', class_='xans-record-')
					
					for product_ctx in product_list :						
						prdname_list = product_ctx.find_all('td')
						td_idx = -1
						for prdname_ctx in prdname_list :
							td_idx += 1
							if(td_idx == 4 ) : 
								order_status_data.cod_count.append( int( __UTIL__.get_only_digit( prdname_ctx.get_text().strip() )) )
							elif(td_idx == 5 ) : 
								order_status_data.cor_memo = prdname_ctx.get_text().strip()
							elif(td_idx == 0 ) : 
								product_url_list = prdname_ctx.find_all('a')
								for product_url_ctx in product_url_list :
									if('href' in product_url_ctx.attrs) :
										product_url = product_url_ctx.attrs['href']
										product_no_list = product_url.split('product_no=')
										if(len(product_no_list) == 2 ) :
											sub_product_no_list = product_no_list[1].split('&')
											order_status_data.cor_goods_code.append( sub_product_no_list[0].strip() )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_hutsandbay')
		__LOG__.Error( ex )
		pass

####################################################################################################
#
#
####################################################################################################


def get_cor_order_no(text) :
	#
	# 문장에서 주문번호 추출 함수
	# - 아래의 형태 8자리-7자리 숫자
	# 20200626-0000097
	# 20200626-0000066
	#
	cor_order_no = ''
	if(text != None) : 
		cor_order_no_re_list = re.compile('\d{8}-\d{7}').finditer( text )
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

	

	