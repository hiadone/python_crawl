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


####################################################################################################
# 대상 사이트
# 
####################################################################################################
def get_order_data( order_data, html ) :
	if(order_data.search_web_str == 'montraum.com' ) : get_order_data_montraum( order_data, html )
	elif(order_data.search_web_str == 'petsandme.co.kr' ) : get_order_data_petsandme( order_data, html )
	elif(order_data.search_web_str == 'gubas.co.kr' ) : get_order_data_gubas( order_data, html )
	elif(order_data.search_web_str == 'dog114.kr' ) : get_order_data_dog114( order_data, html )
	elif(order_data.search_web_str == 'i-avec.com' ) : get_order_data_i_avec( order_data, html )
	elif(order_data.search_web_str == 'wconcept.co.kr' ) : get_order_data_wconcept( order_data, html )
	elif(order_data.search_web_str == 'dhuman.co.kr' ) : get_order_data_dhuman( order_data, html )
	elif(order_data.search_web_str == 'bodeum.co.kr' ) : get_order_data_bodeum( order_data, html )
	elif(order_data.search_web_str == 'purplestore.co.kr' ) : get_order_data_purplestore( order_data, html )
	elif(order_data.search_web_str == 'queenpuppy.co.kr' ) : get_order_data_queenpuppy( order_data, html )


####################################################################################################
# 대상 사이트
# 
####################################################################################################
def get_order_status_data( order_status_data, html ) :
	if(order_status_data.search_web_str == 'montraum.com' ) : get_order_status_data_montraum( order_status_data, html )
	elif(order_status_data.search_web_str == 'petsandme.co.kr' ) : get_order_status_data_petsandme( order_status_data, html )
	elif(order_status_data.search_web_str == 'gubas.co.kr' ) : get_order_status_data_gubas( order_status_data, html )
	elif(order_status_data.search_web_str == 'dog114.kr' ) : get_order_status_data_dog114( order_status_data, html )
	elif(order_status_data.search_web_str == 'i-avec.com' ) : get_order_status_data_i_avec( order_status_data, html )
	elif(order_status_data.search_web_str == 'wconcept.co.kr' ) : get_order_status_data_wconcept( order_status_data, html )
	elif(order_status_data.search_web_str == 'dhuman.co.kr' ) : get_order_status_data_dhuman( order_status_data, html )
	elif(order_status_data.search_web_str == 'bodeum.co.kr' ) : get_order_status_data_bodeum( order_status_data, html )
	elif(order_status_data.search_web_str == 'purplestore.co.kr' ) : get_order_status_data_purplestore( order_status_data, html )
	elif(order_status_data.search_web_str == 'queenpuppy.co.kr' ) : get_order_status_data_queenpuppy( order_status_data, html )

	
		
####################################################################################################
# 대상 사이트
# http://www.montraum.com
####################################################################################################
def get_order_data_montraum( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		# <div class="order-no-wrapper">
		# 주문번호 <span class="order-no">5276160-423673</span>
		# </div>
		#
		######################
		cor_order_no_ctx_div = soup.find('div', class_='order-no-wrapper')
		if(cor_order_no_ctx_div != None) :
			cor_order_no_ctx = cor_order_no_ctx_div.find('span', class_='order-no')
			order_data.cor_order_no = cor_order_no_ctx.get_text().strip()
			
		######################
		# 결재금액 - javascript 에서 값을 추출
		#
		# <script type="text/javascript">
		# fbq('track', 'Purchase', { 
		# content_type: 'product',
		# content_ids: ['1338''1408'],
		# value: 61600,
		# currency: 'KRW'
		# });
		# </script>
		######################

		split_list = html.split('<script type="text/javascript">')
		for split_ctx in split_list :
			strip_idx = split_ctx.find('</script>')
			javascript_str = split_ctx[:strip_idx].strip()
			#
			# 결제금액
			if( 0 <= javascript_str.find('fbq(') ) and ( 0 <= javascript_str.find('value') ) :
				sub_value_list = javascript_str.split(',')
				for sub_value_ctx in sub_value_list :
					real_value_list = sub_value_ctx.split(':')
					if(len(real_value_list) == 2 ) :
						title_str = real_value_list[0].strip()
						value_str = real_value_list[1].replace("'","").strip()
						if(title_str == 'value') : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )
						
						
		######################
		# 물품리스트 - javascript 에서 값을 추출
		#
		# <script language="javascript">
		# var AM_Cart=(function(){
		# var c={pd:'1338',pn:'도그 퓨어 야미 스파이스',am:'29800',qy:'2',ct:view_name("view_brand","82")};
		# var u=(!AM_Cart)?[]:AM_Cart; u[c.pd]=c;return u;
		# })();
		# </script>

		# <script language="javascript">
		# var AM_Cart=(function(){
		# var c={pd:'1408',pn:'★첫 구매 특가★ 트레이닝패드 L 60매 (30매 x 2개)',am:'31800',qy:'2',ct:view_name("view_brand","20")};
		# var u=(!AM_Cart)?[]:AM_Cart; u[c.pd]=c;return u;
		# })();
		# </script>
		######################
		
		product_idx = 0
		cor_content = ''
			
		split_list = html.split('<script language="javascript">')
		for split_ctx in split_list :
			strip_idx = split_ctx.find('</script>')
			javascript_str = split_ctx[:strip_idx].strip()
			#
			# 물품리스트
			sub_javascript_list = javascript_str.split(';')
			for sub_javascript_ctx in sub_javascript_list :
				if( 0 <= sub_javascript_ctx.find('var c={') ) :
					value_str_list = sub_javascript_ctx.split('var c={')
					sub_value_list = value_str_list[1].split(',')
					for sub_value_ctx in sub_value_list :
						real_value_list = sub_value_ctx.split(':')
						if(len(real_value_list) == 2 ) :
							title_str = real_value_list[0].strip()
							value_str = real_value_list[1].replace("'","").strip()
							if(title_str == 'pd') : order_data.cor_goods_code.append( value_str )
							elif(title_str == 'qy') : order_data.cod_count.append( int( __UTIL__.get_only_digit( value_str ) ) )
							elif(title_str == 'pn') :
								product_idx += 1
								if( product_idx == 1 ) : 
									cor_content = value_str 	# 상품명
									order_data.cor_content = cor_content
								else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
	

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_montraum')
		__LOG__.Error( ex )
		pass




def get_order_status_data_montraum( order_status_data, html ) :
	try :
		
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')		
		
		order_div_list = soup.find_all('div', class_="contents-wrapper item-list" )
		
		for order_div_ctx in order_div_list :
			if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
			######################
			# 주문번호
			#
			# <span class="orderNum">2020.06.29<br>20200629-RA22K</span>
			######################
			cor_order_no_ctx = order_div_ctx.find('span', class_='order-no')
			if( cor_order_no_ctx != None ) :
				text = cor_order_no_ctx.get_text().strip()
				cor_order_no = text
				#order_status_data.cos_order_no = text		# 테스트용
				
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :		
				table_ctx = order_div_ctx.find('table', class_='item-table')
				if(table_ctx != None) :
					######################
					# 물품리스트
					#
					# <td class="item-info">
					# <img height="80" src="/_vir0001/product_img/middle/P960_20190910PM24133_1.jpg" width="80"/>
					# <script language="javascript">
					# product.id = '730111'
					# product.name = '★첫 구매 특가★ 트레이닝패드 L 60매 (30매 x 2개)'
					# product.item_price = '15,900'
					# product.quantity = '2'
					# products.push(product);
					# product = new Object();
					# </script>
					# <div class="item-text">
					# <p class="item-name">★첫 구매 특가★ 트레이닝패드 L 60매 (30매 x 2개)</p>
					# <div id="addProduct_div730111" name="addProduct_div730111"><span style="text-decoration:line-through">트레이닝 패드 : 트레이닝 패드 L (30매) 무향</span><br/><span style="text-decoration:line-through">트레이닝 패드 : 트레이닝 패드 L (30매) 무향</span><br/></div>
					# <p class="mobile-text">
					# <span>2개</span>
					# <span>15,900원</span>
					# </p>
					# </div>
					# </td>
					######################
					
					td_list = table_ctx.find_all('td', class_='item-info')
					for td_ctx in td_list :
						script_str = td_ctx.get_text().strip()
						split_list = script_str.split('product.')
						for split_data in split_list :
							sub_split_list = split_data.split('=')
							value_str = ''
							if( 1 < len(sub_split_list) ) : value_str = sub_split_list[1].replace("'","").strip()
							
							if( split_data.startswith('id') ) : order_status_data.cor_goods_code.append( value_str )
							elif( split_data.startswith('quantity') ) : 
								sub_split_list = split_data.split('products.')
								order_status_data.cod_count.append( int(__UTIL__.get_only_digit(sub_split_list[0])) )
				
				##########################################################
				#
				# <table class="item-table type1 pay-info">
				# <tbody>.. 생걀
				# <tr>
				# <th>결제결과</th>
				# <td><script language="javascript">view_name("payresult_arr","9","write")</script>결제완료</td>
				# <th>배송여부</th>
				# <td>
				# <script language="javascript">view_name("delivery","6","write")</script>발송완료
				# <script language="javascript">
				# document.write("<br/>" +getInvoiceUrl('356329762305', 'name', ''));
				# linkUrl = getInvoiceUrl("356329762305","url","3");
				# if(linkUrl != ""){
				# document.write("<a href='"+ linkUrl +"356329762305' target='_blank'>356329762305</a>");
				# }else{
				# document.write("356329762305")
				# }
				# </script><br>CJ대한통운 <a href="https://www.doortodoor.co.kr/parcel/doortodoor.do?fsp_action=PARC_ACT_002&amp;fsp_cmd=retrieveInvNoACT&amp;invc_no=356329762305" target="_blank">356329762305</a>							
				# </td>
				# </tr>
				# </tbody></table>
				############################################################

				pay_table_ctx = soup.find('table', class_="item-table type1 pay-info")
				if( pay_table_ctx != None ) : 
					tr_list = pay_table_ctx.find_all('tr')
					for tr_ctx in tr_list :
						th_ctx_list = tr_ctx.find_all('th')
						td_ctx_list = tr_ctx.find_all('td')
						td_idx = -1
						for th_ctx in th_ctx_list :
							td_idx += 1
							title_str = th_ctx.get_text().strip()
							if(title_str == '결제결과') or (title_str == '배송여부') : 
								delivery_str = td_ctx_list[td_idx].get_text().strip()
								if( delivery_str != '' ) :
									split_list = delivery_str.split('\n')
									sub_split_list = split_list[0].split(')')
									idx = len(sub_split_list) - 1
									order_status_data.cor_memo = sub_split_list[idx].strip()

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_montraum')
		__LOG__.Error( ex )
		pass



