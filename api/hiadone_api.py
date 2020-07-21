#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import requests
from datetime import date
from datetime import datetime
import log as Log;  Log.Init()
from app import config
from model.ApiData import BrdData

'''
#################################################################################
##
##	스토어 리스트 api 
##
#################################################################################
'''
	
def get_storelist_by_brd_id(mall_brd_id): 
	#
	# mall_type : smartstore 및 navershop 용으로 사용하기 위해 정의함.
	# brd_url 에 특정 url 을 비교하기 위함.
	#
	BRD_URL = ''
	data = None
	URL = 'http://adm.denguru.kr/crawl/get_storelist'
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : get_storelist_by_brd_id API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				data = json.loads(res.text)
				if('list' in data ) :
					brd_id_list_json = data['list']
					for list_idx in brd_id_list_json :
						sub_list_json = brd_id_list_json[list_idx]
						brd_id = 0
						brd_url = ''
						for key in sub_list_json :
							if(key == 'brd_id') : brd_id = int( sub_list_json[key] )
							elif(key == 'brd_url') : brd_url = sub_list_json[key].strip()
							
						if(brd_url != '' ) and ( brd_id == int(mall_brd_id) ):
							BRD_URL = brd_url
							#__LOG__.Trace('%d : %s' % (brd_id, brd_url))
							break
							
					
			except Exception as ex :
				__LOG__.Error( "실패 : get_storelist_by_brd_id API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : get_storelist_by_brd_id API")
		__LOG__.Error( exb)
		pass
		
	return BRD_URL
	
'''
#################################################################################
##
##	스토어 리스트 api 
##
#################################################################################
'''
	
def get_storelist(mall_type=''): 
	#
	# mall_type : smartstore 및 navershop 용으로 사용하기 위해 정의함.
	# brd_url 에 특정 url 을 비교하기 위함.
	#
	BRD_ID_HASH = {}
	data = None
	URL = 'http://adm.denguru.kr/crawl/get_storelist'
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : GET_STORELIST API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				data = json.loads(res.text)
				if('list' in data ) :
					brd_id_list_json = data['list']
					for list_idx in brd_id_list_json :
						sub_list_json = brd_id_list_json[list_idx]
						brd_id = 0
						brd_url = ''
						for key in sub_list_json :
							if(key == 'brd_id') : brd_id = int( sub_list_json[key] )
							elif(key == 'brd_url') : brd_url = sub_list_json[key].strip()
							
						if(brd_url != '' ) and ( 0 <= brd_url.find(mall_type) ):
							if(BRD_ID_HASH.get(brd_url, -1) == -1) : 
								BRD_ID_HASH[brd_url] = brd_id
								__LOG__.Trace('%d : %s' % (brd_id, brd_url))
							
					
			except Exception as ex :
				__LOG__.Error( "실패 : GET_STORELIST API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : GET_STORELIST API")
		__LOG__.Error( exb)
		pass
		
	return BRD_ID_HASH

'''
#################################################################################
##
##	아이템 정보  api 
##
#################################################################################
'''
def get_itemlist(brd_id): 
	#
	#
	PRODUCT_ITEM_HASH = {}
	data = None
	URL = 'http://adm.denguru.kr/crawl/get_itemlist/%d/' % ( brd_id )
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : GET_ITEMLIST API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				data = json.loads(res.text)
				if('item' in data ) : 
					jsondata = data['item']
					for item in jsondata :
						PRODUCT_ITEM_HASH[item['crw_goods_code']] = int( item['crw_id'] )
						
					
			except Exception as ex :
				__LOG__.Error( "실패 : GET_ITEMLIST API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : GET_ITEMLIST API")
		__LOG__.Error( exb)
		pass
		
	return PRODUCT_ITEM_HASH
	

