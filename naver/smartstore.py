#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2020. 5. 20.

@author: user
'''
import json
import time
import random
import os, datetime,re, signal
from datetime import date, timedelta

import bs4
import queue
import sys
import warnings
import requests
import datetime
from urllib import parse

import log as Log;  Log.Init()
from app import config
from app import define_mall as __DEFINE__


from util import Util as __UTIL__

from api import hiadone_api as __API__

from model.ProductData import ProductData
from mall.Mall import Mall

if not sys.warnoptions:
    warnings.simplefilter("ignore")

           
    
class smartstore(Mall) :    
        
	def __init__(self) :

		Mall.__init__(self)
		
		self.SITE_HOME = ''
		self.DISPLAY_LIST_COUNT = 40
		
		self.SPECIAL_CATEGORY = ''

		self.SMARTSTORE_CATEGORY_JSON = None
		
		self.SMARTSTORE_PRODUCT_CATEGORY_HASH = {}
	
	'''
	######################################################
	# Selenium 관련 함수
	######################################################
	'''
	

	
	def get_header(self):
	
		header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Sec-Fetch-Dest': 'document' , \
			'Sec-Fetch-Mode': 'navigate' , \
			'Sec-Fetch-Site': 'none' , \
			'Sec-Fetch-User': '?1' , \
			'Upgrade-Insecure-Requests': '1' , \
			'User-Agent': self.USER_AGENT } 

		return header
		
		
		
		
	def get_header_product_list(self, category_url):
	
		header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Referer': category_url , \
			'Sec-Fetch-Dest': 'document' , \
			'Sec-Fetch-Mode': 'same-origin' , \
			'Sec-Fetch-User': '?1' , \
			'Upgrade-Insecure-Requests': '1' , \
			'User-Agent': self.USER_AGENT } 

		return header
		
	
	
	def get_json_category(self, clevel, json_data) :
		'''
		######################################################################
		# 카테고리 리스트를 갖고 오는 부분
		nmp.registerModule(nmp.front.common.category_list, {
			"sCategoryId" : "",
			"sCategoryUrl" : "/miyongin/category/{=CATEGORY_ID}?cp={=CATEGORY_PAGE}",
			"sLayoutType" : "simple",
			"sCategoryType" : "standard",
			"aCategoryList" : [{"shopCategoryName":"화장품/미용","parentShopCategoryId":"0","level":1,"standardCategoryId":"50000002","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어케어","parentShopCategoryId":"b96c7a2709e2481fbf3f2924445bdd3e","level":2,"standardCategoryId":"50000198","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"샴푸","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000297","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"샴푸","displayCategoryId":"e1b1b23625cb4938b305ffa6d1759223","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"린스","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000298","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"린스","displayCategoryId":"6567b066217c4c008f549a62861770f5","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"트리트먼트","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000299","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"트리트먼트","displayCategoryId":"4bb069d4cefc460f918c103b49e1dd52","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어에센스","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000300","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어에센스","displayCategoryId":"30044c19b1c1440e8f93d779baba168c","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"탈모케어","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000304","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"탈모케어","displayCategoryId":"f1951fbe86fc4e909bdec081d5b5a2d1","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어팩","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000301","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어팩","displayCategoryId":"c9471f0a8ff04500a52bb1a8453fbd03","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어미스트","parentShopCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","level":3,"standardCategoryId":"50000302","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어미스트","displayCategoryId":"41a50ae13f6048b69a7023b179c26be2","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어케어","displayCategoryId":"ef9f8f97fc9b4c509d570f6e6376b603","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어스타일링","parentShopCategoryId":"b96c7a2709e2481fbf3f2924445bdd3e","level":2,"standardCategoryId":"50000199","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어왁스","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50000306","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어왁스","displayCategoryId":"6d561d4be3f0491a9320b464eb8a0fe4","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어스프레이","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50000307","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어스프레이","displayCategoryId":"52268f79fb55431fa2aa4bed7d5c3a17","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어젤","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50000309","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어젤","displayCategoryId":"68d2f1e50a314967a79be3770309a22c","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"염색약","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50000311","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"염색약","displayCategoryId":"27d8b970aa75473f8bfb2e715e6c7cca","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"파마약","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50001372","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"스트레이트","parentShopCategoryId":"3789a90d694a4b678c57b3a5634993d6","level":4,"standardCategoryId":"50004378","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"스트레이트","displayCategoryId":"bb2884d77de74506840331944cd8f842","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"웨이브","parentShopCategoryId":"3789a90d694a4b678c57b3a5634993d6","level":4,"standardCategoryId":"50004585","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"웨이브","displayCategoryId":"2b390473c673478ab10bc73b7be029c5","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"파마약","displayCategoryId":"3789a90d694a4b678c57b3a5634993d6","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어글레이즈","parentShopCategoryId":"3717d77b93774b818b045808f07c99d0","level":3,"standardCategoryId":"50000310","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어글레이즈","displayCategoryId":"c8625035892843eb9b9305adf0fd82c9","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어스타일링","displayCategoryId":"3717d77b93774b818b045808f07c99d0","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"뷰티소품","parentShopCategoryId":"b96c7a2709e2481fbf3f2924445bdd3e","level":2,"standardCategoryId":"50000201","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어소품","parentShopCategoryId":"b17ede44f0b04b3f9aadfe96694502e8","level":3,"standardCategoryId":"50001375","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어브러시","parentShopCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","level":4,"standardCategoryId":"50004396","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어브러시","displayCategoryId":"9e92486aaa5842fa9203c36ec760ca41","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"미용가위","parentShopCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","level":4,"standardCategoryId":"50004397","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"미용가위","displayCategoryId":"eb8860f4fc5047c0b321047aed78ffde","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어롤","parentShopCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","level":4,"standardCategoryId":"50004398","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어롤","displayCategoryId":"72bc7c3c43a24cfda46a3a39466790e1","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어캡","parentShopCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","level":4,"standardCategoryId":"50004400","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어캡","displayCategoryId":"6f9ef4eb8f184d1698df7eb8d36dcf24","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"기타헤어소품","parentShopCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","level":4,"standardCategoryId":"50004401","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"기타헤어소품","displayCategoryId":"dc96ba049ffd423982d231d333ba0143","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어소품","displayCategoryId":"9e79ad0d94c5495fb770b2581293ce3b","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"메이크업브러시","parentShopCategoryId":"b17ede44f0b04b3f9aadfe96694502e8","level":3,"standardCategoryId":"50001376","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"아이브러시","parentShopCategoryId":"fb4ad5dc07c0491294d4e99c29e1589e","level":4,"standardCategoryId":"50004587","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"아이브러시","displayCategoryId":"574b88ea06d1442fb69ae6039c1f8f56","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"메이크업브러시","displayCategoryId":"fb4ad5dc07c0491294d4e99c29e1589e","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"뷰티소품","displayCategoryId":"b17ede44f0b04b3f9aadfe96694502e8","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"화장품<span>/</span>미용","displayCategoryId":"b96c7a2709e2481fbf3f2924445bdd3e","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"디지털/가전","parentShopCategoryId":"0","level":1,"standardCategoryId":"50000003","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"이미용가전","parentShopCategoryId":"045280176641404f95e2c73a83e5977c","level":2,"standardCategoryId":"50000211","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"이미용가전액세서리","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001850","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"이미용가전액세서리","displayCategoryId":"93b4a8773a6d452687fd162f62fdf6ac","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"드라이어","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001986","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"드라이어","displayCategoryId":"b2e0dd2a6cac437e97a7cd660a047e1a","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"고데기","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001987","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"고데기","displayCategoryId":"ce17cad0007a405a88d1725345410656","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"매직기","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001988","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"매직기","displayCategoryId":"7720cc12b5574bb184241ecd5eb9fa83","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"에어브러시","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001989","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"에어브러시","displayCategoryId":"c2e9f4ac27774260befed1f2d920718b","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어롤/롤셋","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001990","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어롤<span>/</span>롤셋","displayCategoryId":"abf3eb52bb2f41f6be97b6b5e0cf15c0","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"이발기","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001997","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"이발기","displayCategoryId":"c41d5cf335e44fc5952aaf2b68707996","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"기타이미용가전","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001864","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"기타이미용가전","displayCategoryId":"7b705e548ce648769fcea853119a8799","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"눈썹정리기","parentShopCategoryId":"94c143f520e04a4a9ef0f98566f05822","level":3,"standardCategoryId":"50001992","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"눈썹정리기","displayCategoryId":"c62d08918bfc47059766c359f8c010a3","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"이미용가전","displayCategoryId":"94c143f520e04a4a9ef0f98566f05822","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"디지털<span>/</span>가전","displayCategoryId":"045280176641404f95e2c73a83e5977c","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"생활/건강","parentShopCategoryId":"0","level":1,"standardCategoryId":"50000008","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"반려동물","parentShopCategoryId":"22b924d20ccc490386d75c07bc1d02b9","level":2,"standardCategoryId":"50000155","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"강아지 미용/목욕","parentShopCategoryId":"264e2cd82ebf45a98ec574fc932cc3a6","level":3,"standardCategoryId":"50006662","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"이발기","parentShopCategoryId":"7891f556c50e48ffad7c91306e719487","level":4,"standardCategoryId":"50006666","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"이발기","displayCategoryId":"e9519828c24c43b8bc3de4c9f2ef87cf","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"강아지<span> </span>미용<span>/</span>목욕","displayCategoryId":"7891f556c50e48ffad7c91306e719487","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"반려동물","displayCategoryId":"264e2cd82ebf45a98ec574fc932cc3a6","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"생활<span>/</span>건강","displayCategoryId":"22b924d20ccc490386d75c07bc1d02b9","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"가구/인테리어","parentShopCategoryId":"0","level":1,"standardCategoryId":"50000004","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"침실가구","parentShopCategoryId":"cc3ad9100f824129ae0dd4028560fa47","level":2,"standardCategoryId":"50000100","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"거울","parentShopCategoryId":"62387204c1ca46ae8629790f258fbb65","level":3,"standardCategoryId":"50001232","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"손거울","parentShopCategoryId":"17f99658ad9b46b0a38bdf87ee7764d1","level":4,"standardCategoryId":"50003240","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"손거울","displayCategoryId":"5ce8c292fe9244f398c1a899308624cb","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"거울","displayCategoryId":"17f99658ad9b46b0a38bdf87ee7764d1","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"침실가구","displayCategoryId":"62387204c1ca46ae8629790f258fbb65","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"가구<span>/</span>인테리어","displayCategoryId":"cc3ad9100f824129ae0dd4028560fa47","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"패션잡화","parentShopCategoryId":"0","level":1,"standardCategoryId":"50000001","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어액세서리","parentShopCategoryId":"577725ca9bcf4ab39959eba0d8ff5e24","level":2,"standardCategoryId":"50000184","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"헤어핀","parentShopCategoryId":"06a70d2ebe5145f4804c7a1501641a43","level":3,"standardCategoryId":"50000561","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어핀","displayCategoryId":"8318ba832831496cbbfd40aaff4bfb46","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"헤어끈","parentShopCategoryId":"06a70d2ebe5145f4804c7a1501641a43","level":3,"standardCategoryId":"50000562","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어끈","displayCategoryId":"37ce53896e154b2f92e32926a5f7e481","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"가발","parentShopCategoryId":"06a70d2ebe5145f4804c7a1501641a43","level":3,"standardCategoryId":"50001478","imageUseYn":false,"subShopCategories":[{"shopCategoryName":"여성가발","parentShopCategoryId":"9937aee1f5d446eda6f2620df19abe79","level":4,"standardCategoryId":"50004009","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"여성가발","displayCategoryId":"7ff9078525c74ef2885e18ea100790e6","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"가발","displayCategoryId":"9937aee1f5d446eda6f2620df19abe79","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"헤어액세서리","displayCategoryId":"06a70d2ebe5145f4804c7a1501641a43","listImageHeight":0,"listImageUrl":null}],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"패션잡화","displayCategoryId":"577725ca9bcf4ab39959eba0d8ff5e24","listImageHeight":0,"listImageUrl":null},{"shopCategoryName":"전체상품","parentShopCategoryId":"0","level":1,"standardCategoryId":"ALL","imageUseYn":false,"subShopCategories":[],"supplementListImageUrl":null,"shopCategoryNameForDisplay":"전체상품","displayCategoryId":"ALL","listImageHeight":0,"listImageUrl":null}],
			"sImagePropertyParam" : "?type=m1000_1800",
			"nPage" : 1
		});
		######################################################################
		'''
		shopCategoryName = ''
		CategoryId = None
		standardCategoryId = None
		displayCategoryId = None
		parentShopCategoryId = ''
		level = ''
		subShopCategories_len = 0
		
		if('shopCategoryName' in json_data ) : shopCategoryName = json_data['shopCategoryName']
		if('standardCategoryId' in json_data ) : standardCategoryId = json_data['standardCategoryId'] 
		if('displayCategoryId' in json_data ) : displayCategoryId = json_data['displayCategoryId']
		CategoryId = standardCategoryId
		if( CategoryId == None ) : CategoryId = displayCategoryId
		if('subShopCategories' in json_data ) : subShopCategories_len = len(json_data['subShopCategories'] )
		if('parentShopCategoryId' in json_data ) : parentShopCategoryId = json_data['parentShopCategoryId'] 
		if('level' in json_data ) : level =  json_data['level'] 
		
		
		if( config.__DEBUG__ ) :
			__LOG__.Trace('-----------------------------------------------------------')
			__LOG__.Trace('카테고리명 : %s' % shopCategoryName )
			__LOG__.Trace('카테고리 Std ID : %s ' %  str(standardCategoryId ))
			__LOG__.Trace('카테고리 Dis ID : %s ' % str(displayCategoryId ))
			__LOG__.Trace('카테고리 Sel ID : %s ' % str(CategoryId ))
			__LOG__.Trace('하위카테고리 수 : %d ' % subShopCategories_len )
			__LOG__.Trace('상위카테고리 ID : %s ' % parentShopCategoryId )
			__LOG__.Trace('레벨 : %s ' % level )
		
		
		category_url = ''
		
		#if('subShopCategories' in json_data ) :  
		#	if( subShopCategories_len == 0) :
		
		if(self.SPECIAL_CATEGORY != '' ) :
			# 특정 카데고리에 대해서 찾을 때 사용.
			#
			if( CategoryId == self.SPECIAL_CATEGORY) or ( parentShopCategoryId == self.SPECIAL_CATEGORY) : category_url = '%s/category/%s?cp=1' % ( self.SITE_HOME, str(CategoryId) )

		else :
			# 전체 카데고리에 대해서 찾을 때 사용.
			#
			#if(CategoryId != 'ALL') and (CategoryId != '') and ( parentShopCategoryId != '0' ) : category_url = '%s/category/%s?cp=1' % ( self.SITE_HOME, str(CategoryId) )
			#if(CategoryId != 'ALL') and (CategoryId != '') : category_url = '%s/category/%s?cp=1' % ( self.SITE_HOME, str(CategoryId) )
			if(CategoryId != '') : category_url = '%s/category/%s?cp=1' % ( self.SITE_HOME, str(CategoryId) )
		
		if( category_url != '' ) :
			if(self.CATEGORY_URL_HASH.get(category_url , -1) == -1) and ( self.check_ignore_category_text(shopCategoryName) ) : 
				self.CATEGORY_URL_HASH[category_url] = shopCategoryName
				__LOG__.Trace('-----------------------------------------------------------')
				__LOG__.Trace('카테고리명 : %s' % shopCategoryName )
				__LOG__.Trace('카테고리 Sel ID : %s ' % str(CategoryId ))
					


				
	def get_category_data(self, html):
		
		rtn = False
		
		category_data = self.get_strip_string( html, 'nmp.registerModule(nmp.front.common.category_list,', ');' , [] )
		
		jsondata = json.loads(category_data)
		
		#if('sCategoryUrl' in jsondata) : __LOG__.Trace( jsondata['sCategoryUrl'] )
		if('aCategoryList' in jsondata) : 
			self.SMARTSTORE_CATEGORY_JSON = jsondata['aCategoryList']
			for category_level_1 in jsondata['aCategoryList'] :
				rtn = True
				self.get_json_category(1, category_level_1)
				if('subShopCategories' in category_level_1 ) : 
					for category_level_2 in category_level_1['subShopCategories'] :
						self.get_json_category(2, category_level_2)
						if('subShopCategories' in category_level_2 ) : 
							for category_level_3 in category_level_2['subShopCategories'] :
								self.get_json_category(3, category_level_3)
								if('subShopCategories' in category_level_3 ) : 
									for category_level_4 in category_level_3['subShopCategories'] :
										self.get_json_category(4, category_level_4)

		return rtn
		
		
		
	
	def process_category_list(self):

		__LOG__.Trace("********** process_category_list ***********")
		
		rtn = False
		resptext = ''
		
		try :
			self.CATEGORY_URL_HASH = None
			self.CATEGORY_URL_HASH = {}
			
			time.sleep(self.WAIT_TIME)
			
			URL = self.SITE_HOME
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_category_data( resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_category_list Error 발생 " )
			__LOG__.Error( ex )
			pass
		__LOG__.Trace("*************************************************")	
		
		return rtn
		
		
	'''
	######################################################################
	# 카테고리별로 페이지 URL을 얻는 함수
	######################################################################
	'''
	
	def get_page_data(self, category_url, html):
		rtn = False
		product_count = 0
		display_count = self.DISPLAY_LIST_COUNT
		
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		# 조회 물품수
		count_div_list = soup.find_all('div', class_='header_sub')
		for div_ctx in count_div_list :
			strong_list = div_ctx.find_all('strong', class_='num')
			for strong_ctx in strong_list :
				product_count = int( __UTIL__.get_only_digit( strong_ctx.get_text().strip() ) )
				__LOG__.Trace( 'TOTAL COUNT : %d ' % product_count )
		
		if( product_count == 0) :
			# 조회 물품수
			count_div_list = soup.find_all('span', class_='last_depth')
			for div_ctx in count_div_list :
				split_list = div_ctx.get_text().strip().split('(')
				cate_str = split_list[0].strip()
				strong_list = div_ctx.find_all('span', class_='thm')
				for strong_ctx in strong_list :
					strong_str = strong_ctx.get_text().strip()
					product_count = int( __UTIL__.get_only_digit(strong_str ))
					__LOG__.Trace( '%s - TOTAL COUNT : %d ' % (cate_str, product_count ) )
		
		# 화면상 표시하는 물품		
		sort_div_list = soup.find_all('select', {'name':'size'})
		for div_ctx in sort_div_list :
			option_list = div_ctx.find_all('option')
			for option_ctx in option_list :
				if('selected' in option_ctx.attrs ) : 
					display_count = int( option_ctx.attrs['value'] )
					#__LOG__.Trace( 'DISPLAY COUNT : %d ' % display_count )
					break
				
		split_data = category_url.split('?cp=')
		first_url = split_data[0]
		
		# 페이지 URL 생성
		page = 1
		while(True) :
			
			page_url = '%s?cp=1' % (first_url )
			if(page != 1) : page_url = '%s?page=%d&st=RECENT&dt=IMAGE&size=%d&free=false&cp=1' % (first_url , page , display_count )

			if(self.PAGE_URL_HASH.get(page_url , -1) == -1) : 
				self.PAGE_URL_HASH[page_url] = 1
				if(config.__DEBUG__) : __LOG__.Trace( page_url )
				rtn = True
			if( (page*display_count) < product_count ) : page += 1
			else : break

		return rtn 
		
		
		
	def process_page(self, category_url):
	
		rtn = False
		resptext = ''
		
		try :
			# 카테고리 URL로 첫 화면에서 페이지 리스트를 얻어옴.
			# 초기화
			#self.PAGE_FIRST_URL = ''		
			#self.PAGE_SECOND_URL = ''
			#self.PAGE_LAST_VALUE = 0
			
			#if( config.__DEBUG__ ) : __LOG__.Trace('page : %s' % ( category_url ) )
				
			time.sleep(self.WAIT_TIME)
			URL = category_url
			header = self.get_header_product_list(category_url)
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_page_data( category_url, resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_page Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
	def process_page_list(self):

		__LOG__.Trace("********** process_page_list ***********")
		
		rtn = False
		resptext = ''
		
		self.PAGE_URL_HASH = None
		self.PAGE_URL_HASH = {}
			
		for category_url in self.CATEGORY_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			self.process_page( category_url )
		
		if(config.__DEBUG__) : __LOG__.Trace( '페이지 수 : %d' % len(self.PAGE_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn	

		

	'''
	######################################################################
	# 상품 리스트 함수
	######################################################################
	'''
	
	def sub_search_category_depth(self, clevel, json_data, current_category_id, current_category_name) :
		rtn = False
		shopCategoryName = ''
		
		standardCategoryId = ''
		displayCategoryId = ''
		
		if('shopCategoryName' in json_data ) : shopCategoryName = json_data['shopCategoryName']
		if('standardCategoryId' in json_data ) : standardCategoryId = json_data['standardCategoryId']
		if('displayCategoryId' in json_data ) : displayCategoryId = json_data['displayCategoryId']
		
		if( shopCategoryName == current_category_name ) : 
			if( standardCategoryId == current_category_id ) or ( displayCategoryId == current_category_id ) : 
				rtn = True
		
		return rtn, shopCategoryName
		
	
	def search_category_depth(self, current_category_id, current_category_name) :
		rtn_category_name = ''
		category_level_1_name = ''
		category_level_2_name = ''
		category_level_3_name = ''
		
		for category_level_1 in self.SMARTSTORE_CATEGORY_JSON :
			rtn, category_name = self.sub_search_category_depth(1, category_level_1, current_category_id, current_category_name)
			if(rtn) :
				rtn_category_name = category_name
			else :
				category_level_1_name = category_name
				if('subShopCategories' in category_level_1 ) : 
					for category_level_2 in category_level_1['subShopCategories'] :
						rtn, category_name = self.sub_search_category_depth(2, category_level_2, current_category_id, current_category_name)
						if(rtn) :
							rtn_category_name = '%s|%s' % (category_level_1_name, category_name )
						else :
							category_level_2_name = category_name
							if('subShopCategories' in category_level_2 ) : 
								for category_level_3 in category_level_2['subShopCategories'] :
									rtn, category_name =  self.sub_search_category_depth(3, category_level_3, current_category_id, current_category_name)
									if(rtn) : 
										rtn_category_name = '%s|%s|%s' % (category_level_1_name, category_level_2_name, category_name )
									else :
										category_level_3_name = category_name
										if('subShopCategories' in category_level_3 ) : 
											for category_level_4 in category_level_3['subShopCategories'] :
												rtn, category_name = self.sub_search_category_depth(4, category_level_4, current_category_id, current_category_name)
												if(rtn) : rtn_category_name = '%s|%s|%s|%s' % (category_level_1_name, category_level_2_name, category_level_3_name, category_name )
												
		return 	rtn_category_name						
									

	def get_current_category(self, html ) :	
		#
		# 상품리스트 페이지에서 현재 카테고리 추출
		#
		# catnm_str : 현재의 카테고리

		current_category = ''
		
		try :
			

			current_category_id = self.get_strip_string( html, "_nao['catid'] =", ';' , ['"'] )
			current_category_name = self.get_strip_string( html, "_nao['catnm'] =", ';' , ['"'] )
			current_category = self.search_category_depth(current_category_id , current_category_name)
			
		except Exception as ex :
			__LOG__.Error(ex)
			pass
			
		return current_category
		
		
	def get_current_category_web(self, soup ) :	
		#
		# 상품리스트 페이지에서 현재 카테고리 추출
		#
		# catnm_str : 현재의 카테고리

		current_category = []
		
		try :
			category_div_list = soup.find_all('div', class_='module_breadcrumb' )
			for category_div_ctx in category_div_list :
				li_list = category_div_ctx.find_all('li', class_='item_breadcrumb' )
				for li_ctx in li_list :
					a_link = li_ctx.find('a')
					split_list = a_link.get_text().strip().split('(')
					now_cate = split_list[0].strip()
					if(now_cate != '') and (now_cate != '홈') : current_category.append( split_list[0].strip() )
			
			if(len(current_category) == 0 ) :
				category_div_list = soup.find_all('div', class_='_shopcategory_list' )
				for category_div_ctx in category_div_list :
					li_list = category_div_ctx.find_all('a', class_='path')
					for li_ctx in li_list :
						split_list = li_ctx.get_text().strip().split('(')
						now_cate = split_list[0].strip()
						if(now_cate != '') and (now_cate != '홈') : current_category.append( split_list[0].strip() )
						
					span_ctx = category_div_ctx.find('span', class_='path')
					if(span_ctx != None) :
						split_list = span_ctx.get_text().strip().split('(')
						now_cate = split_list[0].strip()
						if(now_cate != '') and (now_cate != '홈') : current_category.append( split_list[0].strip() )
			
		except Exception as ex :
			__LOG__.Error(ex)
			pass
			
		return '|'.join(current_category) 
		
	
	def set_current_category(self, product_data, current_category) :
		self.reset_product_category(product_data)
		
		category_depth_name = current_category.split('|')
		category_len = len(category_depth_name)
		
		if( category_len == 1 ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			
		elif( category_len == 2 ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			product_data.crw_category2 = category_depth_name[1].strip()
			
		elif( 3 == category_len ) :
			product_data.crw_category1 = category_depth_name[0].strip()
			product_data.crw_category2 = category_depth_name[1].strip()
			product_data.crw_category3 = category_depth_name[2].strip()
			
		elif( 4 == category_len ) :
			product_data.crw_category1 = category_depth_name[1].strip()
			product_data.crw_category2 = category_depth_name[2].strip()
			product_data.crw_category3 = category_depth_name[3].strip()
			
			
	
	def set_product_data(self, product_data, crw_post_url, current_category, li_ctx, product_ctx ) :
		
		try :
			
			####################################
			# 상품코드 추출
			####################################
			crw_goods_code_list = crw_post_url.split('/products/')
			crw_goods_code = crw_goods_code_list[1].strip()

			
			
			# 기존 상품정보가 입력되어 있을때 UPDATE Action 으로 변경.
			if(self.PRODUCT_ITEM_HASH.get(crw_goods_code, -1) != -1) : 
				product_data.crw_action = __DEFINE__.__UPDATE_CRW__
				product_data.crw_id = self.PRODUCT_ITEM_HASH[crw_goods_code]
				__LOG__.Trace( '%s - %s' % (crw_goods_code , product_data.crw_action ) )
			
			####################################
			# 상품명 추출
			####################################
			
			self.set_product_name( product_data, li_ctx )
			self.set_product_name( product_data , product_ctx )
			
			####################################
			# 상품가격 추출
			####################################
			
			self.set_product_price(product_data, li_ctx )
			self.set_product_price(product_data, product_ctx )
			
			if( product_data.crw_price == 0 ) : product_data.crw_price = product_data.crw_price_sale
			if( product_data.crw_price_sale == 0 ) : product_data.crw_price_sale = product_data.crw_price
			
			####################################
			# 품절여부 추출
			####################################
			
			self.set_product_soldout( product_data, li_ctx )
			self.set_product_soldout( product_data, product_ctx )
			
			####################################				
			# 상품 이미지 확인
			####################################
			div_list = product_ctx.find_all('div')
			for div_ctx in div_list :
				if('class' in div_ctx.attrs ) : 
					class_name_list = div_ctx.attrs['class']
					
					if(class_name_list[0].strip() == 'thumbnail') :
						# 이미지 추출
						product_img_ctx = div_ctx.find('img')
						if( product_img_ctx != None ) : 							
							if('data-src' in product_img_ctx.attrs ) :
								img_src_list = product_img_ctx.attrs['data-src'].split('?')
								product_data.product_img = img_src_list[0].strip()
								break

				
			product_data.brd_id = self.BRD_ID
			
			
			self.set_current_category( product_data, current_category)
			
			#product_data.crw_category1  = current_category

			product_data.crw_post_url = crw_post_url
			product_data.crw_goods_code  = crw_goods_code
			
			self.PRODUCT_URL_HASH[crw_post_url] = product_data
			self.PRODUCT_AVAIBLE_ITEM_HASH[product_data.crw_goods_code] = product_data.crw_id
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
	
	
	def set_product_data_second(self, product_data, crw_post_url, current_category, li_ctx, product_ctx ) :
		
		try :
			
			####################################
			# 상품코드 추출
			####################################
			crw_goods_code_list = crw_post_url.split('/products/')
			crw_goods_code = crw_goods_code_list[1].strip()

			
			
			# 기존 상품정보가 입력되어 있을때 UPDATE Action 으로 변경.
			if(self.PRODUCT_ITEM_HASH.get(crw_goods_code, -1) != -1) : 
				product_data.crw_action = __DEFINE__.__UPDATE_CRW__
				product_data.crw_id = self.PRODUCT_ITEM_HASH[crw_goods_code]
				__LOG__.Trace( '%s - %s' % (crw_goods_code , product_data.crw_action ) )
			
			####################################
			# 상품명 추출
			####################################

			self.set_product_name_second( product_data , product_ctx )
			
			####################################
			# 상품가격 추출
			####################################
			
			self.set_product_price_second(product_data, li_ctx )

			
			if( product_data.crw_price == 0 ) : product_data.crw_price = product_data.crw_price_sale
			if( product_data.crw_price_sale == 0 ) : product_data.crw_price_sale = product_data.crw_price
			
			####################################
			# 품절여부 추출
			####################################
			
			self.set_product_soldout_second( product_data, li_ctx )

			
			####################################				
			# 상품 이미지 확인
			####################################
			div_list = li_ctx.find_all('a', class_='N=a:lst.img')
			for div_ctx in div_list :
				# 이미지 추출
				product_img_ctx = div_ctx.find('img')
				if( product_img_ctx != None ) : 							
					if('src' in product_img_ctx.attrs ) :
						img_src_list = product_img_ctx.attrs['src'].split('?')
						product_data.product_img = img_src_list[0].strip()
						break

				
			product_data.brd_id = self.BRD_ID
			
			self.set_current_category( product_data, current_category)
			
			#product_data.crw_category1  = current_category
			product_data.crw_post_url = crw_post_url
			product_data.crw_goods_code  = crw_goods_code
			
			self.PRODUCT_URL_HASH[crw_post_url] = product_data
			self.PRODUCT_AVAIBLE_ITEM_HASH[product_data.crw_goods_code] = product_data.crw_id
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
	
	def set_product_name(self, product_data, ctx ) :
		
		try :
			
			if(product_data.crw_name == '') :
				# 상품명
				name_list = ctx.find_all('strong', class_='title')
				for name_ctx in name_list :
					if('title' in name_ctx.attrs ) : product_data.crw_name = name_ctx.attrs['title'].strip()
		
		except Exception as ex:
			__LOG__.Error(ex)
			pass
	
	def set_product_name_second(self, product_data, ctx ) :
		
		try :
			
			if(product_data.crw_name == '') :
				# 상품명
				if('title' in ctx.attrs ) : product_data.crw_name = ctx.attrs['title'].strip()
		
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
	def set_product_price(self, product_data, ctx ) :
		
		try :
			
			div_list = ctx.find_all('div' , class_='area_price')
			for div_ctx in div_list :
				# 가격 추출
				product_price_list = div_ctx.find_all('strong')
				for product_price_ctx in product_price_list :
					if('class' in product_price_ctx.attrs ) :
						class_name_list = product_price_ctx.attrs['class']
						if( len(class_name_list) == 1 ) and (class_name_list[0].strip() == 'price' ) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( product_price_ctx.get_text().strip() ) )
						elif(len(class_name_list) == 2 ) and (class_name_list[1].strip() == 'extend_cancel' ) : product_data.crw_price = int( __UTIL__.get_only_digit( product_price_ctx.get_text().strip() ) )
		
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
	def set_product_price_second(self, product_data, ctx ) :
		
		try :
			
			div_list = ctx.find_all('dd' , class_='price')
			for div_ctx in div_list :
				# 가격 추출
				product_price_list = div_ctx.find_all('span', class_='thm')
				for product_price_ctx in product_price_list :
					value_str = product_price_ctx.get_text().strip()
					if(0 <= value_str.find('판매가')) : product_data.crw_price = int( __UTIL__.get_only_digit( value_str ) )
					elif(0 <= value_str.find('할인가')) : product_data.crw_price_sale = int( __UTIL__.get_only_digit( value_str ) )

		
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
			
	def set_product_soldout(self, product_data, ctx ) :
		
		try :
			
			div_list = ctx.find_all('div', class_='area_status')
			for div_ctx in div_list :
				if(0 <= div_ctx.get_text().strip().find('일시품절')) : product_data.crw_is_soldout = 1
				if( product_data.crw_is_soldout == 0 ) :
					soldout_list = div_ctx.find_all('div')
					for soldout_ctx in soldout_list :
						if('title' in soldout_ctx.attrs) :
							if(soldout_ctx.attrs['title'].strip() == '일시품절') : product_data.crw_is_soldout = 1
						if('class' in soldout_ctx.attrs) :
							class_name_list = soldout_ctx.attrs['class']
							for class_name_str in class_name_list :
								if(class_name_str.strip() == 'soldout') : product_data.crw_is_soldout = 1
				
		
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
	
	def set_product_soldout_second(self, product_data, ctx ) :
		
		try :
			
			div_list = ctx.find_all('em', class_='soldout')
			for div_ctx in div_list :
				product_data.crw_is_soldout = 1
				
		
		except Exception as ex:
			__LOG__.Error(ex)
			pass

	
	def get_product_data_first(self, current_category, form_ctx ) :
		# <li class="item">
		# <a href="/aboutmeal/products/4891125789" class="N=a:lst.product area_overview">
		# <div class="thumbnail ">
		# <img src="https://shop-phinf.pstatic.net/20200414_224/1586829351177JaQ9P_JPEG/24190893802847365_135854332.jpg?type=f295_381" alt="어바웃밀 동결건조사료 비프레시피 400g" class="image img_full_h" onerror="this.onerror=null;this.src='https://img-shop.pstatic.net/storefarm/front/common/noimg/no_img_450x450.jpg'">                        </div>
		# <strong class="title" title="어바웃밀 동결건조사료 비프레시피 400g">어바웃밀 동결건조사료 비프레시피 400g</strong>
		# <div class="area_price">
		# <strong class="price"><span class="number">35,200</span><span class="currency">원</span></strong>
		# <strong class="price extend_cancel"><span class="number">44,000</span><span class="currency">원</span><span class="blind">취소</span></strong>
		# <strong class="price sale">20%<span class="blind">할인</span></strong>
		# </div>
		# </a>                        <div class="area_flag">
		# <div class="flag best"><span class="blind">베스트상품</span></div>
		# </div>
		# <div class="area_estimation">
		# <span class="label">리뷰</span>
		# <span class="count">11</span>
		# <span class="label">평점</span>
		# <span class="count">4.9<span class="slash">/</span>5</span>
		# </div>
		# <div class="area_status">
		# </div>
		# <a class="button_keep N=a:lst.mylist _click(nmp.front.sellershop.toggleKeep(4891125789)) _responsive_scrap_button _stopDefault" role="button" data-scrap-item-id="4891125789" aria-pressed="false" aria-label="찜하기" href="#" title="찜하기">찜하기 버튼</a>
		# <div class="area_button">
		# <a class="button keep N=a:lst.mylist2 _click(nmp.front.sellershop.toggleKeep(4891125789)) _responsive_scrap_button _stopDefault" role="button" data-scrap-item-id="4891125789" aria-pressed="false" aria-label="찜하기" href="#">찜하기 버튼</a>
		# <a class="button N=a:lst.simple _click(nmp.front.sellershop.openSimpleProduct(aboutmeal,4891125789,NORMAL)) _stopDefault more" role="button" href="##"><span class="blind">더보기</span></a>
		# </div>
		# </li>
		#__LOG__.Trace('get_product_data_first' )
		
		rtn = False	
		try :
			li_list = form_ctx.find_all('li', class_='item')
			#if(len(li_list) == 0 ) : li_list = form_ctx.find_all('li')
				
			for li_ctx in li_list :
				product_data = None
				product_link_list = li_ctx.find_all('a')
				for product_ctx in product_link_list :
					if('class' in product_ctx.attrs ) : 
						class_name_list = product_ctx.attrs['class']
						#__LOG__.Trace(class_name_list)
						if(0 == class_name_list[0].find('N=a:lst.product') ) or (0 == class_name_list[0].find('N=a:all.product') ) :
							
							if('href' in product_ctx.attrs ) : 
								href_str = product_ctx.attrs['href']
								if(10 < len(href_str) ) :
									# 상품 URL
									#__LOG__.Trace( product_ctx.attrs['href'] )
									crw_post_url = 'https://smartstore.naver.com%s' % product_ctx.attrs['href']

									#if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
									product_data = ProductData()
									
									# 기본 정보
									self.set_product_data( product_data, crw_post_url, current_category, li_ctx, product_ctx )

									self.process_product_api(product_data)
									
									rtn = True
										
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
		return rtn
			
	def get_product_data_second(self, current_category, form_ctx ) :
		# <li>
		# <div class="_mouseover(nmp.front.sellershop.showOverMenu()) _mouseout(nmp.front.sellershop.hideOverMenu()) thmb">
		# <div class="img_center"><a href="/barbichon/products/4501017106" class="N=a:lst.img"><img src="https://shop-phinf.pstatic.net/20190511_171/barbichonshop_1557551002749ANPth_JPEG/80858182392127711_1240488994.jpg?type=m120" alt="바비숑 티피하우스 엣지아이보리" onerror="this.onerror=null;this.src='https://img-shop.pstatic.net/storefarm/front/common/noimg/no_img_120x120.jpg'"></a></div>				<div class="ico_goods">
		# </div>
		# <span class="_over_menu over_menu" _item_key="89148101" style="display: none;">
		# <a href="#" class="_click(nmp.front.sellershop.openSimpleProduct(barbichon,4501017106,NORMAL)) _stopDefault frst
 		# N=a:lst.simple" title="간략보기">간략보기</a>
		# <a href="/barbichon/products/4501017106" class="N=a:lst.new" target="_blank" title="새창보기">새창보기</a>
		# </span>
		# </div>
		# <dl class="info">
		# <dt><a href="/barbichon/products/4501017106" title="바비숑 티피하우스 엣지아이보리" class="N=a:lst.title">바비숑 티피하우스 엣지아이보리</a>
		# <a href="#" role="button" data-scrap-item-id="4501017106" class="_responsive_scrap_button _click(nmp.front.sellershop.toggleKeep(4501017106)) _stopDefault scrap N=a:lst.mylist" title="찜하기">
		# 찜하기
		# </a>
		# </dt>
		# <dd class="prm"></dd>
		# <dd class="cate">			<a href="/barbichon/category/fecdd543d8d243d7ba9c65dec77e42ac">하우스</a>
		# </dd>
		# <dd class="price">		<strong><span class="thm"><span class="blind">판매가 </span>77,000</span>원</strong>
		# <span class="ico_goods2">	<em title="일시품절" class="soldout"><span class="png24">일시품절</span></em>
		# </span></dd>
		# </dl>
		# <div class="side_area">
		# <div class="addit_info">
		# <p>	<a href="#" class="info_item _sellershop_product_review_count _stopDefault">리뷰
		# <span class="fc_point thm">3</span>
		# </a>
		# <span class="info_item">평점<span class="fc_point thm">4.7</span><span class="slash">/</span><span class="fc_point thm">5</span></span>
		# </p>
		# <p></p>
		# </div>
		# <ul class="benefit">
		# <li title="">무료배송</li>
		# <li title="포인트 최대 150원">포인트</li>
		# </ul>
		# </div>
		# </li>
		#__LOG__.Trace('get_product_data_second' )
		
		rtn = False	
		try :
			ul_list = form_ctx.find_all('ul', class_='lst')
			for ul_ctx in ul_list :
				li_list = ul_ctx.find_all('li')
				for li_ctx in li_list :
					product_data = None
					product_link_list = li_ctx.find_all('a')
					for product_ctx in product_link_list :
						if('class' in product_ctx.attrs ) : 
							class_name_list = product_ctx.attrs['class']
							#__LOG__.Trace(class_name_list)
							if(0 == class_name_list[0].find('N=a:lst.title') ) :
								
								if('href' in product_ctx.attrs ) : 
									href_str = product_ctx.attrs['href']
									if(10 < len(href_str) ) :
										# 상품 URL
										#__LOG__.Trace( product_ctx.attrs['href'] )
										crw_post_url = 'https://smartstore.naver.com%s' % product_ctx.attrs['href']

										#if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
										product_data = ProductData()
										
										# 기본 정보
										self.set_product_data_second( product_data, crw_post_url, current_category, li_ctx, product_ctx )

										self.process_product_api(product_data)
										
										rtn = True
										
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
		return rtn
		
		
	
	def get_product_data(self, html):
	
		rtn = False	
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		current_category = self.get_current_category_web(soup)
		 
		if(current_category == '') : current_category = self.get_current_category(html)
		
		form_list = soup.find_all('form', class_='_list_form')

		if(len(form_list) == 0 ) : 
			# 아래 사이트의 경우
			# https://smartstore.naver.com/smallbatch
			form_list = soup.find_all('form', class_='_wholeproduct_form')
			
		for form_ctx in form_list :
			try :

				rtn = self.get_product_data_first(current_category, form_ctx )
				if(rtn == False ) :
					rtn = self.get_product_data_second(current_category, form_ctx )
				
				
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		return rtn


		
	'''
	def get_product_data(self, html):
	
		rtn = False	
		soup = bs4.BeautifulSoup(html, 'lxml')
		
		current_category = self.get_current_category(html)
		
		form_list = soup.find_all('form', class_='_list_form')

		for form_ctx in form_list :
			try :
				
				
				li_list = form_ctx.find_all('li', class_='item')
				for li_ctx in li_list :
					product_data = None
					product_link_list = li_ctx.find_all('a')
					for product_ctx in product_link_list :
						
						if('class' in product_ctx.attrs ) : 
							class_name_list = product_ctx.attrs['class']
							#__LOG__.Trace(class_name_list)
							if(0 == class_name_list[0].find('N=a:lst.product') ) :
								
								if('href' in product_ctx.attrs ) : 
									href_str = product_ctx.attrs['href']
									if(10 < len(href_str) ) :
										# 상품 URL
										#__LOG__.Trace( product_ctx.attrs['href'] )
										crw_post_url = 'https://smartstore.naver.com%s' % product_ctx.attrs['href']

										if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
											product_data = ProductData()
											
											# 기본 정보
											self.set_product_data( product_data, crw_post_url, current_category, li_ctx, product_ctx )

											self.process_product_api(product_data)
											
											rtn = True
						
				#
				# <li class="item">
	<a href="/aboutmeal/products/4891125789" class="N=a:lst.product area_overview">
                        <div class="thumbnail ">
