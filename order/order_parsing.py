#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user
'''
import json
import time
import os, signal
import sys
import bs4
import warnings
import chardet
import requests

from model.OrderData import OrderData, OrderStatusData
from app import config
from api import hiadone_api as __API__
from util import Util as __UTIL__

from order import order_naver as __NAVER__
from order import order_godo as __GODO__
from order import order_imweb as __IMWEB__
from order import order_makeshop as __MAKESHOP__
from order import order_sixshop as __SIXSHOP__

from order import order_cafe24 as __CAFE24__

from order import order_other as __ORDER_OTHER__

from order import order_wisa as __WISA__

import log as Log;  Log.Init()


if not sys.warnoptions:
    warnings.simplefilter("ignore")

__ORDER__ = '__ORDER__'
__ORDER_STATUS__ = '__ORDER_STATUS__'
__NAVER_PAY__ = 'naverpay'
	
'''
#
# smartstore / navershop
#
'''	
def order_naver( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- NAVER - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __NAVER__.get_order_data( order_data, order_html  )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __NAVER__.get_order_status_data( order_status_data, orderstatus_html )
	

'''
#
# IMWEB
#
'''	
def order_imweb( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- IMWEB - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1 , EUC_ENCODING)
		if( order_html != '' ) : __IMWEB__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __IMWEB__.get_order_status_data( order_status_data, orderstatus_html )
		


'''
#
# 고도몰
#
'''	
	
def order_godo( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- GODO - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __GODO__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __GODO__.get_order_status_data( order_status_data, orderstatus_html )
		

'''
#
# Makeshop
#
'''	
def order_makeshop( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- MAKESHOP - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __MAKESHOP__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __MAKESHOP__.get_order_status_data( order_status_data, orderstatus_html )
		

'''
#
# Wisa
#
'''		
def order_wisa( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- WISA - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __WISA__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1 , EUC_ENCODING)
		if( orderstatus_html != '' ) : __WISA__.get_order_status_data( order_status_data, orderstatus_html )
		

'''
#
# SixShop
#
'''	
def order_sixshop( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- SIXSHOP - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __SIXSHOP__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __SIXSHOP__.get_order_status_data( order_status_data, orderstatus_html )


		
'''
#
# Cafe24
#
'''		
def order_cafe24( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- CAFE24 - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1, EUC_ENCODING )
		if( order_html != '' ) : __CAFE24__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __CAFE24__.get_order_status_data( order_status_data, orderstatus_html )

		

		
'''
#
# other
#
'''	
def order_other( action_type, order_data, order_status_data ) :
	global __ORDER__ , __ORDER_STATUS__
	
	__LOG__.Trace('%d --- OTHER - %s' % ( order_data.action_value, order_data.search_web_str ))
	
	EUC_ENCODING = False
	
	if(action_type == __ORDER__) : 
		order_html = open_html( order_data.cor_file_1 , EUC_ENCODING)
		if( order_html != '' ) : __ORDER_OTHER__.get_order_data( order_data, order_html )
		
	elif(action_type == __ORDER_STATUS__) :
		orderstatus_html = open_html( order_status_data.cos_file_1, EUC_ENCODING )
		if( orderstatus_html != '' ) : __ORDER_OTHER__.get_order_status_data( order_status_data, orderstatus_html )


'''
#
# 공통
#
'''	


def open_html(html_file_path, EUC_ENCODING ) :
	html = ''
	
	try :				
		resp = None
		resp = requests.get( html_file_path )
		
		if(EUC_ENCODING != None) :
			if(EUC_ENCODING) : resp.encoding='euc-kr'  # 한글 EUC-KR인코딩
		else :
			resp.encoding=None								# 'ISO-8859-1'일때 인코딩
		
		if( resp.status_code != 200 ) :
			__LOG__.Error('에러 : open_html - 에러코드 ( %d )' % (resp.status_code))
		else :
			html = resp.text

	except Exception as ex:
		__LOG__.Error( "에러 : open_html (%s) " % ( html_file_path ) )
		__LOG__.Error( ex )
		pass
	
	return html

	
def print_order_data( order_data ) :
	if(config.__DEBUG__) :
		__LOG__.Trace( order_data.cor_file_1 )
		__LOG__.Trace( order_data.brd_id )
		__LOG__.Trace( order_data.mem_id )
		__LOG__.Trace( order_data.cor_key )
		__LOG__.Trace( order_data.cor_order_no )
		__LOG__.Trace( order_data.total_price_sum )
		__LOG__.Trace( order_data.cor_goods_code )
		__LOG__.Trace( order_data.cod_count )
		__LOG__.Trace( order_data.cor_content )


def print_order_status_data( order_status_data ) :
	if(config.__DEBUG__) :	
		__LOG__.Trace( order_status_data.cos_file_1 )
		__LOG__.Trace( order_status_data.brd_id )
		__LOG__.Trace( order_status_data.mem_id )
		__LOG__.Trace( order_status_data.cos_order_no )
		#__LOG__.Trace( order_status_data.cor_carrier )
		#__LOG__.Trace( order_status_data.cor_track )
		__LOG__.Trace( order_status_data.cor_goods_code )
		__LOG__.Trace( order_status_data.cod_count )
		__LOG__.Trace( order_status_data.cor_memo )

		
	
def get_file_name( brd_id, sel_file ) :
	#
	# TEST 용
	#
	order_file = ''
	orderstatus_file = ''
	
	order_file = '/home/crawling/HIADONE/order_html/cafe24/%s/order_%s.html' % (brd_id , sel_file)
	orderstatus_file = '/home/crawling/HIADONE/order_html/cafe24/%s/orderstatus_%s결과.html' % (brd_id, sel_file)
		
		
	return 	order_file, orderstatus_file

def open_html_from_file( html_file_path , encoding_str='utf-8') :
	#
	# TEST 용
	#
	html = None
	try :
		#with open(html_file_path, 'r', encoding=encoding_str) as f :
		with open(html_file_path, 'r') as f :
			html = f.read()
			f.close()
	except Exception as ex:
		__LOG__.Error('에러 : open_html_from_file')
		__LOG__.Error( ex )
		pass
		
	return html

	
if __name__ == '__main__':
	
	
	###########################################
	# 분기되는 함수 지정
	###########################################
	
	order_math_func = {
		'smartstore.naver.com' : order_naver,
		'shopping.naver.com' : order_naver,		
		'biteme.co.kr' : order_godo ,
		'fitpetmall.com' : order_godo ,
		'gaenimshop.com' : order_godo ,
		'ssfw.kr' : order_godo ,
		'diditable.com' : order_godo ,
		'ainsoap.com' : order_godo ,
		'gulliverdog.co.kr' : order_godo ,
		'edenchien.com' : order_godo ,
		'mytrianon.co.kr' : order_godo ,
		'petesthe.co.kr' : order_godo ,
		'bourdog.com' : order_godo ,
		'naturalex.co.kr' : order_godo ,
		'vlab.kr' : order_godo ,
		'wangzzang.com' : order_godo ,
		'petgear.kr' : order_godo ,		
		'duit.kr' : order_imweb ,
		'eledog.co.kr' : order_imweb ,
		'andblank.com' : order_imweb ,
		'yosemite.pet' : order_imweb ,
		'varram.co.kr' : order_imweb ,
		'hipaw.co.kr' : order_imweb ,
		'vuumpet.co.kr' : order_imweb ,
		'plumstudio.co.kr' : order_imweb ,
		'vavox.co.kr' : order_imweb ,
		'gettouch.co.kr' : order_imweb ,
		'cheesesun.com' : order_imweb ,		
		'oraeorae.com' : order_makeshop ,
		'cocochien.kr' : order_makeshop ,
		'hydewolf.co.kr' : order_makeshop ,
		'itsdog.com' : order_makeshop ,
		'petnoriter.co.kr' : order_makeshop ,
		'ecofoam.co.kr' : order_makeshop ,
		'puppygallery.co.kr' : order_makeshop ,
		'amylovespet.co.kr' : order_makeshop ,
		'dermadog.co.kr' : order_makeshop ,
		'affetto.co.kr' : order_makeshop ,		
		'howlpot.com' : order_wisa ,
		'smallstuff.kr' : order_wisa ,		
		'guilty-pleasure.co.kr' : order_sixshop ,
		'comercotte.com' : order_sixshop ,
		'melonicoco.com' : order_sixshop ,
		'ddoang.com' : order_sixshop ,
		'pawunion.kr' : order_sixshop ,
		'harryspet.com' : order_sixshop ,
		'wilddog.co.kr' : order_sixshop ,
		'bonjourtou-tou.com' : order_sixshop ,
		'pethod.co.kr' : order_sixshop ,		
		'purplestore.co.kr' : order_other ,
		'dhuman.co.kr' : order_other ,
		'montraum.com' : order_other ,
		'petsandme.co.kr' : order_other ,
		'gubas.co.kr' : order_other ,
		'bodeum.co.kr' : order_other ,
		'queenpuppy.co.kr' : order_other ,
		'dog114.kr' : order_other ,
		'i-avec.com' : order_other ,
		'wconcept.co.kr' : order_other ,		
		'ai-doggi.com' : order_cafe24 ,
		'allieelf.com' : order_cafe24 ,
		'amor-ange.com' : order_cafe24 ,
		'arrr.kr' : order_cafe24 ,
		'babiana.co.kr' : order_cafe24 ,
		'barker-korea.com' : order_cafe24 ,
		'ba-ttang.com' : order_cafe24 ,
		'beatto.kr' : order_cafe24 ,
		'becomingstudio.com' : order_cafe24 ,
		'betterskorea.com' : order_cafe24 ,
		'bokseul.com' : order_cafe24 ,
		'boondog.co.kr' : order_cafe24 ,
		'bowbowpet.com' : order_cafe24 ,
		'bowwowmill.com' : order_cafe24 ,
		'bricbric.com' : order_cafe24 ,
		'bridge.dog' : order_cafe24 ,
		'buildapuppy.com' : order_cafe24 ,
		'burdog.co.kr' : order_cafe24 ,
		'bybong.com' : order_cafe24 ,
		'bymona.co.kr' : order_cafe24 ,
		'carmineproject.com' : order_cafe24 ,
		'charlie-market.com' : order_cafe24 ,
		'cherpetit.co.kr' : order_cafe24 ,
		'chloecolin.com' : order_cafe24 ,
		'choandkang.com' : order_cafe24 ,
		'cjgsfood1.cafe24.com' : order_cafe24 ,
		'clusterround.com' : order_cafe24 ,
		'cocasbin.com' : order_cafe24 ,
		'cocotail.co.kr' : order_cafe24 ,
		'cokemill.com' : order_cafe24 ,
		'comofranche.com' : order_cafe24 ,
		'coteacote.kr' : order_cafe24 ,
		'dalbampicnic.com' : order_cafe24 ,
		'ddasaroom.co.kr' : order_cafe24 ,
		'dfang.co.kr' : order_cafe24 ,
		'dogcook.co.kr' : order_cafe24 ,
		'dogshower.co.kr' : order_cafe24 ,
		'dogsnack.kr' : order_cafe24 ,
		'dongmongtable.com' : order_cafe24 ,
		'dontcrymypet.com' : order_cafe24 ,
		'double-comma.com' : order_cafe24 ,
		'drby.kr' : order_cafe24 ,
		'drmamma.net' : order_cafe24 ,
		'drmypet.co.kr' : order_cafe24 ,
		'dugroo.com' : order_cafe24 ,
		'elishop.co.kr' : order_cafe24 ,
		'esdog.co.kr' : order_cafe24 ,
		'eyoushop.co.kr' : order_cafe24 ,
		'flotshop.com' : order_cafe24 ,
		'foreverybari.com' : order_cafe24 ,
		'forpet.net' : order_cafe24 ,
		'fundlefarm.com' : order_cafe24 ,
		'handsdog.co.kr' : order_cafe24 ,
		'happypangpang.net' : order_cafe24 ,
		'holicarebarf.co.kr' : order_cafe24 ,
		'honestmeal.kr' : order_cafe24 ,
		'hutsandbay.com' : order_cafe24 ,
		'ig-apparel.com' : order_cafe24 ,
		'ilikedogcasual.com' : order_cafe24 ,
		'inherent.co.kr' : order_cafe24 ,
		'inuvivre.com' : order_cafe24 ,
		'its-sunnyoutside.com' : order_cafe24 ,
		'janggeumi.com' : order_cafe24 ,
		'j-o-yi.com' : order_cafe24 ,
		'kyeonsadol.co.kr' : order_cafe24 ,
		'laminarof.com' : order_cafe24 ,
		'likalika.kr' : order_cafe24 ,
		'littlecollin.kr' : order_cafe24 ,
		'lora.kr' : order_cafe24 ,
		'lottie.co.kr' : order_cafe24 ,
		'lovecoco.co.kr' : order_cafe24 ,
		'lovehotfit.com' : order_cafe24 ,
		'love-more.co.kr' : order_cafe24 ,
		'louisdogboutique.com' : order_cafe24 ,
		'naspapet.co.kr' : order_cafe24 ,
		'rudolphshop.kr' : order_cafe24 ,
		'u-n-pet.com' : order_cafe24 ,
		'magdog.co.kr' : order_cafe24 ,
		'maisondemiu.co.kr' : order_cafe24 ,
		'makemakit.com' : order_cafe24 ,
		'marlonshop.com' : order_cafe24 ,
		'merrypongo.com' : order_cafe24 ,
		'milliong.co.kr' : order_cafe24 ,
		'milloty.com' : order_cafe24 ,
		'monchouchou.co.kr' : order_cafe24 ,
		'munikund.com' : order_cafe24 ,
		'mypetmeat.com' : order_cafe24 ,
		'natress.ifupet.com' : order_cafe24 ,
		'needsthepet.com' : order_cafe24 ,
		'nixen.co.kr' : order_cafe24 ,
		'noashop.co.kr' : order_cafe24 ,
		'noutti.kr' : order_cafe24 ,
		'npmp.co.kr' : order_cafe24 ,
		'odd-pet.com' : order_cafe24 ,
		'ohdodog.com' : order_cafe24 ,
		'oneofus.co.kr' : order_cafe24 ,
		'opaaap.com' : order_cafe24 ,
		'parisdog.co.kr' : order_cafe24 ,
		'peppymeal.kr' : order_cafe24 ,
		'peppytail.com' : order_cafe24 ,
		'petcaresoap.com' : order_cafe24 ,
		'petdaddy.co.kr' : order_cafe24 ,
		'pethroom.com' : order_cafe24 ,
		'petpapa.co.kr' : order_cafe24 ,
		'pet-paradise.kr' : order_cafe24 ,
		'pets-plate.com' : order_cafe24 ,
		'petto.kr' : order_cafe24 ,
		'plushpuppykr.com' : order_cafe24 ,
		'pooch-dog.com' : order_cafe24 ,
		'project21.kr' : order_cafe24 ,
		'pupping.co.kr' : order_cafe24 ,
		'puppyangel.com' : order_cafe24 ,
		'puppyangel.co.kr' : order_cafe24 ,
		'pup-son.com' : order_cafe24 ,
		'raffinett.com' : order_cafe24 ,
		'riribubu.cafe24.com' : order_cafe24 ,
		'rorodog.com' : order_cafe24 ,
		'saltyhearty.com' : order_cafe24 ,
		'samdung2ne.com' : order_cafe24 ,
		'sectionkproject.com' : order_cafe24 ,
		'see-kitchen.com' : order_cafe24 ,
		'selectedpet.cafe24.com' : order_cafe24 ,
		'sempre-pet.com' : order_cafe24 ,
		'seoul-pet.com' : order_cafe24 ,
		'stroll.co.kr' : order_cafe24 ,
		'studioalive.co.kr' : order_cafe24 ,
		'studioaloitti.com' : order_cafe24 ,
		'su-su.kr' : order_cafe24 ,
		'sweetpet.co.kr' : order_cafe24 ,
		'tangleangel.co.kr' : order_cafe24 ,
		'terrylatte.com' : order_cafe24 ,
		'thesallyslaw.com' : order_cafe24 ,
		'totonroy.co.kr' : order_cafe24 ,
		'tustus.co.kr' : order_cafe24 ,
		'twoinplace.com' : order_cafe24 ,
		'ubuntu-korea.com' : order_cafe24 ,
		'uglugl.com' : order_cafe24 ,
		'urbanbeast.co.kr' : order_cafe24 ,
		'velynmore.com' : order_cafe24 ,
		'vemvem.com' : order_cafe24 ,
		'wefam.co.kr' : order_cafe24 ,
		'withtory.com' : order_cafe24 ,
		'wowdogshop.com' : order_cafe24 ,
		'xn--hw4ba51ra.com' : order_cafe24 ,
		'yasico.co.kr' : order_cafe24 ,
		'yolohollo.com' : order_cafe24 ,
		'youareapeach.co.kr' : order_cafe24 }
	
	
	
	'''	
	#
	# 로컬 테스트시 사용
	#
	#action_type = __ORDER_STATUS__
	
	action_type = __ORDER__
	
	LOG_NAME = "%s/ORDER/%s.%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]), action_type )
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	
	#brd_id_list = [ '21', '61', '63' ,'81', '89', '129', '159', '165', '215', '315']	# OTHER -- 테스트 완료 (0706)

	#brd_id_list = [ '1','4','11','12','13','20','22','34','49','59','68','83','85','87','90','96','98','100','101','112','114','116','117','118','121','123']	# CAFE24 -- 테스트 완료 (0706)
	
	#brd_id_list = [ '2', '28', '86', '97', '103', '134', '221', '233', '250', '251', '273', '278', '309', '323' ]	# GODO -- 테스트 완료 (0706)
	
	#brd_id_list = [ '84', '91', '95', '105','109','110','111','140','307','314','324','326' ]	# NAVER -- 테스트 완료 (0706)
	#brd_id_list = [ '314' ]	# NAVER -- html 안에 내용없음
	#brd_id_list = [ '24', '82' , '115', '130', '142', '154', '155', '157', '213', '301']	# MAKESHOP -- 테스트 완료 (0706)
	#brd_id_list = [ '15', '30' ,'64', '88', '92', '102', '113', '175', '185', '187', '254']	# IMWEB - 테스트 완료 (0706)
	#brd_id_list = [ '19', '119', '120', '163', '173', '188', '189', '205', '222']	# SIXSHOP - 테스트 완료 (0706)
	#brd_id_list = [ '93', '143']	# WISA - 테스트 완료 (0706)
	
	# naverpay
	#brd_id_list = [ '102',	'103',	'113',	'115',	'119',	'120',	'130',	'134',	'142',	'143' , '15',	'154',	'155',	'157',	'163',	'165',	'173',	'175',	'187',	'189',	'19',	'2' ,'205',	'213',	'215',	'22',	'24',	'250',	'251',	'254',	'278',	'28',	'301',	'315', '323',	'63',	'64',	'81',	'85',	'86',	'88',	'92',	'93',	'97']
	
	# 무통장 - brd_id_list = [ '124','125','127','128','131','132','135','136','137','138','139','14','146','147','148','149','150','151','153','156','16','160','164','167','168','17','171','172','177','178','179','180','181','182','186','191','196','29','306','31','311','316','322','35','36','37','39','41','46','48','75','77' ]	# CAFE24 second
	#brd_id_list = [ '124','125','127','128','131','132','135','136','137','138','139','14','146','147','148','149','150','151','153','156','16','160','164','167','168','17','171','172','177','178','179','180','181','182','186','191','196','29','306','31','311','316','322','35','36','37','39','41','46','48','69','75','77' ]	# CAFE24 second
	
	#brd_id_list = [ '179'] #-- 에러, html이 없음
	#brd_id_list = [ '29','306','31','311','316','322','35','36','37','39','41','46','48','75','77' ]
	
	#brd_id_list = [ '124', '127','128','131','132','135','136','137','138','139','14','146','147','148','149','150','151','153','156','16','160','164','167','168','17','171','172','177','178','179','180','181','182','186','191','196','29','306','31','311','316','322','35','36','37','39','41','46','48','75','77' ]
	#brd_id_list = [ '29', '35' ]
	
	#brd_id_list = [ '124', '127','128','131','132','135','136','137','138','139','14','146','147','148','149','150','151','153','156','16','160','164','167','168','17','171','172','177','178','179','180','181','182','186','191','196','29','306','31','311','316','322','35','36','37','39','41','46','48','75','77' ]
	#brd_id_list = [ '150' ] -- babiana.co.kr 주문결과 파일이 주문파일과 동일한것 같음..
	
	# npay
	#brd_id_list = [ '124','131','135','136','137','139','146','147','153','156','16','160','167','168','17','171','172','177','179','180','182','186','191','196','29','306','322','35','37','39','41','46','48','69']
	
	brd_id_list = [ '57', '64', '69', '94', '99', '104', '108', '125', '165', '176' ]
	brd_id_list = [ '165' ]
	
	for brd_id in brd_id_list :

		action_value =  int(brd_id)
		
		brd_url = __API__.get_storelist_by_brd_id( brd_id )
		__LOG__.Trace('---------------------------------------')
		#if(config.__DEBUG__) : 
		#	__LOG__.Trace('---------------------------------------')
		#	__LOG__.Trace('%d - %s' % ( int(brd_id), brd_url) )
		
		if(brd_url == '') :
			__LOG__.Trace('ERROR url : %s' % ( brd_id ) )
		else :
		
			split_list = brd_url.split('/')
			search_web_str = split_list[2].strip()
			
			if(search_web_str.startswith('www.')) : search_web_str = split_list[2].replace('www.','')
			elif(search_web_str.startswith('shop.')) : search_web_str = split_list[2].replace('shop.','')
			elif(search_web_str.startswith('m.')) : search_web_str = split_list[2].replace('m.','')
			
			if(config.__DEBUG__) : __LOG__.Trace('%d - %s ( %s )' % ( int(brd_id), brd_url, search_web_str) )
			
			#sel_file_list = ['무통장주문','npay주문']
			sel_file_list = ['무통장주문']
			
			for sel_file in sel_file_list :
				order_data = OrderData()
				order_status_data = OrderStatusData()
				
				order_data.brd_url = brd_url
				order_status_data.brd_url = brd_url
				
				order_data.search_web_str = search_web_str
				order_status_data.search_web_str = search_web_str
				
				order_data.action_value = action_value
				order_status_data.action_value = action_value
			
				order_file, orderstatus_file = get_file_name( brd_id, sel_file )
				if(order_file != '') :
					__LOG__.Trace('---------------------------------------------')

					#if(action_type == __ORDER__ ) : __LOG__.Trace( order_file )
					#else : __LOG__.Trace( orderstatus_file )
					
					order_data.brd_id = int( brd_id )
					order_status_data.brd_id = int( brd_id )
					
					order_data.cor_file_1 = order_file
					order_status_data.cos_file_1 = orderstatus_file

					#order_naver( action_type, order_data, order_status_data )
					order_math_func[search_web_str]( action_type, order_data, order_status_data )

					if(action_type == __ORDER__ ) : print_order_data( order_data )
					else : print_order_status_data( order_status_data )
					
	'''
		
	

	
	if(len( sys.argv ) != 3) :
		print("에러 : sys.argv != 3 ")
	else :
		if(sys.argv[1] != __ORDER__ ) and (sys.argv[1] != __ORDER_STATUS__ )  :
			print("에러 : sys.argv[1] != __ORDER__ and  sys.argv[1] != __ORDER_STATUS__  ")
		else :
		
			LOG_NAME = "%s/ORDER/%s.%s%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]), sys.argv[1], sys.argv[2] )
			Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))
	
			__LOG__.Trace("***********************************************************")
			__LOG__.Trace("Start ")
			__LOG__.Trace("***********************************************************")
			action_type = sys.argv[1]
			action_value =  int(sys.argv[2])	# cor_id 또는 cos_id

			#__LOG__.Trace("%s (%d) " % ( action_type, action_value))
			
			order_data = OrderData()
			order_status_data = OrderStatusData()
			
			brd_url = ''
			cor_pay_type = ''	# 일반 쇼핑몰에서 네이버 Pay로 결재시, 주문/주문결과 페이지가 Naver Pay 페이지로 넘어가는 것을 처리하기 위한 변수
			
			###########################################
			# action_type에 따른 API 값을 받아서, OrderData() / OrderStatusData() 값 초기화
			###########################################
			if(action_type == __ORDER__) : 
				__API__.get_order_html_file( action_value, order_data )
				brd_url = order_data.brd_url
				cor_pay_type = order_data.cor_pay_type
				
			elif(action_type == __ORDER_STATUS__) : 
				__API__.get_orderstatus_html_file( action_value, order_status_data )
				brd_url = order_status_data.brd_url
				cor_pay_type = order_status_data.cor_pay_type
			
			if(brd_url == '' ) :
				__LOG__.Trace("ERROR : value of brd_url is '' ")
			else :
				###########################################
				# brd_url를 갖고 분기하는 함수를 찾는 부분
				###########################################
				split_list = brd_url.split('/')
				search_web_str = split_list[2].strip()
				
				if(search_web_str.startswith('www.')) : search_web_str = split_list[2].replace('www.','')
				elif(search_web_str.startswith('shop.')) : search_web_str = split_list[2].replace('shop.','')
				elif(search_web_str.startswith('m.')) : search_web_str = split_list[2].replace('m.','')
				
				#if(config.__DEBUG__) : __LOG__.Trace('brd_url : %s ( %s )' % ( brd_url, search_web_str) )
				
				order_data.search_web_str = search_web_str
				order_status_data.search_web_str = search_web_str
				
				order_data.action_value = action_value
				order_status_data.action_value = action_value
				
				if( cor_pay_type == __NAVER_PAY__ ) : 
					# 일반 쇼핑몰에서 네이버 Pay로 결제시, 주문/주문결과 페이지가 Naver Pay 페이지로 넘어가는 것을 처리하기 위한 변수
					order_naver( action_type, order_data, order_status_data )
				else : 
					# 네이버 Pay로 미결제시
					order_math_func[search_web_str]( action_type, order_data, order_status_data )
				
				###########################################
				# API로 INSERT 또는 UPDATE 하는 부분
				###########################################
				if(action_type == __ORDER__) : 
					if(config.__DEBUG__) : print_order_data( order_data )
					if( order_data.cor_order_no != '' ) : __API__.insert_order( order_data )
					
				elif(action_type == __ORDER_STATUS__) : 
					if(config.__DEBUG__) : print_order_status_data( order_status_data )
					if( order_status_data.cos_order_no != '' ) : __API__.update_order( order_status_data )
			
			
			__LOG__.Trace("***********************************************************")
			__LOG__.Trace("Program End......")
			__LOG__.Trace("***********************************************************")
	
	
	