'''
#################################################################################
##
##	상품 입력 api
##  - insert_itemlist : 상품입력
##	- update_itemlist : 기존 상품 업데이트
#################################################################################
'''
def insert_itemlist(product_data): 
	#
	# 상품리스트에서의 내용을 입력
	#
	crw_id = 0
	try :
		
		data = None
		URL = 'http://adm.denguru.kr/crawl/insert_itemlist/%d/' % ( product_data.brd_id )
		
		#보내고자하는 파일을 'rb'(바이너리 리드)방식 열고
		img_files = open( product_data.crw_file_1 , 'rb')

		upload = {'crw_file_1' : img_files }
			
		
		params = {'crw_name' : product_data.crw_name ,
					'crw_price' : product_data.crw_price ,
					'crw_is_soldout' : product_data.crw_is_soldout ,
					'crw_goods_code' : product_data.crw_goods_code ,
					'crw_post_url' : product_data.crw_post_url ,
					'crw_price_sale' : product_data.crw_price_sale ,
					'crw_brand1' : product_data.crw_brand1 ,
					'crw_brand2' : product_data.crw_brand2 ,
					'crw_brand3' : product_data.crw_brand3 ,
					'crw_brand4' : product_data.crw_brand4 ,
					'crw_brand5' : product_data.crw_brand5 ,
					'crw_category1' : product_data.crw_category1 ,
					'crw_category2' : product_data.crw_category2 ,
					'crw_category3' : product_data.crw_category3 }
		
		
		res = requests.post(URL , files=upload, data=params)
		
		if(config.__DEBUG__) :
			__LOG__.Trace( URL )
			__LOG__.Trace( params )
		
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : INSERT_ITEMLIST API res.status_code : %s " % str(res.status_code) )
		else : 
			
			data = json.loads(res.text)
			if('resultcode' in data) :
				if(data['resultcode'] == 1) : 
					__LOG__.Trace('성공 : INSERT_ITEMLIST API (%s)' % ( URL) )
					if('crw_id' in data ) : crw_id = data['crw_id']
					
				else : 
					__LOG__.Trace('실패 : INSERT_ITEMLIST API (%d)' % (data['resultcode']) )
					__LOG__.Trace( URL )
					__LOG__.Trace( params )

	except Exception as exb :
		__LOG__.Error( "실패 : INSERT_ITEMLIST API")
		__LOG__.Error( exb)
		pass
	
	return crw_id
	
		
def update_itemlist(product_data): 
	#
	# 상품리스트에서의 내용을 업데이트
	# 업데이트시 이미지 업로드 미실시함.
	# 
	try :
		data = None
		URL = 'http://adm.denguru.kr/crawl/insert_itemlist/%d/%d' % ( product_data.brd_id, product_data.crw_id )
			
		
		params = {'crw_name' : product_data.crw_name ,
					'crw_price' : product_data.crw_price ,
					'crw_is_soldout' : product_data.crw_is_soldout ,
					'crw_goods_code' : product_data.crw_goods_code ,
					'crw_post_url' : product_data.crw_post_url ,
					'crw_price_sale' : product_data.crw_price_sale ,
					'crw_brand1' : product_data.crw_brand1 ,
					'crw_brand2' : product_data.crw_brand2 ,
					'crw_brand3' : product_data.crw_brand3 ,
					'crw_brand4' : product_data.crw_brand4 ,
					'crw_brand5' : product_data.crw_brand5 ,
					'crw_category1' : product_data.crw_category1 ,
					'crw_category2' : product_data.crw_category2 ,
					'crw_category3' : product_data.crw_category3 }
					
		res = requests.post(URL , data=params)	
		
		if(config.__DEBUG__) :
			__LOG__.Trace( URL )
			__LOG__.Trace( params )
					
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : UPDATE_ITEMLIST res.status_code : %s " % str(res.status_code) )
		else : 

			data = json.loads(res.text)
			if('resultcode' in data) :
				if(data['resultcode'] == 1) : __LOG__.Trace('성공 : UPDATE_ITEMLIST API (%s)' % ( URL ) )
				else : 
					__LOG__.Trace('실패 : UPDATE_ITEMLIST API (%d)' % (data['resultcode']) )
					__LOG__.Trace( URL )
					__LOG__.Trace( params )
					
					
	except Exception as exb :
		__LOG__.Error( "실패 : UPDATE_ITEMLIST API")
		__LOG__.Error( exb)
		pass
		
		
'''
#################################################################################
##
##	상품 삭제 api
##
#################################################################################
'''
def is_delete(crw_id): 
	#
	#
	data = None
	URL = 'http://adm.denguru.kr/crawl/is_delete/%d' % ( crw_id )
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : IS_DELETE API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				data = json.loads(res.text)
				if('resultcode' in data) :
					if(data['resultcode'] == 1) : __LOG__.Trace('성공 : IS_DELETE API (%s)' % ( URL ) )
					else : 
						__LOG__.Trace('실패 : IS_DELETE API (%d)' % (data['resultcode']) )
						__LOG__.Trace( URL )
					
			except Exception as ex :
				__LOG__.Error( "실패 : IS_DELETE API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : IS_DELETE API")
		__LOG__.Error( exb)
		pass
		
	