<img src="https://shop-phinf.pstatic.net/20200414_224/1586829351177JaQ9P_JPEG/24190893802847365_135854332.jpg?type=f295_381" alt="어바웃밀 동결건조사료 비프레시피 400g" class="image img_full_h" onerror="this.onerror=null;this.src='https://img-shop.pstatic.net/storefarm/front/common/noimg/no_img_450x450.jpg'">                        </div>
                            <strong class="title" title="어바웃밀 동결건조사료 비프레시피 400g">어바웃밀 동결건조사료 비프레시피 400g</strong>
                            <div class="area_price">
			<strong class="price"><span class="number">35,200</span><span class="currency">원</span></strong>
			<strong class="price extend_cancel"><span class="number">44,000</span><span class="currency">원</span><span class="blind">취소</span></strong>

<strong class="price sale">20%<span class="blind">할인</span></strong>
                            </div>
                            
</a>                        <div class="area_flag">
<div class="flag best"><span class="blind">베스트상품</span></div>

                        </div>
<div class="area_estimation">
	<span class="label">리뷰</span>
	<span class="count">11</span>
	<span class="label">평점</span>
	<span class="count">4.9<span class="slash">/</span>5</span>
</div>
                        <div class="area_status">
                        </div>
<a class="button_keep N=a:lst.mylist _click(nmp.front.sellershop.toggleKeep(4891125789)) _responsive_scrap_button _stopDefault" role="button" data-scrap-item-id="4891125789" aria-pressed="false" aria-label="찜하기" href="#" title="찜하기">찜하기 버튼</a>
                        <div class="area_button">