####################################################################################################
# 대상 사이트
# http://www.petsandme.co.kr
#
# 물품리스트 데이터 없음
####################################################################################################
	
	
def get_order_data_petsandme( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		# <span class="p">2006261356-216</span>
		#
		######################
		cor_order_no_ctx_div = soup.find('div', class_='done_box')
		if(cor_order_no_ctx_div != None) :
			cor_order_no_ctx_p = cor_order_no_ctx_div.find('p', class_='in')
			if(cor_order_no_ctx_p != None) :
				cor_order_no_ctx = cor_order_no_ctx_p.find('span', class_='p')
				if(cor_order_no_ctx != None) : order_data.cor_order_no = cor_order_no_ctx.get_text().strip()
			
			######################
			# 결재금액 - javascript 에서 값을 추출
			#
			# <div class="done_box">            
			# 펫츠앤미 제품을 주문해 주셔서 감사합니다.
			# 금액: 47,200원
			# 입금 계좌: 국민은행 750602-01-160356 (이다솜)
			# 24시간 이내에 미입금 시 주문이 자동 취소됩니다.<div class="done_inner page_mg">
			# ... 생략
			######################
			
			split_list = cor_order_no_ctx_div.get_text().strip().split('\n')
			for text in split_list :
				if( 0 <= text.find('금액:') ) and ( 0 <= text.find('원') ) : 
					total_price_sum_str = __UTIL__.get_total_price_sum( text)
					order_data.total_price_sum = int( __UTIL__.get_only_digit( total_price_sum_str ) )
	
	

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_petsandme')
		__LOG__.Error( ex )
		pass




def get_order_status_data_petsandme( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')		
		
		table_ctx = soup.find('table', class_='shop_table order_list_st')
		if(table_ctx != None) :
			tr_list = table_ctx.find_all('tr')
			for tr_ctx in tr_list :
				td_list = tr_ctx.find_all('td')
				if(len(td_list) != 0 ) :
					######################
					# 주문번호
					# <tr>
					# <td class="w_no orderlist_st">1</td>
					# <td class="w_ordernum"><a href="../mypage/orderlist_view.php?order_num=2006261356-216"><strong>2006261356-216</strong><input style="cursor:pointer;" type="button" onfocus="blur();" value="주문상세조회" class="btn_os os5 order_inp_st"></a></td>
					# <td class="w_prod">체리퐁당 크롭티 -1</td>
					# <td class="w_price">47,200 원</td>
					# <td class="w_state">
					# <p class="os_wrap"><input type="button" onfocus="blur();" value="주문취소" class="btn_os os7 order_inp_st"></p>
					# </td>
					# </tr>
					# 
					######################
					cor_order_no_ctx = tr_ctx.find('td', class_="w_ordernum")
					if( cor_order_no_ctx != None ) :
						strong_ctx = cor_order_no_ctx.find('strong')
						if(strong_ctx != None) :
							text = strong_ctx.get_text().strip()
							cor_order_no = text
							#order_status_data.cos_order_no = text		# 테스트용
						
					#if( True ) :	# 테스트용
					if( cor_order_no == order_status_data.cos_order_no ) :	
						
						##########################################################
						# 주문상태
						# <td class="w_state">
						# <p class="os_wrap"><input type="button" onfocus="blur();" value="주문취소" class="btn_os os7 order_inp_st"></p>
						# </td>
						############################################################

						cor_memo_ctx = tr_ctx.find('td', class_='w_state')
						if( cor_memo_ctx != None) : 
							os_wrap_ctx = cor_memo_ctx.find('p', class_='os_wrap')
							if( os_wrap_ctx != None) : 
								input_ctx = os_wrap_ctx.find('input')
								if( input_ctx != None) : 
									if('value' in input_ctx.attrs) :
										if(order_status_data.cor_memo == '' ) : order_status_data.cor_memo = input_ctx.attrs['value'].strip()
								
						
			
		
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_petsandme')
		__LOG__.Error( ex )
		pass	




####################################################################################################
# 대상 사이트
# http://gubas.co.kr
####################################################################################################

def get_cor_order_no_gubas(text) :
	#
	# 문장에서 주문번호 추출 함수
	# - 아래의 형태 19자리 숫자
	# 20200 62613 59131 7530
	#
	cor_order_no = ''
	if(text != None) : 
		cor_order_no_re_list = re.compile('\d{15,20}').finditer( text )
		for cor_order_no_re in cor_order_no_re_list:
			cor_order_no = cor_order_no_re.group()

	return cor_order_no


def get_product_list( html, order_data ) :
	######################
	# 물품리스트
	#
	# <script type="text/javascript">
	# var _nao={};
	# _nao["chn"] = "AD";
	# _nao["order"]=[{"oid":2020062613591317530, "poid":846, "pid":192, "parpid":192, "name":"강아지 리드줄 콤비네이션_베이지브라운", "cnt":2, "price":38000},{"oid":2020062613591317530, "poid":847, "pid":195, "parpid":195, "name":"강아지 목줄/3M리드줄세트 콤비네이션_옐로우레드", "cnt":2, "price":68000}];
	# wcs.CPAOrder(_nao);
	# </script>
	######################
	product_idx = 0
	cor_content = ''
		
	split_list = html.split('<script type="text/javascript">')
	for split_ctx in split_list :
		strip_idx = split_ctx.find('</script>')
		javascript_str = split_ctx[:strip_idx].strip()
		#
		# 물품리스트
		sub_javascript_list = javascript_str.split(';')
		for sub_javascript_ctx in sub_javascript_list :
			if( 0 <= sub_javascript_ctx.find('_nao["order"]=') ) :
				product_split_list = sub_javascript_ctx.split( '_nao["order"]=' )
				json_str = product_split_list[1].strip()
				json_data_list = json.loads( json_str )
				for json_data in json_data_list :
					for key in json_data :
						#__LOG__.Trace('%s : %s' % (key, json_data[key]) )
						if(key == 'pid') : order_data.cor_goods_code.append( str(json_data[key]) )
						elif(key == 'cnt') : order_data.cod_count.append( int( json_data[key] ) )
						elif(key == 'name') :
							product_idx += 1
							if( product_idx == 1 ) : 
								cor_content = json_data[key] 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
							

def get_order_data_gubas( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호 / 결제금액
		#
		# <td>총 결제금액</td>
		# <td class="right">
		# <span class="tahoma">106,000</span>
		# ------------------------------------------
		# <div class="complete_info_lay">
		# <dl>
		# <dt>주문번호</dt>
		# <dd>2020062613591317530 (2020-06-26 13:59)</dd>
		# </dl>
		# <dl>
		# <dt>결제금액</dt>
		# <dd>
		# <strong>106,000₩</strong>
		# &nbsp;
		# <button type="button" class="ml5 btn_open_small blue" onclick="detail_contents_toggle(this,'priceDetail')" style="height:20px;">자세히</button>
		# </dd>
		# </dl>
		######################
		cor_order_no_ctx_div_list = soup.find_all('div', class_='complete_info_lay')
		for cor_order_no_ctx_div in cor_order_no_ctx_div_list :
						
			dl_list = cor_order_no_ctx_div.find_all('dl')
			for dl_ctx in dl_list :
				title_ctx = dl_ctx.find('dt')
				value_ctx = dl_ctx.find('dd')
				if(title_ctx != None) and (value_ctx != None) : 
					title_str = title_ctx.get_text().strip()
					value_str = value_ctx.get_text().strip()
					if( title_str == '주문번호' ) : order_data.cor_order_no = get_cor_order_no_gubas( value_str )						
					elif( title_str == '결제금액' ) : 
						strong_ctx = value_ctx.find('strong')
						order_data.total_price_sum = int( __UTIL__.get_only_digit( strong_ctx.get_text().strip() ) )
			
			if( order_data.total_price_sum == 0 ) :
				span_ctx = cor_order_no_ctx_div.find('span', class_='tahoma')
				if(span_ctx != None) : order_data.total_price_sum = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
	
		######################
		# 물품리스트
		#
		# <script type="text/javascript">
		# var _nao={};
		# _nao["chn"] = "AD";
		# _nao["order"]=[{"oid":2020062613591317530, "poid":846, "pid":192, "parpid":192, "name":"강아지 리드줄 콤비네이션_베이지브라운", "cnt":2, "price":38000},{"oid":2020062613591317530, "poid":847, "pid":195, "parpid":195, "name":"강아지 목줄/3M리드줄세트 콤비네이션_옐로우레드", "cnt":2, "price":68000}];
		# wcs.CPAOrder(_nao);
		# </script>
		######################
		get_product_list( html, order_data )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_gubas')
		__LOG__.Error( ex )
		pass




def get_order_status_data_gubas( order_status_data, html ) :
	try :
	
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')		
		

		######################
		# 주문번호
		#
		# <span class="orderNum">2020.06.29<br>20200629-RA22K</span>
		######################
		cor_order_no_ctx = soup.find('span', class_="order-seq")

		if( cor_order_no_ctx != None ) :
			text = cor_order_no_ctx.get_text().replace('(','').replace(')','').strip()
			cor_order_no = text
			#order_status_data.cos_order_no = text		# 테스트용
			
		#if( True ) :	# 테스트용
		if( cor_order_no == order_status_data.cos_order_no ) :		
			ul_ctx = soup.find('ul', class_='settle_cart_list')

			if(ul_ctx != None) :
				######################
				# 물품리스트
				#
				#  <li class="item_option">
				#  <table width="100%" border="0" cellpadding="0" cellspacing="0" class="goods-info-table">
				#  <tbody><tr>
				#  <td class="left" width="90" valign="top">
				#  <a href="../goods/view?no=192"><img src="/data/goods/1/2019/06/192_tmp_371e4ca5c4ba4b273f44a2e5298a68645378thumbCart.jpg?dummy=1593570291" class="goods_thumb" align="absmiddle" width="80" onerror="this.src='/data/skin/mobile_ver3_fashion_itsimply_gls/images/common/noimage_list.gif'"></a>
				#  </td>
				#  <td valign="top" class="goods-info">
				#  <div class="goods_name">						
				#  <a href="../goods/view?no=192">강아지 리드줄 콤비네이션_베이지브라운</a>
				#  </div>
				#  <div class="pdb5">
				#  </div>
				#  <div class="pdb5 goods-option">
				#  사이즈:M
				#  </div>
				#  <div class="clearbox">
				#  <div class="sum_ea">수량 : 2개</div>
				#  <div class="sum_price bold" style="color:#0050d2;"><span class="cart_price_num">38,000₩</span></div>
				#  </div>
				#  </td>
				#   </tr>
				#  </tbody></table>
				#  </li>
				######################
				
				li_list = ul_ctx.find_all('li', class_='item_option')
				for li_ctx in li_list :
					ea_ctx = li_ctx.find('div', class_='sum_ea')
					if( ea_ctx != None) : order_status_data.cod_count.append( int(__UTIL__.get_only_digit(ea_ctx.get_text().strip() )) )
					
					goods_name_ctx = li_ctx.find('div', class_='goods_name')
					if( goods_name_ctx != None) :
						a_link_ctx = goods_name_ctx.find('a')
						if( a_link_ctx != None) :
							if('href' in a_link_ctx.attrs) :
								product_url = a_link_ctx.attrs['href']
								split_list = product_url.split('?no=')
								order_status_data.cor_goods_code.append( split_list[1].strip() )
			
				##########################################################
				#
				# <li class="item_step_cell">
				# <div class="fleft">
				# <div class="step-info">
				# 주문접수
				# </div>
				# </div>
				# <div class="fright">
				# </div>
				# </li>
				############################################################

				li_list = ul_ctx.find_all('li', class_='item_step_cell')
				for li_ctx in li_list :
					cor_memo_ctx = li_ctx.find('div', class_='step-info')
					if( cor_memo_ctx != None) : 
						if(order_status_data.cor_memo == '' ) : order_status_data.cor_memo = cor_memo_ctx.get_text().strip()

			
		
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_gubas')
		__LOG__.Error( ex )
		pass
		
		


####################################################################################################
# 대상 사이트
# https://dog114.kr
####################################################################################################

def get_order_data_dog114( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호 / 결제금액
		#
		# <table width="100%" border="0" cellpadding="0" cellspacing="0">
		# <colgroup><col width="90">
		# </colgroup><tbody><tr>
		# <td>주문번호</td>
		# <td class="fx12">2020062614574817534</td>
		# </tr>
		# .. 생략 ..
		# <tr>
		# <td>결제금액</td>
		# <td class="fx12"><font color="black"><strong>14,500원</strong></font></td>
		# </tr>
		# <tr><td height="15"></td></tr>
		# 
		# </tbody></table>
		######################
		cor_order_no_ctx_div_list = soup.find_all('div', class_='pd10')
		for cor_order_no_ctx_div in cor_order_no_ctx_div_list :
						
			dl_list = cor_order_no_ctx_div.find_all('tr')
			for dl_ctx in dl_list :
				td_list = dl_ctx.find_all('td')
				if(len(td_list) == 2) :
						title_str = td_list[0].get_text().strip()
						value_str = td_list[1].get_text().strip()
						if( title_str == '주문번호' ) : order_data.cor_order_no = value_str					
						elif( title_str == '결제금액' ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )

						
		######################
		# 물품리스트
		#
		# <script type="text/javascript">
		# var _nao={};
		# _nao["chn"] = "AD";
		# _nao["order"]=[{"oid":2020062614574817534, "poid":58386, "pid":420, "parpid":420, "name":"인도산 스텐 쌍식기 [사이즈선택]", "cnt":2, "price":12000}];
		# wcs.CPAOrder(_nao);
		# </script>
		######################
		get_product_list( html, order_data )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_dog114')
		__LOG__.Error( ex )
		pass




def get_order_status_data_dog114( order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')


		######################
		# 주문번호
		#
		# <div class="order-date-info">
		# <span class="order-date">2020.06.29</span>
		# <span class="order-seq">(2020062916164317538)</span>
		# <div class="pdt5 center">
		# <span class="btn large"><button type="button" onclick="order_cancel('2020062916164317538');">주문무효</button></span>
		# </div>
		# </div>
		######################
		cor_order_no_ctx = soup.find('div', class_="order-date-info")

		if( cor_order_no_ctx != None ) :
			span_ctx = cor_order_no_ctx.find('span', class_='order-seq')
			if( span_ctx != None ) : 
				text = span_ctx.get_text().replace('(','').replace(')','').strip()
				cor_order_no = text
				#order_status_data.cos_order_no = text		# 테스트용
			
		#if( True ) :	# 테스트용
		if( cor_order_no == order_status_data.cos_order_no ) :		

			######################
			# 물품리스트
			#
			# <ul class="settle_cart_list">
			# .. 생략
			# <li class="item_option">
			# <div class="fx14 bold goods_name">
			# <a href="../goods/view?no=610">마단 핀브러쉬 [중] MPB-M11 빨강바탕 검정테두리 가장 딱딱함</a>
			# </div>
			# <table width="100%" border="0" cellpadding="0" cellspacing="0" class="goods-info-table">
			# <tbody><tr>
			# <td class="left" width="90" valign="top">
			# <a href="../goods/view?no=610"><img src="/data/goods/1/2013/10/610_tmp_9efb078ecaf4735810c28f9e109f84474196thumbCart.JPG?dummy=1593673634" align="absmiddle" width="80" height="80" onerror="this.src='/data/skin/mobile_ver3_default/images/common/noimage_list.gif'"></a>
			# </td>
			# <td valign="top" class="goods-info">
			# <div>
			# </div>
			# <div class="clearbox">
			# <div class="sum_ea">수량 : 1개</div>
			# <div class="sum_price bold" style="color:#0050d2;"><span class="cart_price_num">30,000</span>원</div>
			# </div>
			# </td>
			# </tr>
			# </tbody></table>
			# </li>
			# <li class="item_step_cell">
			# <div class="fleft">
			# <div class="step-info">
			# 배송완료
			# ( 1 / 1 )
			# </div>
			# </div>
			# <div class="fright">
			# <span class="btn small"><button type="button" onclick="goods_review_write('776', '2020062915282117536');">상품후기</button></span>
			# <span class="btn small"><button onclick="export_list('2020062915282117536', 'goods');">배송조회</button></span>
			# </div>
			# </li>
			# </div>
			# </div>
			# <div style="padding-top: 5px;"></div>
			# </ul>
			######################
			ul_ctx = soup.find('ul', class_="settle_cart_list" )
			if(ul_ctx != None) :
				cor_memo_list = ul_ctx.find_all('li', class_='item_step_cell')
				for cor_memo_ctx in cor_memo_list :
					cor_memo = cor_memo_ctx.find('div' , class_="step-info")
					if( cor_memo != None ) :
						if(order_status_data.cor_memo == '' ) : 
							cor_memo_str =  cor_memo.get_text().strip()
							split_list = cor_memo_str.split('(')
							order_status_data.cor_memo = split_list[0].strip()
				
				product_list = ul_ctx.find_all('li', class_='item_option')
				for product_ctx in product_list :
					ea_ctx = product_ctx.find('div', class_='sum_ea')
					if( ea_ctx != None) : order_status_data.cod_count.append( int(__UTIL__.get_only_digit( ea_ctx.get_text().strip() )) )
					
					goods_name_list = product_ctx.find_all('div')
					for goods_name_ctx in goods_name_list :
						is_good = False
						if('class' in goods_name_ctx.attrs ) :
							class_name_list = goods_name_ctx.attrs['class']
							for class_name in class_name_list :
								if(class_name == 'goods_name') : is_good = True
						if(is_good) :		
							a_link_ctx = goods_name_ctx.find('a')
							if( a_link_ctx != None) :
								if('href' in a_link_ctx.attrs) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('?no=')
									order_status_data.cor_goods_code.append( split_list[1].strip() )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_dog114')
		__LOG__.Error( ex )
		pass
		
		

####################################################################################################
# 대상 사이트
# http://shop.i-avec.com
####################################################################################################

def get_order_data_i_avec( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		# <div id="sod_fin_no">주문번호 <strong>2020062615093097</strong></div>
		######################
		cor_order_no_ctx_div_list = soup.find_all('div', id='sod_fin_no')
		for cor_order_no_ctx_div in cor_order_no_ctx_div_list :
			title_str = cor_order_no_ctx_div.get_text().strip()	
			strong_ctx = cor_order_no_ctx_div.find('strong')
			if(strong_ctx != None) :
				value_str = strong_ctx.get_text().strip()
				if( 0 <= title_str.find('주문번호' )) : order_data.cor_order_no = value_str

	
		######################
		# 물품리스트 / 결제금액
		#
		# <section class="sod_fin_list">
		# <h2>주문하신 상품</h2>
		# 
		# <ul id="sod_list_inq" class="sod_list">
		# <li class="sod_li">
		# <div class="li_name">
		# <a href="./item.php?it_id=1571120298"><strong>닭가슴살 브로콜리 [70g]</strong></a>
		# </div>
		# <div class="li_op_wr">
		# <div class="li_opt">닭가슴살 브로콜리 [70g]</div>
		# <a href="./item.php?it_id=1571120298" class="total_img"><img src="http://shop.i-avec.com/data/item/1571120298/thumb-64ut6rCA7Iq07IK067iM66Gc7L2c66as70g_m_80x80.png" width="80" height="80" alt="닭가슴살 브로콜리 [70g]"></a>
		# <span class="prqty_stat"><span class="sound_only">상태</span>주문</span>
		# </div>
		# <div class="li_prqty">
		# <span class="prqty_price li_prqty_sp"><span>판매가 </span>3,500</span>
		# <span class="prqty_qty li_prqty_sp"><span>수량 </span>2</span>
		# <span class="prqty_sc li_prqty_sp"><span>배송비 </span>선불</span>
		# <span class="total_point li_prqty_sp"><span>적립포인트 </span>0</span>
		# </div>
		# <div class="li_total">
		# <span class="total_price total_span"><span>주문금액 </span>7,000</span>
		# </div>
		# </li>
		# </ul>
		# <div class="sod_ta_wr">
		# <dl id="m_sod_bsk_tot">
		# <dt class="sod_bsk_dvr">주문총액</dt>
		# <dd class="sod_bsk_dvr"><strong>7,000 원</strong></dd>
		# <dt class="sod_bsk_dvr">배송비</dt>
		# <dd class="sod_bsk_dvr"><strong>2,500 원</strong></dd>
		# <dt class="sod_bsk_point">적립포인트</dt>
		# <dd class="sod_bsk_point"><strong>0 점</strong></dd>
		# <dt class="sod_bsk_cnt">총계</dt>
		# <dd class="sod_bsk_cnt"><strong>9,500 원</strong></dd>
		# </dl>
		# </div>
		# </section>
		######################
		section_list = soup.find_all('section', class_='sod_fin_list')
		for section_ctx in section_list :
			dd_ctx = section_ctx.find('dd', class_='sod_bsk_cnt')
			if( dd_ctx != None ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( dd_ctx.get_text().strip() ) )
			
			ul_ctx = section_ctx.find('ul', id='sod_list_inq')
			if(ul_ctx != None) :
				product_idx = 0
				cor_content = ''
				li_list = ul_ctx.find_all('li')
				for li_ctx in li_list :
					ea_ctx = li_ctx.find('span', class_='prqty_qty li_prqty_sp')
					if( ea_ctx != None) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
						
					pname_ctx = li_ctx.find('div', class_='li_name')
					if( pname_ctx != None) :
						product_idx += 1
						# 물품 product no
						product_url_ctx = pname_ctx.find('a')
						if( product_url_ctx != None) :
							if('href' in product_url_ctx.attrs) :
								product_url = product_url_ctx.attrs['href']
								product_no_list = product_url.split('?it_id=')
								if(len(product_no_list) == 2 ) : order_data.cor_goods_code.append( product_no_list[1].strip() )
								
						# 물품명
						if( product_idx == 1 ) : 
							cor_content = pname_ctx.get_text().strip() 	# 상품명
							order_data.cor_content = cor_content
						else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
				

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_i_avec')
		__LOG__.Error( ex )
		pass




def get_order_status_data_i_avec( order_status_data, html ) :
	try :
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		######################
		# 주문번호
		#
		# <div id="sod_fin_no">주문번호 <strong>2020062615093097</strong></div>
		######################
		cor_order_no_ctx_div_list = soup.find_all('div', id='sod_fin_no')
		for cor_order_no_ctx_div in cor_order_no_ctx_div_list :
			title_str = cor_order_no_ctx_div.get_text().strip()	
			strong_ctx = cor_order_no_ctx_div.find('strong')
			if(strong_ctx != None) :
				value_str = strong_ctx.get_text().strip()
				if( 0 <= title_str.find('주문번호' )) : 
					cor_order_no = value_str
					#order_status_data.cos_order_no = value_str	# 테스트용

		#if( True ) :	# 테스트용
		if( cor_order_no == order_status_data.cos_order_no ) :	
			######################
			# 물품리스트 / 결제금액
			#
			# <section class="sod_fin_list">
			# <h2>주문하신 상품</h2>
			# 
			# <ul id="sod_list_inq" class="sod_list">
			# <li class="sod_li">
			# <div class="li_name">
			# <a href="./item.php?it_id=1571120298"><strong>닭가슴살 브로콜리 [70g]</strong></a>
			# </div>
			# <div class="li_op_wr">
			# <div class="li_opt">닭가슴살 브로콜리 [70g]</div>
			# <a href="./item.php?it_id=1571120298" class="total_img"><img src="http://shop.i-avec.com/data/item/1571120298/thumb-64ut6rCA7Iq07IK067iM66Gc7L2c66as70g_m_80x80.png" width="80" height="80" alt="닭가슴살 브로콜리 [70g]"></a>
			# <span class="prqty_stat"><span class="sound_only">상태</span>주문</span>
			# </div>
			# <div class="li_prqty">
			# <span class="prqty_price li_prqty_sp"><span>판매가 </span>3,500</span>
			# <span class="prqty_qty li_prqty_sp"><span>수량 </span>2</span>
			# <span class="prqty_sc li_prqty_sp"><span>배송비 </span>선불</span>
			# <span class="total_point li_prqty_sp"><span>적립포인트 </span>0</span>
			# </div>
			# <div class="li_total">
			# <span class="total_price total_span"><span>주문금액 </span>7,000</span>
			# </div>
			# </li>
			# </ul>
			# <div class="sod_ta_wr">
			# <dl id="m_sod_bsk_tot">
			# <dt class="sod_bsk_dvr">주문총액</dt>
			# <dd class="sod_bsk_dvr"><strong>7,000 원</strong></dd>
			# <dt class="sod_bsk_dvr">배송비</dt>
			# <dd class="sod_bsk_dvr"><strong>2,500 원</strong></dd>
			# <dt class="sod_bsk_point">적립포인트</dt>
			# <dd class="sod_bsk_point"><strong>0 점</strong></dd>
			# <dt class="sod_bsk_cnt">총계</dt>
			# <dd class="sod_bsk_cnt"><strong>9,500 원</strong></dd>
			# </dl>
			# </div>
			# </section>
			######################
			section_list = soup.find_all('section', class_='sod_fin_list')
			for section_ctx in section_list :
				
				ul_ctx = section_ctx.find('ul', id='sod_list_inq')
				if(ul_ctx != None) :
					product_idx = 0
					cor_content = ''
					li_list = ul_ctx.find_all('li')
					for li_ctx in li_list :
						cor_memo_ctx = li_ctx.find('span', class_='prqty_stat')
						if( cor_memo_ctx != None) : 
							strip_ctx = cor_memo_ctx.find('span')
							strip_str_len = 0
							if(strip_ctx != None) : strip_str_len = len(strip_ctx.get_text())
							if(order_status_data.cor_memo == '' ) : 
								cor_memo = cor_memo_ctx.get_text()
								order_status_data.cor_memo = cor_memo[strip_str_len:].strip()
							
						ea_ctx = li_ctx.find('span', class_='prqty_qty li_prqty_sp')
						if( ea_ctx != None) : order_status_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
							
						pname_ctx = li_ctx.find('div', class_='li_name')
						if( pname_ctx != None) :
							product_idx += 1
							# 물품 product no
							product_url_ctx = pname_ctx.find('a')
							if( product_url_ctx != None) :
								if('href' in product_url_ctx.attrs) :
									product_url = product_url_ctx.attrs['href']
									product_no_list = product_url.split('?it_id=')
									if(len(product_no_list) == 2 ) : order_status_data.cor_goods_code.append( product_no_list[1].strip() )
								

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_i_avec')
		__LOG__.Error( ex )
		pass
		
		
		
		
		

####################################################################################################
# 대상 사이트
# https://www.wconcept.co.kr
####################################################################################################

def get_order_data_wconcept( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호
		#
		# <div class="box order_info">
		# <h2>이현정 고객님의 주문이 완료되었습니다.</h2>
		# <p>
		# <span>2020</span>년
		# .. 생략
		# <span class="red">U01408333</span> 입니다.
		# </p>
		# 
		# </div>
		######################
		cor_order_no_ctx_div_list = soup.find_all('div', class_='box order_info')
		for cor_order_no_ctx_div in cor_order_no_ctx_div_list :
			span_ctx = cor_order_no_ctx_div.find('span', class_='red')
			if(span_ctx != None) : order_data.cor_order_no = span_ctx.get_text().strip()
			
		
		######################
		# 결제금액
		#
		# <div class="total">
		# <strong>최종 결제금액</strong>
		# <span>58,900<em>원</em></span>
		# </div>
		######################
		div_list = soup.find_all('div', class_='total')
		for div_ctx in div_list :
			title_ctx = div_ctx.find('strong')
			value_ctx = div_ctx.find('span')
			if(title_ctx != None) and (value_ctx != None) : 
				title_str = title_ctx.get_text().strip()
				if(title_str == '최종 결제금액') : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_ctx.get_text().strip() ) )

	
		######################
		# 물품리스트 / 결제금액
		#
		# <div class="box orderList">
		# <h3>주문 상품 (<span>3</span>)<button type="button" name="button" class="down_arrow"></button></h3>
		# <div class="body">
		# <div class="product">
		# <div class="img">
		# <div class="inner-wrap">
		# <img src="//image.wconcept.co.kr/productimg/image/img3/67/300907767.jpg" alt=" single type">
		# </div>
		# </div>
		# <div class="text">
		# <a href="/Product/300907767">
		# <h3>SUCK U.K</h3>
		# <p class="name">키오스 장난감 고양이집</p>
		# <p class="option">옵션 :  single type</p>
		# <p class="shipping">3,000원</p>
		# <p class="price">39,000<span>원</span> / 1<span>개</span></p>
		# </a>
		# </div>
		# </div>
		# .. 생략 ..
		# <div class="product">
		# <div class="img">
		# <div class="text">
		# <a href="/Product/300671375">
		# <h3>Arrr</h3>
		# <p class="name">아르르 맛있는 쮸르 1팩 5봉</p>
		# <p class="option">옵션 :  pink</p>
		# <p class="shipping">2,500원</p>
		# <p class="price">14,400<span>원</span> / 2<span>개</span></p>
		# </a>
		# </div>
		# </div>
		# .. 생략..
		# </div>
		# </div>
		######################
		section_list = soup.find_all('div', class_='box orderList')
		for section_ctx in section_list :
			product_idx = 0
			cor_content = ''
			product_list = section_ctx.find_all('div', class_='product')
			for product_ctx in product_list :
				text_ctx = product_ctx.find('div', class_='text')
				if( text_ctx != None ) : 
					product_url_ctx = text_ctx.find('a')
					if( product_url_ctx != None) :
						if('href' in product_url_ctx.attrs) :
							product_url = product_url_ctx.attrs['href']
							product_no_list = product_url.split('/')
							order_data.cor_goods_code.append( product_no_list[2].strip() )
					
					pname_ctx = text_ctx.find('p', class_='name')
					if( pname_ctx != None) :
						product_idx += 1
						# 물품명
						if( product_idx == 1 ) : 
							cor_content = pname_ctx.get_text().strip() 	# 상품명
							order_data.cor_content = cor_content
						else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
					
					ea_ctx = text_ctx.find('p', class_='price')
					if( ea_ctx != None) :
						value_str = ea_ctx.get_text().strip()
						split_list = value_str.split('/')
						order_data.cod_count.append( int( __UTIL__.get_only_digit( split_list[1].strip() ) ) )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_wconcept')
		__LOG__.Error( ex )
		pass




def get_order_status_data_wconcept(  order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		section_ctx = soup.find('section', id="order")
		if( section_ctx != None ) :

			######################
			# 주문번호
			#
			# <div class="order_title">
			# <div class="left">
			# 주문번호<span>U01408333</span>
			# </div>
			# <div class="right">2020-06-26</div>
			# </div>
			######################
			cor_order_no_ctx = section_ctx.find('div', class_="order_title")

			if( cor_order_no_ctx != None ) :
				span_ctx = cor_order_no_ctx.find('span')
				if( span_ctx != None ) : 
					text = span_ctx.get_text().strip()
					cor_order_no = text
					#order_status_data.cos_order_no = text		# 테스트용
				
			#if( True ) :	# 테스트용
			if( cor_order_no == order_status_data.cos_order_no ) :		

				######################
				# 물품리스트
				#
				#  <div class="product">
				# <div class="img"><a href="/Product/300907767"><img src="//image.wconcept.co.kr/productimg/image/img4/67/300907767.jpg" alt=""></a></div>
				# <div class="text">
				# <a href="/Product/300907767">
				# <h3>SUCK U.K</h3>
				# <p class="name">키오스 장난감 고양이집</p>
				# <p class="option">옵션 :  COLOR single type</p>
				# <p class="price">39,000<span>원</span><span>/ 1개</span></p>
				# </a>
				# <div class="label">취소완료</div>
				# <button class="case_detail_btn" onclick="location.href='/MyPage/OrderClaimView?orderno=U01408333&amp;orderidxnum=1770795'">취소상세</button>
				# </div>
				# </div>
				# <div class="buttons">
				# </div>
				# <div class="total" data-vendorcd="3002118">
				# <p><strong>39,000</strong><span>원 + </span><strong>3,000</strong><span>원(배송비) = </span><strong>42,000</strong><span>원</span></p>
				# </div>
				######################
				
				product_list = section_ctx.find_all('div', class_='product')
				for product_ctx in product_list :
					ea_ctx = product_ctx.find('p', class_='price')
					if( ea_ctx != None) : 
						ea_str = ea_ctx.get_text().strip()
						split_list = ea_str.split('/')
						order_status_data.cod_count.append( int(__UTIL__.get_only_digit(split_list[1].strip() )) )
					
					goods_name_ctx = product_ctx.find('div', class_='text')
					if( goods_name_ctx != None) :
						a_link_ctx = goods_name_ctx.find('a')
						if( a_link_ctx != None) :
							if('href' in a_link_ctx.attrs) :
								product_url = a_link_ctx.attrs['href']
								split_list = product_url.split('/')
								order_status_data.cor_goods_code.append( split_list[2].strip() )
			
					cor_memo_ctx = product_ctx.find('div', class_='label')
					if( cor_memo_ctx != None) : 
						if(order_status_data.cor_memo == '' ) : order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
					
					
	
	
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_wconcept')
		__LOG__.Error( ex )
		pass
		
		
		
		
		

####################################################################################################
# 대상 사이트
# http://www.dhuman.co.kr
####################################################################################################

def get_order_data_dhuman( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호 / 결제금액
		#
		# <div class="odTit"><strong>주문번호</strong> <span>20200629-RA22K</span></div>
		# -------------------------------------------------
		# <div class="orderInfoBox">
		# <dl>
		# </dl>
		# <dl>
		# <dt>결제정보</dt>
		# <dd>하나 &nbsp; 23991003130504 ㈜ 지앤몰</dd>
		# </dl>
		# 
		# <dl>
		# <dt>최종결제금액</dt>
		# <dd><span class="price"><strong>
		# 9,600
		# </strong>원</span></dd>
		# </dl>
		# </div>
		######################
		div_list = soup.find_all('div', class_='odTit')
		for div_ctx in div_list :
			title_ctx = div_ctx.find('strong')
			value_ctx = div_ctx.find('span')
			if( title_ctx != None ) and ( value_ctx != None ) :
				title_str = title_ctx.get_text().strip()
				value_str = value_ctx.get_text().strip()
				if(title_str == '주문번호') : order_data.cor_order_no = value_str
				
		div_list = soup.find_all('div', class_='orderInfoBox')
		for div_ctx in div_list :
			span_ctx = div_ctx.find('span', class_='price')
			if( span_ctx != None ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( span_ctx.get_text().strip() ) )
			

	
		######################
		# 물품리스트
		#
		# <script type="text/javascript">  
		# var items = [
		#   {
		# "id": "IPLOI47EB",
		# "name": "오리안심&amp;채소 오리지널 50g",
		# "list_name": "",
		# "brand": "goobnemall",
		# "category": "",
		# "variant": "",
		# "list_position": 1,
		# "quantity": 2,  
		# "price": '2000.0'
		# }       
		# , 
		# {
		# "id": "TPXGVRHS6",
		# "name": "[BEST]영양특식 7종 50g 골라담기",
		# "list_name": "",
		# "brand": "goobnemall",
		# "category": "",
		# "variant": "",
		# "list_position": 1,
		# "quantity": 2,  
		# "price": '1300.0'
		# }       
		# ];
		# </script> 
		######################
		product_idx = 0
		cor_content = ''
			
		split_list = html.split('<script type="text/javascript">')
		for split_ctx in split_list :
			strip_idx = split_ctx.find('</script>')
			javascript_str = split_ctx[:strip_idx].replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ').replace('&quot;','').replace('\n','').replace("'","\"").strip()
			#
			# 물품리스트
			sub_javascript_list = javascript_str.split(';')
			for sub_javascript_ctx in sub_javascript_list :
				if( 0 <= sub_javascript_ctx.find('var items =') ) :
					product_split_list = sub_javascript_ctx.split( 'var items =' )
					json_str = product_split_list[1].strip().strip()

					json_data_list = json.loads( json_str )
					for json_data in json_data_list :
						for key in json_data :
							if(key == 'id') : order_data.cor_goods_code.append( json_data[key] )
							elif(key == 'quantity') : order_data.cod_count.append( int( json_data[key] ) )
							elif(key == 'name') :
								product_idx += 1
								if( product_idx == 1 ) : 
									cor_content = json_data[key] 	# 상품명
									order_data.cor_content = cor_content
								else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_dhuman')
		__LOG__.Error( ex )
		pass




def get_order_status_data_dhuman(  order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		contents_div_ctx = soup.find('div', id='contents')
		if(contents_div_ctx != None) :
			orderlist_list = contents_div_ctx.find_all('div', class_="orderList")
			for orderlist_ctx in orderlist_list :
				ul_ctx = orderlist_ctx.find('ul')
				if(ul_ctx != None) :
					order_list = ul_ctx.find_all('li')
					for order_ctx in order_list :
						######################
						# 주문번호
						#
						# <div class="orderTit">
						# <div class="tit"><span class="orderNum">2020.06.29<br>20200629-RA22K</span></div>
						# <div>
						# <strong class="fc02">무통장입금(법인계좌)</strong>
						# </div>
						# </div>
						######################
						cor_order_no_ctx = order_ctx.find('span', class_="orderNum")

						if( cor_order_no_ctx != None ) :
							text = cor_order_no_ctx.get_text().strip()
							cor_order_no = text[10:]
							#order_status_data.cos_order_no = text[10:]		# 테스트용
				
						#if( True ) :	# 테스트용
						if( cor_order_no == order_status_data.cos_order_no ) :		
							######################
							# 
							# 주문 상태
							# <div class="orderSum">
							# <p class="tit">주문접수</p>
							# <p class="priceW">총<span class="price"><strong>9,600</strong>원</span></p>
							# <p class="btnW">
							# <a href="/m/view/mypage/order/main/cancel/20200629-RA22K?search_start_dt=&amp;search_end_dt=" class="btnE sub2">
							# <button class="btnSS sub2">주문취소</button>
							# </a>
							# </p>
							# </div>
							######################
							
							cor_memo_div_ctx = order_ctx.find('div', class_="orderSum")
							if( cor_memo_div_ctx != None) : 
								cor_memo_ctx = cor_memo_div_ctx.find('p', class_='tit')
								if( cor_memo_ctx != None) : 
									if(order_status_data.cor_memo == '' ) : order_status_data.cor_memo = cor_memo_ctx.get_text().strip()
						
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
							#
							######################
							
							
							product_list = order_ctx.find_all('div', class_="orderItem")
							for product_ctx in product_list :
								ea_ctx = product_ctx.find('div', class_='itemQuantity')
								if( ea_ctx != None) : order_status_data.cod_count.append( int(__UTIL__.get_only_digit( ea_ctx.get_text().strip() )) )
								
								goods_name_ctx = product_ctx.find('div', class_='infoW')
								if( goods_name_ctx != None) :		
									a_link_ctx = goods_name_ctx.find('a')
									if( a_link_ctx != None) :
										if('href' in a_link_ctx.attrs) :
											product_url = a_link_ctx.attrs['href']
											split_list = product_url.split('/')
											order_status_data.cor_goods_code.append( split_list[4].strip() )
	
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_dhuman')
		__LOG__.Error( ex )
		pass
		
		
		

####################################################################################################
# 대상 사이트
# https://www.bodeum.co.kr
####################################################################################################

def get_order_data_bodeum( order_data, html ) :
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')

		
		######################
		# 주문번호 / 결제금액
		#
		# <div class="order-date">
		# 2020-06-30  <span>[주문번호 : <a href="../mypage/orderDetail.php?trade_gubun=1&amp;idx=207375&amp;enc_data=">KEPJO1593481213</a>]
		# </span>
		# </div>
		#
		# -------------------------------------------------
		# <div class="total">
		# <div>
		# <dl>
		# <dt>총 상품금액</dt>
		# <dd>38,000원</dd>
		# </dl>
		# .. 생략
		# <dl>
		# <dt>총 결제금액</dt>
		# <dd><strong>41,000</strong>원</dd>
		# </dl>
		# </div>
		# </div>
		######################
		div_list = soup.find_all('div', class_='order-date')
		for div_ctx in div_list :
			value_ctx = div_ctx.find('a')
			if( value_ctx != None ) : order_data.cor_order_no = value_ctx.get_text().strip()
				
		div_list = soup.find_all('div', class_='total')
		for div_ctx in div_list :
			dl_list = div_ctx.find_all('dl')
			for dl_ctx in dl_list :
				title_ctx = dl_ctx.find('dt')
				value_ctx = dl_ctx.find('dd')
				if(title_ctx != None) and (value_ctx != None) : 
					title_str = title_ctx.get_text().strip()
					value_str = value_ctx.get_text().strip()
					if( title_str == '총 결제금액' ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( value_str ) )
				

	
		######################
		# 물품리스트
		#
		# <div class="order-complete">
		# <table class="list-table order-table payment-table mb-50">
		# <thead>
		# <tr>
		# <th colspan="3">
		# <div class="order-date">
		# 2020-06-30  <span>[주문번호 : <a href="../mypage/orderDetail.php?trade_gubun=1&amp;idx=207375&amp;enc_data=">KEPJO1593481213</a>]
		# </span>
		# </div>
		# </th>
		# </tr>
		# </thead>
		# <tbody>
		# <tr>
		# <td class="prd-info">
		# <div class="title-wrap">
		# <div class="imgArea">
		# <div class="ratio2 thumbnail-wrapper">
		# <div class="thumbnail">
		# <div class="centered">
		# <img src="/data/goodsImages/1529307661_IMAGES1.jpg">
		# </div> 
		# </div> 
		# </div>
		# </div>
		# <div class="buy-info">
		# <div class="prd_code_num">상품주문번호 : KEPJO1593481213-1</div>
		# <p class="title-txt">
		# <a href="/html/shop/prd_detail.php?idx=179">보듬 가슴줄 (H형 가슴줄)</a>
		# </p>
		# <div class="option">
		# <p>컬러 : 네이비</p>															<p>사이즈 : 보듬 S</p>																													</div>
		# <div class="quantity">1개</div>													</div>
		# </div>
		# </td>
		# <td class="col-price">
		# <span class="label">상품금액</span>
		# <span class="price"><strong>38,000</strong>원</span>
		# </td>
		# <td class="col-orderState">
		# <span class="label">상태</span>
		# <span><span class="blue"><span class="blue">입금대기중</span> </span>
		# <br>(2020-07-07 23:59:59 이내 입금)</span>
		# </tr>
		# </tbody>
		# </table>
		# .. 생략
		######################
		
		section_list = soup.find_all('div', class_='order-complete')
		for section_ctx in section_list :
			product_idx = 0
			cor_content = ''
			tr_list = section_ctx.find_all('tr')
			for product_ctx in tr_list :
				ea_ctx = product_ctx.find('div', class_='quantity')
				if( ea_ctx != None) : order_data.cod_count.append( int( __UTIL__.get_only_digit( ea_ctx.get_text().strip() ) ) )
						
				text_ctx = product_ctx.find('p', class_='title-txt')
				if( text_ctx != None ) : 
					product_url_ctx = text_ctx.find('a')
					if( product_url_ctx != None) :
						if('href' in product_url_ctx.attrs) :
							product_idx += 1
							product_url = product_url_ctx.attrs['href']
							product_no_list = product_url.split('?idx=')
							order_data.cor_goods_code.append( product_no_list[1].strip() )
							# 물품명
							if( product_idx == 1 ) : 
								cor_content = product_url_ctx.get_text().strip() 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )
					

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_bodeum')
		__LOG__.Error( ex )
		pass




def get_order_status_data_bodeum(  order_status_data, html ) :
	try :
	
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')		
		
		div_ctx = soup.find('div', class_="rightBlock" )
		if( div_ctx != None) :
			table_ctx_list = div_ctx.find_all('table' )
			for table_ctx in table_ctx_list :
				if( cor_order_no != '' ) and (cor_order_no == order_status_data.cos_order_no ) : break		# 해당되는 주문번호만 추출
				######################
				# 주문번호
				#
				# <div class="order-date">
				# 2020-06-30													<!-- ?if($trade_gubun=='2' || $trade_gubun=='3' || $trade_gubun=='4'){?>< ?=$tools->strDateCut($trade_row->trade_money_ok,3);?>< ?} else { ?>< ?=$tools->strDateCut($trade_row->trade_day,3); ?>< ?}? -->  <span>[주문번호 : KEPJO1593481213]</span>
				# </div>
				######################
				cor_order_no_ctx = table_ctx.find('div', class_='order-date')
				if( cor_order_no_ctx != None ) :
					cor_order_ctx = cor_order_no_ctx.find('span')
					if( cor_order_ctx != None ) :
						text = cor_order_ctx.get_text().replace('주문번호','').replace(':','').replace('[','').replace(']','').strip()
						cor_order_no = text
						#order_status_data.cos_order_no = text		# 테스트용
					
				#if( True ) :	# 테스트용
				if( cor_order_no == order_status_data.cos_order_no ) :	
					tr_list = table_ctx.find_all('tr')
					for tr_ctx in tr_list :
						######################
						# 물품리스트
						#
						# <tr>
						# <td class="prd-info">
						# <div class="title-wrap">
						# <div class="imgArea">
						# <div class="ratio2 thumbnail-wrapper">
						# <div class="thumbnail">
						# <div class="centered">
						# <img src="/data/goodsImages/1529307661_IMAGES1.jpg">
						# </div> 
						# </div> 
						# </div>
						# </div>
						# <div class="buy-info">
						# <p class="title-txt">
						# </p><div class="mb-5 orderNumber">상품주문번호 : KEPJO1593481213-1</div>
						# <a href="/html/shop/prd_detail.php?idx=179">보듬 가슴줄 (H형 가슴줄)</a>
						# <p></p>
						# <div class="option">
						# <p>컬러 : 네이비</p>															<p>사이즈 : 보듬 S</p>																													</div>
						# <div class="quantity">1개</div>
						# </div>
						# </div>
						# </td>
						# <td class="col-price">
						# <span class="label">상품금액</span>
						# <span class="price"><strong>38,000</strong>원</span>
						# </td>
						# <td class="col-orderState">
						# <span class="label">상태</span>
						# <span><span class="blue">입금대기중</span> <br>(2020-07-07 23:59:59 이내 입금)</span>
						# </td>
						# </tr>
						######################
						
						ea_ctx = tr_ctx.find('div', class_='quantity')
						if(ea_ctx != None) : order_status_data.cod_count.append( int(__UTIL__.get_only_digit( ea_ctx.get_text().strip() )) )
						
						cor_memo_ctx = tr_ctx.find('td', class_='col-orderState')
						if(cor_memo_ctx != None) : 
							text = cor_memo_ctx.get_text().replace('상태','').strip()
							split_list = text.split('(')
							order_status_data.cor_memo = split_list[0].strip()
							
						product_ctx = tr_ctx.find('div', class_='buy-info')
						if(product_ctx != None) : 
							a_link_ctx = product_ctx.find('a')
							if(a_link_ctx != None) : 
								if('href' in a_link_ctx.attrs) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('?idx=')
									order_status_data.cor_goods_code.append( split_list[1].strip() )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_bodeum')
		__LOG__.Error( ex )
		pass
		
		
		
	

####################################################################################################
# 대상 사이트
# purplestore.co.kr
# -- script에서 데이터 추출
####################################################################################################

def get_order_data_purplestore( order_data, html ) :
	try :

		######################
		# 주문번호 / 결제금액 / 물품리스트 -- script에서 데이터 추출
		#
		# 
		# <script>
		# const dataLayerContent = {
		# 'ecommerce': {
		# 'purchase': {
		# 'actionField': {
		# 'id': '37497',
		# 'affiliation': '퍼플스토어',
		# 'revenue': '14000',
		# 'tax':'0',
		# 'shipping': '0',
		# },
		# 'products': [{'name': '[아웃워드하운드] DOG 슬로우식기 미니 그린', 'id': '2556', 'price': 14000, 'brand': '아웃워드하운드', 'category': '개|용품|식기·주방|기능성 식기', 'quantity': 1}],
		# }
		# }
		# };
		# window.dataLayerProd = window.dataLayerProd || [];
		# window.dataLayerProd.push(dataLayerContent);
		# </script>
		######################
		
		split_list = html.split('<script>')
		for split_data in split_list :
			find_str = 'const dataLayerContent ='
			if(0 <= split_data.find(find_str) ) :
				find_idx = split_data.find(find_str) + len(find_str)
				strip_idx = split_data.find(';')
				json_str = split_data[find_idx:strip_idx]
				order_list = json_str.split("'products':")
				if(len(order_list) == 2) :
					order_info_list = order_list[0].split(',')
					for order_info in order_info_list :
						sub_value_list = order_info.split(':')
						if( 0 <= order_info.find("'id':") ) : 
							sub_value_list = order_info.split('{')
							for sub_value in sub_value_list :
								if( 0 <= sub_value.find("'id':") ) : 
									sub_id_list = sub_value.split(':')
									order_data.cor_order_no = sub_id_list[1].replace("'","").strip()
						elif( 0 <= order_info.find("'revenue':") ) : order_data.total_price_sum = int( __UTIL__.get_only_digit( sub_value_list[1] ) )
					
					product_idx = 0
					cor_content = ''
					order_product_list = order_list[1].split(',')
					for order_product in order_product_list :
						sub_value_list = order_product.split(':')
						if( 0 <= order_product.find("'id':") ) : 
							order_data.cor_goods_code.append( sub_value_list[1].replace("'","").strip() )
						elif( 0 <= order_product.find("'quantity':") ) : 
							order_data.cod_count.append( int( __UTIL__.get_only_digit( sub_value_list[1] ) ) ) 
						elif( 0 <= order_product.find("'name':") ) : 
							product_idx += 1
							# 물품명
							if( product_idx == 1 ) : 
								cor_content = sub_value_list[1].replace("'","").strip() 	# 상품명
								order_data.cor_content = cor_content
							else : order_data.cor_content = '%s 외 %d 개 상품' % (cor_content, (product_idx - 1) )

	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_purplestore')
		__LOG__.Error( ex )
		pass




def get_order_status_data_purplestore(  order_status_data, html ) :
	try :
		cor_order_no = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		section_ctx = soup.find('section', id="section")
		if( section_ctx != None ) :

			######################
			# 주문번호
			#
			# <span class="header-info__serial">주문번호 : <span class="num">37497</span></span>
			######################
			cor_order_no_ctx = section_ctx.find('span', class_="header-info__serial")

			if( cor_order_no_ctx != None ) :
				span_ctx = cor_order_no_ctx.find('span', class_='num')
				if( span_ctx != None ) : 
					text = span_ctx.get_text().strip()
					cor_order_no = text
					#order_status_data.cos_order_no = text		# 테스트용
				
			#if(True) :
			if( cor_order_no == order_status_data.cos_order_no ) :		

				######################
				# 물품리스트
				#
				# <li class="_saleItem sale-info" data-cancelled-order-id="37816" data-order-detail-id="102639" data-sale-id="2556"><div class="sale-info__content"><a href="/products/sales/2566/"><div class="sale-info__thumbnail"><img alt="상품 이미지" class="_saleImage image--no-bg" src="https://cdn.purplesto.re/media/store/sale/main_image/outwardhound_dog_B048DS01_thumb01.png"></div></a><div class="sale-info__info"><a href="/products/sales/2566/"><div class="_saleInfo sale-info__title" data-brand-name="아웃워드하운드" data-customer-type="DOG" data-sale-name="슬로우식기 미니 그린">[아웃워드하운드] DOG 슬로우식기 미니 그린</div></a><div class="sale-info__detail"><span class="_saleQty count" data-qty="1">수량 1개</span> <span class="_salePrice price" data-selling-price="14000">14,000원</span></div><ul class="order-status"><li class="status"><a class="link" href="https://www.doortodoor.co.kr/parcel/doortodoor.do?fsp_action=PARC_ACT_002&amp;fsp_cmd=retrieveInvNoACT&amp;invc_no=353976176842" rel="noopener noreferrer" target="_blank"><span class="text">배송완료</span> <i class="icon"><svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><path d="M15.423 12L6.4 4.78l1.25-1.56L18.625 12 7.649 20.78l-1.25-1.56z" id="ChveronBoldIconA"></path></defs><g fill="none" fill-rule="evenodd"><mask fill="#fff" id="ChveronBoldIconB"><use xlink:href="#ChveronBoldIconA"></use></mask><use fill="#000" fill-rule="nonzero" xlink:href="#ChveronBoldIconA"></use><g fill="#000" mask="url(#ChveronBoldIconB)"><path d="M0 0h24v24H0z"></path></g></g></svg></i></a></li><li class="status"><button class="_cancelledStatusBtn button" type="button"><span class="text">반품상세</span> <i class="icon"><svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><path d="M15.423 12L6.4 4.78l1.25-1.56L18.625 12 7.649 20.78l-1.25-1.56z" id="ChveronBoldIconA"></path></defs><g fill="none" fill-rule="evenodd"><mask fill="#fff" id="ChveronBoldIconB"><use xlink:href="#ChveronBoldIconA"></use></mask><use fill="#000" fill-rule="nonzero" xlink:href="#ChveronBoldIconA"></use><g fill="#000" mask="url(#ChveronBoldIconB)"><path d="M0 0h24v24H0z"></path></g></g></svg></i></button></li></ul></div></div></li>
				######################
				ul_ctx = section_ctx.find('ul', class_='order-item__sale__list')
				if( ul_ctx != None) : 
					product_list = ul_ctx.find_all('li', class_='_saleItem sale-info')
					for product_ctx in product_list :
						ea_ctx = product_ctx.find('span', class_='_saleQty count')
						if( ea_ctx != None) : order_status_data.cod_count.append( int(__UTIL__.get_only_digit(ea_ctx.get_text().strip() )) )
						
						goods_name_ctx = product_ctx.find('div', class_='sale-info__info')
						if( goods_name_ctx != None) :
							a_link_ctx = goods_name_ctx.find('a')
							if( a_link_ctx != None) :
								if('href' in a_link_ctx.attrs) :
									product_url = a_link_ctx.attrs['href']
									split_list = product_url.split('/')
									order_status_data.cor_goods_code.append( split_list[3].strip() )
				
						cor_memo_ctx = product_ctx.find('li', class_='status')
						if( cor_memo_ctx != None) : 
							if(order_status_data.cor_memo == '' ) : 
								span_ctx = cor_memo_ctx.find('span' , class_='text')
								if( span_ctx != None) : order_status_data.cor_memo = span_ctx.get_text().strip()

		
						
	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_purplestore')
		__LOG__.Error( ex )
		pass
		
		
	

####################################################################################################
# 대상 사이트
# queenpuppy.co.kr
#
####################################################################################################

def get_order_data_queenpuppy( order_data, html ) :
	#
	# 물품리스트 없음 / 가격은 script에서 얻어옴
	#
	try :
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		######################
		# 주문번호 / 결제금액 / 물품리스트 -- script에서 데이터 추출
		#
		# 
		# <div class="ending_order_num">주문번호 : <span class="price2"><strong>1192869</strong></span></div>
		######################
		box_wrap_cart_ctx = soup.find('div', id='box_wrap_cart')
		if( box_wrap_cart_ctx != None ) :
			ending_order_num_div = box_wrap_cart_ctx.find('div', class_='ending_order_num')
			if( ending_order_num_div != None ) :
				cor_order_no_ctx = ending_order_num_div.find('strong')
				if( cor_order_no_ctx != None ) :
					order_data.cor_order_no = cor_order_no_ctx.get_text().strip()
		
		#############################
		# 구매가격
		#
		# <script>
		# fbq("track", "Purchase", {
		#     value: "6500",
		#     currency: "KRW"
		# });
		# </script>
		#############################
		
		split_list = html.split('<script>')
		for split_data in split_list :
			strip_idx = split_data.find('</script>')
			javascript_str = split_data[: strip_idx]
			
			if(0 <= javascript_str.find('fbq(') ) and (0 < javascript_str.find('"Purchase"') ) and (0 < javascript_str.find('value') ):
				sub_split_list = javascript_str.split(',')
				for sub_split_data in sub_split_list :
					value_str = sub_split_data.strip()
					if( 0 <= value_str.find('value:') ) :
						value_list = value_str.split(':')
						order_data.total_price_sum = int( __UTIL__.get_only_digit( value_list[1].replace('"','').strip() ) )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_data_queenpuppy')
		__LOG__.Error( ex )
		pass




def get_order_status_data_queenpuppy(  order_status_data, html ) :
	try :
		cor_order_no = ''
		status_value = ''
		
		#cor_order_no = order_status_data.cos_order_no	# 테스트용
		#order_status_data.cos_order_no = ''				# 테스트용
		
		soup = bs4.BeautifulSoup(html, 'lxml')
			
		######################
		# 주문번호
		#
		# <div id="order_detail">
		# <div class="tit">주문번호</div>
		# <div class="content">1192869</div>
		# </div>
		######################
		cor_order_no_ctx_list = soup.find_all('div', id="order_detail")
		for cor_order_no_ctx in cor_order_no_ctx_list :
			title_ctx = cor_order_no_ctx.find('div', class_='tit')
			value_ctx = cor_order_no_ctx.find('div', class_='content')
			if(title_ctx != None) and (value_ctx != None) :
				title_str = title_ctx.get_text().strip()
				value_str = value_ctx.get_text().strip()
				if(title_str == '주문번호') :
					cor_order_no = value_str
					#order_status_data.cos_order_no = value_str		# 테스트용
				elif(title_str == '진행정보') :
					status_value = value_str
			
		#if(True) :
		if( cor_order_no == order_status_data.cos_order_no ) :		
			
			order_status_data.cor_memo = status_value
			
			######################
			# 물품리스트
			#
			# <li class="_saleItem sale-info" data-cancelled-order-id="37816" data-order-detail-id="102639" data-sale-id="2556"><div class="sale-info__content"><a href="/products/sales/2566/"><div class="sale-info__thumbnail"><img alt="상품 이미지" class="_saleImage image--no-bg" src="https://cdn.purplesto.re/media/store/sale/main_image/outwardhound_dog_B048DS01_thumb01.png"></div></a><div class="sale-info__info"><a href="/products/sales/2566/"><div class="_saleInfo sale-info__title" data-brand-name="아웃워드하운드" data-customer-type="DOG" data-sale-name="슬로우식기 미니 그린">[아웃워드하운드] DOG 슬로우식기 미니 그린</div></a><div class="sale-info__detail"><span class="_saleQty count" data-qty="1">수량 1개</span> <span class="_salePrice price" data-selling-price="14000">14,000원</span></div><ul class="order-status"><li class="status"><a class="link" href="https://www.doortodoor.co.kr/parcel/doortodoor.do?fsp_action=PARC_ACT_002&amp;fsp_cmd=retrieveInvNoACT&amp;invc_no=353976176842" rel="noopener noreferrer" target="_blank"><span class="text">배송완료</span> <i class="icon"><svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><path d="M15.423 12L6.4 4.78l1.25-1.56L18.625 12 7.649 20.78l-1.25-1.56z" id="ChveronBoldIconA"></path></defs><g fill="none" fill-rule="evenodd"><mask fill="#fff" id="ChveronBoldIconB"><use xlink:href="#ChveronBoldIconA"></use></mask><use fill="#000" fill-rule="nonzero" xlink:href="#ChveronBoldIconA"></use><g fill="#000" mask="url(#ChveronBoldIconB)"><path d="M0 0h24v24H0z"></path></g></g></svg></i></a></li><li class="status"><button class="_cancelledStatusBtn button" type="button"><span class="text">반품상세</span> <i class="icon"><svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><path d="M15.423 12L6.4 4.78l1.25-1.56L18.625 12 7.649 20.78l-1.25-1.56z" id="ChveronBoldIconA"></path></defs><g fill="none" fill-rule="evenodd"><mask fill="#fff" id="ChveronBoldIconB"><use xlink:href="#ChveronBoldIconA"></use></mask><use fill="#000" fill-rule="nonzero" xlink:href="#ChveronBoldIconA"></use><g fill="#000" mask="url(#ChveronBoldIconB)"><path d="M0 0h24v24H0z"></path></g></g></svg></i></button></li></ul></div></div></li>
			######################
			div_ctx_list = soup.find_all('div', id='box_wrap_cart')
			for div_ctx in div_ctx_list :				
				ea_ctx_list = div_ctx.find_all('span', class_='cart_price3')
				for ea_ctx in ea_ctx_list :
					ea_str = ea_ctx.get_text().strip()
					split_list = ea_str.split('x')
					if(len( split_list ) == 2 ) :
						order_status_data.cod_count.append( int(__UTIL__.get_only_digit(split_list[1].strip() )) )
								
			
				goods_name_ctx_list = div_ctx.find_all('div', id='cart_name')
				for goods_name_ctx in goods_name_ctx_list :
					a_link_ctx = goods_name_ctx.find('a')
					if( a_link_ctx != None) :
						if('href' in a_link_ctx.attrs) :
							product_url = a_link_ctx.attrs['href']
							split_list = product_url.split('?pd_code=')
							if(len( split_list ) == 2 ) : order_status_data.cor_goods_code.append( split_list[1].strip() )


	except Exception as ex:
		__LOG__.Error('에러 : get_order_status_data_queenpuppy')
		__LOG__.Error( ex )
		pass