'''
#################################################################################
##
##	상품 상세설명 입력 api
##
#################################################################################
'''

def insert_itemdetail(product_data): 
	#
	# 상품리스트에서의 내용을 입력
	#
	try :
		
		data = None
		URL = 'http://adm.denguru.kr/crawl/insert_itemdetail/%d/%d' % ( product_data.brd_id, product_data.crw_id )
		
		#보내고자하는 파일을 'rb'(바이너리 리드)방식 열고
		upload = {'cdt_file_1' : None }
		if( product_data.d_crw_file_1 != '' ) : 
			img_files = open( product_data.d_crw_file_1 , 'rb')
			upload = {'cdt_file_1' : img_files }
			
		
		params = {'cdt_content' : product_data.cdt_content ,
					'cdt_brand1' : product_data.d_crw_brand1 ,
					'cdt_brand2' : product_data.d_crw_brand2 ,
					'cdt_brand3' : product_data.d_crw_brand3 ,
					'cdt_brand4' : product_data.d_crw_brand4 ,
					'cdt_brand5' : product_data.d_crw_brand5  }
		
		res = None
		if( product_data.d_crw_file_1 != '' ) : res = requests.post(URL , files=upload, data=params)
		else : res = requests.post(URL , data=params)
		
		if(config.__DEBUG__) :
			__LOG__.Trace( URL )
			__LOG__.Trace( product_data.d_crw_file_1 )
			__LOG__.Trace( params )
		
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : INSERT_ITEMDETAIL API res.status_code : %s " % str(res.status_code) )
		else : 
			
			data = json.loads(res.text)
			if('resultcode' in data) :
				if(data['resultcode'] == 1) : __LOG__.Trace('성공 : INSERT_ITEMDETAIL API (%s)' % ( URL) )
				else : 
					__LOG__.Trace('실패 : INSERT_ITEMDETAIL API (%d)' % (data['resultcode']) )
					__LOG__.Trace( URL )
					__LOG__.Trace( params )

	except Exception as exb :
		__LOG__.Error( "실패 : INSERT_ITEMDETAIL")
		__LOG__.Error( exb)
		pass

'''
#################################################################################
##
##	주문 html 정보  얻어오는 api 
##
#################################################################################
'''
def get_order_html_file(cor_id, order_data): 
	#
	#
	data = None
	URL = 'http://adm.denguru.kr/crawl/get_order_html_file/%d' % ( cor_id )
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : GET_ORDER_HTML_FILE API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				jsondata = json.loads(res.text)
				
				for item in jsondata :
					if(item == 'mem_id') : order_data.mem_id = int( jsondata[item] )
					elif(item == 'brd_id') : order_data.brd_id = int( jsondata[item] )
					elif(item == 'cor_key') : order_data.cor_key = jsondata[item]
					elif(item == 'cor_file_1') : order_data.cor_file_1 = jsondata[item]
					elif(item == 'brd_url') : order_data.brd_url = jsondata[item]
					elif(item == 'cor_pay_type') : 
						if( jsondata[item] != None ) : order_data.cor_pay_type = jsondata[item]
					
				__LOG__.Trace(res.text)
				
			except Exception as ex :
				__LOG__.Error( "실패 : GET_ORDER_HTML_FILE API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : GET_ORDER_HTML_FILE API")
		__LOG__.Error( exb)
		pass
		

	
'''
#################################################################################
##
##	주문정보 입력 api
##
#################################################################################
'''