<a class="button keep N=a:lst.mylist2 _click(nmp.front.sellershop.toggleKeep(4891125789)) _responsive_scrap_button _stopDefault" role="button" data-scrap-item-id="4891125789" aria-pressed="false" aria-label="찜하기" href="#">찜하기 버튼</a>
<a class="button N=a:lst.simple _click(nmp.front.sellershop.openSimpleProduct(aboutmeal,4891125789,NORMAL)) _stopDefault more" role="button" href="##"><span class="blind">더보기</span></a>
                        </div>
                </li>
				#
				
			except Exception as ex:
				__LOG__.Error(ex)
				pass
		
		return rtn
	'''
				
		
	def process_product(self, page_url):
	
		rtn = False
		resptext = ''
		
		try :
		
			if( config.__DEBUG__ ) :
				__LOG__.Trace('page : %s' % ( page_url ) )
				
			time.sleep(self.WAIT_TIME)
			URL = page_url
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_product_data( resptext )
			
		except Exception as ex:
			__LOG__.Error( "process_product Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		return rtn
		
		
		
	def process_product_list(self):

		__LOG__.Trace("********** process_product_list ***********")
		
		rtn = False
		resptext = ''
		
		self.PRODUCT_URL_HASH = None
		self.PRODUCT_URL_HASH = {}
			
		for page_url in self.PAGE_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			self.process_product( page_url )
		
		if(config.__DEBUG__) : __LOG__.Trace( '총 물품 수 : %d' % len(self.PRODUCT_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn			
				

	######################################################################
	#
	# 상품 상세 페이지
	#
	######################################################################
	
		
	def get_product_detail_notice_table(self, table_list , product_data) :
		#
		# 상세페이지 내용중 - 상품정보 테이블 정보
		#
		rtn_dict = self.get_value_in_table_two_colume(table_list, '상품 기본정보', 'th', 'td')
		for key in rtn_dict.keys() :
			if(key == '제조사') : 
				if( product_data.crw_brand2 == '') : product_data.d_crw_brand2 = rtn_dict[key]
			elif(key == '브랜드') : 
				if( product_data.crw_brand1 == '') : product_data.d_crw_brand1 = rtn_dict[key]
			elif(key == '원산지') : 
				if( product_data.crw_brand3 == '') : product_data.d_crw_brand3 = rtn_dict[key]

				
	def get_product_detail_notice_two_table(self, table_list , product_data) :
		#
		# 상세페이지 내용중 - 상품정보제공공시 테이블 정보
		#		
		rtn_dict = self.get_value_in_table(table_list, '상품정보 리스트', 'th', 'td', 0)
		for key in rtn_dict.keys() :
			rtn_value = rtn_dict[key]
			if(rtn_value.find('상품상세 참조') < 0 ) :
				if(key == '제조국') : 
					if( product_data.crw_brand3 == '') : product_data.d_crw_brand3 = rtn_value
				elif(key == '제조업자') : 
					if( product_data.crw_brand2 == '') : product_data.d_crw_brand2 = rtn_value
				elif(key == '제조판매업자') : 
					if( product_data.crw_brand4 == '') : product_data.d_crw_brand4 = rtn_value


	
	
	
	def get_product_detail_data(self, product_data, html):
		'''
		# < 상품명 / 상품번호 / 카테고리 부분 >
		# 		
		_nao['mid'] = "510298578";
		_nao['chno'] = "100320832";
		_nao['mtyp'] = "STF";
		_nao['vtyp'] = "DET";

		_nao['pid'] = "4039468610";
		_nao['pnm'] = "하이포닉 고양이, 강아지 워터리스 샴푸 190ml";
		_nao['lcatid'] = "50000008";
		_nao['lcatnm'] = "생활/건강";
		_nao['mcatid'] = "50000155";
		_nao['mcatnm'] = "반려동물";
		_nao['scatid'] = "50006662";
		_nao['scatnm'] = "강아지 미용/목욕";
		_nao['dcatid'] = "50006663";
		_nao['dcatnm'] = "샴푸/린스/비누";
		#
		#	< 가격 >
		nmp.registerModule(nmp.front.sellershop.product.calculator, {
			"bSubscriberOnly" : false,
			"bStoreZzimProduct" : false,
			"aCombinationGroupName" : [],
			"aCombinationOption" : [],
			"sOptionSortType" : "",
			"bCombinationOption" : false,
			"bStandardOption" : false,
			"nBasicPrice" : 18000,
			"nSalePrice" : 18000,
			"nProductId" : 4039468610,
			"nChannelNo" : "100320832",
			"nMinPurchaseQuantity" : 1,
			"bSingleUnit" : true,
			"supplementData" : {},
			"singleType" : "SINGLE_UNIT",
			"optionType" : "OPTION_PRODUCT",
			"combinationType" : "PRICING_OPTION_PRODUCT",
			"supplementType" : "SUPPLEMENT_PRODUCT",
			"ELEMENT_TYPE_CUSTOM" : "CUSTOM",
			"ELEMENT_TYPE_OPTION" : "OPTION",
			"ELEMENT_TYPE_COMBINATION" : "COMBINATION",
			"ELEMENT_TYPE_SUPPLEMENT" : "SUPPLEMENT",
			"ELEMENT_TYPE_STANDARD" : "STANDARD",
			"bPreview" : false
		});
		
		< 품절 부분 체크 >
		<script type="application/ld+json">
			{"name":"하이포닉 고양이, 강아지 워터리스 샴푸 190ml : 하이포닉","description":"[하이포닉] 하이포닉 본사 온라인몰입니다.","image":"https://shop-phinf.pstatic.net/20200220_253/1582159075364hCx1d_PNG/19522463889608946_2131709101.png?type=o640","sku":100288682,"mpn":4039468610,"productID":4039468610,"category":"생활/건강>반려동물>강아지 미용/목욕>샴푸/린스/비누","offers":{"price":18000,"priceCurrency":"KRW","availability":"http://schema.org/InStock","url":"https://smartstore.naver.com/hyponic/products/4039468610","@type":"Offer"},"@context":"http://schema.org","@type":"Product"}
		</script>

		< 상세 페이지 텍스트 및 이미지 >
		nmp.registerModule(nmp.front.sellershop.product.show.detail_info, {
				sAuthenticationType : "NORMAL",
				bSeOne : true,
				pcHtml : "<div id=\"SEDOC-1578557436135--2108069652\" class=\"se_doc_viewer se_body_wrap se_theme_transparent \" data-docversion=\"1.0\">\n<div class=\"se_doc_header_start\" id=\"SEDOC-1578557436135--2108069652_se_doc_header_start\"><\/div>\n\x3C!-- SE_DOC_HEADER_START --\>\n<div id=\"SEDOC-1578557436135--2108069652_viewer_head\" class=\"se_viewer_head\"><\/div>\n<div class=\"se_component_wrap\">\n<\/div>\n\n\x3C!-- SE_DOC_HEADER_END --\>\n<div class=\"se_doc_header_end\" id=\"SEDOC-1578557436135--2108069652_se_doc_header_end\"><\/div>\n<div class=\"se_doc_contents_start\" id=\"SEDOC-1578557436135--2108069652_se_doc_contents_start\"><\/div>\n\x3C!-- SE_DOC_CONTENTS_START --\>\n<div class=\"se_component_wrap sect_dsc __se_component_area\">\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\">\x3C!-- SE3-TEXT { --\><span><br><\/span><span><br><\/span><span><\/span>\x3C!-- } SE3-TEXT --\><\/p>\n                    <\/div>\n                <\/div>\n            <\/div>\n        <\/div>\n    <\/div>\n<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_0_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/01.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_0_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wMS5qcGc=?token=072b3b80260a1c5b7cefc0458534c79a\" width=\"860\" height=\"856\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_1_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/02.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_1_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wMi5qcGc=?token=fa358086f92375910f7e255210dc939e\" width=\"860\" height=\"969\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_2_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/03.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_2_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wMy5qcGc=?token=c7f15b3babd2ded928ca1e3d7f8f9f99\" width=\"860\" height=\"1072\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_3_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/04.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_3_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wNC5qcGc=?token=6027af08115b29643861408c7930dc65\" width=\"860\" height=\"1558\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_4_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/05.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_4_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wNS5qcGc=?token=9f1316ff887838463bf0a8ec5260b15d\" width=\"860\" height=\"2963\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_5_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/06.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_5_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wNi5qcGc=?token=71bcd455d56a97936aa0c76d1736785e\" width=\"860\" height=\"1144\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_6_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/07.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_6_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wNy5qcGc=?token=9faa47c35d9529aa53a7033d7cb636cc\" width=\"860\" height=\"1886\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_7_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/08.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_7_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wOC5qcGc=?token=52d93761616af7dfda6a720f2565162f\" width=\"860\" height=\"2395\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_8_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/09.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_8_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8wOS5qcGc=?token=e7dbba133815bd0c0c03d54a95249b9f\" width=\"860\" height=\"1349\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:860px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1578557436135--2108069652_image_9_img&quot;,&quot;src&quot;:&quot;http://hyponic.co.kr/bizdemo52442/img/main/detail/A11/10.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1578557436135--2108069652_image_9_img\" class=\"se_mediaImage __se_img_el\" src=\"https://proxy.smartstore.naver.com/img/aHlwb25pYy5jby5rci9iaXpkZW1vNTI0NDIvaW1nL21haW4vZGV0YWlsL0ExMS8xMC5qcGc=?token=d8f9214deda00d156e1f7429e4b6461f\" width=\"860\" height=\"1093\" data-attachment-id=\"\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\">\x3C!-- SE3-TEXT { --\>\x3C!-- } SE3-TEXT --\><\/p>\n                    <\/div>\n                <\/div>\n            <\/div>\n        <\/div>\n    <\/div>\n<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n<\/div>\n\x3C!-- SE_DOC_CONTENTS_END --\>\n<div class=\"__se_doc_title_end\" id=\"se_doc_contents_end\"><\/div>\n<div id=\"SEDOC-1578557436135--2108069652_se_doc_footer\" class=\"se_doc_footer\"><\/div>\n<\/div>\n"
			});
		'''
		
		rtn = False
		try :


			soup = bs4.BeautifulSoup(html, 'lxml')
			div_list = soup.select('#wrap > div > div.prd_detail_common')
			
			for div_ctx in div_list :
				table_list = div_ctx.find_all('table')
				# 상품정보
				self.get_product_detail_notice_table( table_list , product_data)
				
				# 상품정보제공공시
				self.get_product_detail_notice_two_table( table_list , product_data)
			
			
			#
			# 상세 페이지 이미지 및 텍스트 추출
			self.get_detail_img_text_data(product_data, html)	
				
			
			rtn = True
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		return rtn
		
	
	def process_product_detail(self, product_url, product_data):
	
		rtn = False
		resptext = ''
		
		try :
			__LOG__.Trace("-----------------------------------------------------")
			if( config.__DEBUG__ ) : __LOG__.Trace('product : %s' % ( product_url ) )
				
			time.sleep(self.WAIT_TIME*2)
			URL = product_url
			header = self.get_header()
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(resp.status_code)
			else :
				resptext = resp.text
				rtn = self.get_product_detail_data( product_data, resptext )
				
				self.process_product_detail_api(product_data)
				
		except Exception as ex:
			__LOG__.Error( "process_product_detail Error 발생 " )
			__LOG__.Error( ex )
			pass
		
		self.PRODUCT_URL_HASH[product_url] = product_data
		
		return rtn	
		



	def get_detail_img_text_data(self, product_data, html):
		#
		#
		# 상세페이지 부분에서 텍스트 와 이미지 갖고 오기
		#
		#nmp.registerModule(nmp.front.sellershop.product.show.detail_info, {
		#	sAuthenticationType : "NORMAL",
		#	bSeOne : true,
		#	pcHtml : "<div id=\"SEDOC-1567414677093--1045529342\" class=\"se_doc_viewer se_body_wrap se_theme_transparent \" data-docversion=\"1.0\">\n<div class=\"se_doc_header_start\" id=\"SEDOC-1567414677093--1045529342_se_doc_header_start\"><\/div>\n\x3C!-- SE_DOC_HEADER_START --\>\n<div id=\"SEDOC-1567414677093--1045529342_viewer_head\" class=\"se_viewer_head\"><\/div>\n<div class=\"se_component_wrap\">\n<\/div>\n\n\x3C!-- SE_DOC_HEADER_END --\>\n<div class=\"se_doc_header_end\" id=\"SEDOC-1567414677093--1045529342_se_doc_header_end\"><\/div>\n<div class=\"se_doc_contents_start\" id=\"SEDOC-1567414677093--1045529342_se_doc_contents_start\"><\/div>\n\x3C!-- SE_DOC_CONTENTS_START --\>\n<div class=\"se_component_wrap sect_dsc __se_component_area\">\n    \n\n\n\n\n\n\n\n\n\n\n\n<div class=\"se_component se_sectionTitle \">\n    <div class=\"se_sectionArea se_align-center\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_H3 se_fw_bold\" style=\"color: #272727;\n                        text-decoration: inherit;\n                        font-style: inherit;\n                        \">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <h6 class=\"se_textarea\">\x3C!-- SE3-TEXT { --\>\x3C!-- } SE3-TEXT --\><\/h6>\n                    <\/div>\n                <\/div>\n            <\/div>\n        <\/div>\n    <\/div>\n<\/div>\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\">\x3C!-- SE3-TEXT { --\><br><span><\/span><br><span><\/span><br><span><\/span>\x3C!-- } SE3-TEXT --\><\/p>\n                    <\/div>\n                <\/div>\n            <\/div>\n        <\/div>\n    <\/div>\n<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:808px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1567414677093--1045529342_image_0_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20190902_109/15674146715070nGl7_JPEG/%BA%A3%B8%AE%C6%CE%B0%A1%B5%F0%B0%C7-%B1%D7%B8%B0_%BB%F3%BC%BC%C6%E4%C0%CC%C1%F6.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1567414677093--1045529342_image_0_img\" class=\"se_mediaImage __se_img_el\" src=\"https://shop-phinf.pstatic.net/20190902_109/15674146715070nGl7_JPEG/%BA%A3%B8%AE%C6%CE%B0%A1%B5%F0%B0%C7-%B1%D7%B8%B0_%BB%F3%BC%BC%C6%E4%C0%CC%C1%F6.jpg\" width=\"808\" height=\"14500\" data-attachment-id=\"Ip65Z4qze2b-E0dhIlTZ2ir4y5fo\" alt=\"\">\n        \n        <\/a>\n\t\t\t\t\t<\/div>\n\t\t\t\t<\/div>\n\t\t\t<\/div>\n\t\t<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\">\x3C!-- SE3-TEXT { --\><span><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span><br><\/span><span class=\"se_fs_T2\"><br><\/span><span><br><\/span><span><\/span><br><span><br><\/span><span><br><\/span><span><br><\/span><span><\/span>\x3C!-- } SE3-TEXT --\><\/p>\n                    <\/div>\n                <\/div>\n            <\/div>\n        <\/div>\n    <\/div>\n<\/div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n<\/div>\n\x3C!-- SE_DOC_CONTENTS_END --\>\n<div class=\"__se_doc_title_end\" id=\"se_doc_contents_end\"><\/div>\n<div id=\"SEDOC-1567414677093--1045529342_se_doc_footer\" class=\"se_doc_footer\"><\/div>\n<\/div>\n"
		#});
		#
		
		ignore_str = 'nmp.registerModule(nmp.front.sellershop.product.show.detail_info,'
		del_pos = html.find(ignore_str)
		
		if(0 < del_pos):
			ignore_pos = html.find(ignore_str) + len( ignore_str )
			last_pos = html[ignore_pos:].find('});')
			
			category_data = html[ignore_pos:ignore_pos+last_pos].strip() 

			text_list = category_data.split('pcHtml : "')

			if(len(text_list) == 2) : 
				
				#inner_html = text_list[1].replace('\\n"','' ).replace('\\n','\n' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','\t' ).replace('&quot;',' ' ).replace('\\x3C!','<!').replace('\\>','>').strip()
				#inner_html = text_list[1].replace('\\n"','' ).replace('\\n','' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','\t' ).replace('&quot;',' ' ).replace('\\x3C!','<!').replace('\\>','>').strip()
				inner_html = text_list[1].replace('\\n"','' ).replace('\\n','\n' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','' ).replace('&quot;',' ' ).replace('\\xa0!',' ').replace('\\x3C!','<!').replace('\\>','>').strip()
				
				html = '''<html lang="ko"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
						<body>''' + inner_html + '''</body></html>'''
						

				soup = bs4.BeautifulSoup(html, 'lxml')
				detail_content_list = soup.select('html > body > div')
				if(len(detail_content_list) == 0 ) : detail_content_list = soup.select('html > body')
				detail_page_txt = []
				detail_page_img = []
				
				for detail_content_ctx in detail_content_list :
					content_text = detail_content_ctx.get_text().strip()
					
					if( 0 < len(content_text) ) :
						rtn_str = self.get_detail_text_with_strip( content_text )
						detail_page_txt.append( rtn_str )
					
					
					# 순수한 이미지 요소 추출
					img_list = detail_content_ctx.find_all('img')
					for img_ctx in img_list :
						if('src' in img_ctx.attrs) : 
							img_src = img_ctx.attrs['src']
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							#if(0 != img_link.find('https://proxy.smartstore.naver.com/') ) : detail_page_img.append( self.get_hangul_url_convert( img_link )  )
							detail_page_img.append( self.get_hangul_url_convert( img_link )  )
							
					# 링크와 같이 있는 이미지 요소 추출
					img_list = detail_content_ctx.find_all('a', {'data-linktype':'img'})
					for img_ctx in img_list :
						if('data-linkdata' in img_ctx.attrs) : 
							img_text = img_ctx.attrs['data-linkdata']
							img_text_list = img_text.split(', src :')
							if(len(img_text_list) == 2) :
								tmp_img_list = img_text_list[1].strip().split(',')
								img_src = tmp_img_list[0].strip()
								img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
								#if(0 != img_link.find('https://proxy.smartstore.naver.com/') ) : detail_page_img.append( self.get_hangul_url_convert( img_link )  )
								detail_page_img.append( self.get_hangul_url_convert( img_link )  )


				self.set_detail_page( product_data, detail_page_txt, detail_page_img)
				
				
	'''
	######################################################################
	# 메인 함수
	######################################################################
	''' 
	

		
	
	def main(self, site_home, brd_id):

		__LOG__.Trace("***********************************************************")
		__LOG__.Trace("Start (%s) %s ....." % ( str(brd_id) ,site_home) )
		__LOG__.Trace("***********************************************************")
		
		try :
			if(0 < site_home.find('/products/') ) :
				__LOG__.Trace("특정 product URL에 대해서는 상품정보를 얻을수 없습니다.")
			else :
				self.init_mall(brd_id)
				
				if(0 < site_home.find('/category/') ) :
					# 특정 카테고리만 지정하는 경우
					split_data = site_home.split('/category/')
					self.set_site_home( split_data[0] )
					
					cateogory_list = split_data[1].split('?')
					self.SPECIAL_CATEGORY = cateogory_list[0].strip()
					self.CATEGORY_URL_HASH = None
					self.CATEGORY_URL_HASH = {}
					self.CATEGORY_URL_HASH[site_home] = ''
				else : 
					# 전체 카테고리 경우
					self.set_site_home( site_home )
					# 전체 카테고리 리스트 갖고 오기
					self.process_category_list()
				
					#
					# https://smartstore.naver.com//smallbatch 처럼 카테고리가 없을때
					if(len(self.CATEGORY_URL_HASH) == 0 ) : 
						self.CATEGORY_URL_HASH[site_home] = ''
					else :
						all_category = '%s/category/ALL?cp=1' % (site_home)
						if(self.CATEGORY_URL_HASH.get(all_category, -1) == -1) : self.CATEGORY_URL_HASH[all_category] = ''
						
						
				#페이지 URL 갖고 오기
				self.process_page_list()
				
				#물품 URL 갖고 오기
				self.process_product_list()
				
				#물품의 상세 페이지 정보 갖고 오기
				self.process_product_detail_page()
				
				#삭제된 물품리스트에 대해서, 삭제처리 
				self.process_product_delete_api()
			
		except Exception as ex :  
			__LOG__.Error(ex)            
			pass
			
		
		__LOG__.Trace("***********************************************************")
		__LOG__.Trace("Program End......")
		__LOG__.Trace("***********************************************************")

	
	'''
	######################################################################
	# 상품 상세페이지 테스트 함수
	######################################################################
	''' 

		
	def test_detail_page(self):
		
		try :
			
			self.set_cookie()
			self.set_user_agent()
			
			product_data = ProductData()
			self.process_product_detail( 'https://smartstore.naver.com/hyponic/products/4039468610', product_data)
				
		except Exception as ex :  
			__LOG__.Error(ex)            
			pass


	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 20000000, 10))
	

	BRD_ID_HASH = __API__.get_storelist('smartstore.naver.com')
	#if(len(BRD_ID_HASH) == 0) :
	#	time.sleep(self.WAIT_TIME)
	#	BRD_ID_HASH = __API__.get_storelist( 'smartstore.naver.com' )
			
	app = smartstore()

	for app_url in BRD_ID_HASH.keys() :
		if(app.SHUTDOWN) : break
		brd_id = BRD_ID_HASH[app_url]
		__LOG__.Trace('%s : %s' % (app_url, str(brd_id ) ) )
		app.main(app_url, brd_id)