def insert_order(order_data): 
	#
	# 주문정보 입력
	#
	try :
		
		data = None
		
		URL = "http://adm.denguru.kr/crawl/insert_order/%d/%d/%s/%s" % ( order_data.brd_id, order_data.mem_id , order_data.cor_order_no, order_data.cor_key )
		if( order_data.cor_pay_type != '') : URL = "http://adm.denguru.kr/crawl/insert_order/%d/%d/%s/%s/%s" % ( order_data.brd_id, order_data.mem_id , order_data.cor_order_no, order_data.cor_key, order_data.cor_pay_type )
		
		params = {'total_price_sum' : order_data.total_price_sum ,
					'cor_goods_code' : order_data.cor_goods_code ,
					'cod_count' : order_data.cod_count ,
					'cor_content' : order_data.cor_content }
		
		
		res = requests.post(URL ,data=params)
		
		if(config.__DEBUG__) :
			__LOG__.Trace( URL )
			__LOG__.Trace( params )
		
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : INSERT_ORDER API res.status_code : %s " % str(res.status_code) )
		else : 
			__LOG__.Trace( res.text )
			data = json.loads(res.text)
			if('resultcode' in data) :
				if(data['resultcode'] == 1) : __LOG__.Trace('성공 : INSERT_ORDER API (%s)' % ( URL) )
				else : 
					__LOG__.Trace('실패 : INSERT_ORDER API (%d)' % (data['resultcode']) )
					__LOG__.Trace( URL )
					__LOG__.Trace( params )

	except Exception as exb :
		__LOG__.Error( "실패 : INSERT_ORDER")
		__LOG__.Error( exb)
		pass


'''
#################################################################################
##
##	주문 status html 정보  얻어오는 api 
##
#################################################################################
'''
def get_orderstatus_html_file(cos_id, order_status_data): 
	#
	#
	data = None
	URL = 'http://adm.denguru.kr/crawl/get_orderstatus_html_file/%d' % ( cos_id )
	res = requests.get(URL)
	try :
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : GET_ORDERSTATUS_HTML_FILE API res.status_code : %s " % str(res.status_code) )
		else : 
			try :
				jsondata = json.loads(res.text)
				for item in jsondata :
					if(item == 'mem_id') : order_status_data.mem_id = int( jsondata[item] )
					elif(item == 'brd_id') : order_status_data.brd_id = int( jsondata[item] )
					elif(item == 'brd_url') : order_status_data.brd_url = jsondata[item]
					elif(item == 'cos_file_1') : order_status_data.cos_file_1 = jsondata[item]
					elif(item == 'cos_order_no') : order_status_data.cos_order_no = jsondata[item]
					elif(item == 'cor_pay_type') : 
						if( jsondata[item] != None ) : order_status_data.cor_pay_type = jsondata[item]

				__LOG__.Trace(res.text)
				
			except Exception as ex :
				__LOG__.Error( "실패 : GET_ORDERSTATUS_HTML_FILE API")
				__LOG__.Error( ex)
				pass
		
		
	except Exception as exb :
		__LOG__.Error( "실패 : GET_ORDERSTATUS_HTML_FILE API")
		__LOG__.Error( exb)
		pass
		

		
'''
#################################################################################
##
##	주문정보 업데이트 api
##
#################################################################################
'''		

def update_order(order_status_data): 
	#
	# 주문정보 업데이트
	#
	try :
		
		data = None
		URL = 'http://adm.denguru.kr/crawl/update_order/%d/%d/%s' % ( order_status_data.brd_id, order_status_data.mem_id , order_status_data.cos_order_no )
		
		params = {'cor_carrier' : order_status_data.cor_carrier ,
					'cor_track' : order_status_data.cor_track ,
					'cor_goods_code' : order_status_data.cor_goods_code ,
					'cod_count' : order_status_data.cod_count ,
					'cor_memo' : order_status_data.cor_memo }
					
		res = requests.post(URL ,data=params)
		
		if(config.__DEBUG__) :
			__LOG__.Trace( URL )
			__LOG__.Trace( params )
		
		if(res.status_code != 200) :
			__LOG__.Error( "실패 : UPDATE_ORDER API res.status_code : %s " % str(res.status_code) )
		else : 
			
			data = json.loads(res.text)
			if('resultcode' in data) :
				if(data['resultcode'] == 1) : __LOG__.Trace('성공 : UPDATE_ORDER API (%s)' % ( URL) )
				else : 
					__LOG__.Trace('실패 : UPDATE_ORDER API (%d)' % (data['resultcode']) )
					__LOG__.Trace( URL )
					__LOG__.Trace( params )

	except Exception as exb :
		__LOG__.Error( "실패 : UPDATE_ORDER")
		__LOG__.Error( exb)
		pass
		
if __name__ == '__main__':

    get_order_html_file(89)
