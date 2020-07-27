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

           
    
class shopnaver(Mall) :    
        
	def __init__(self) :

		Mall.__init__(self)
		
		self.SITE_HOME = ''
		self.DISPLAY_LIST_COUNT = 10
		
		self.STORE_ID = ''
	
	def set_store_id(self, site_home ) :
		'''
		# https://shopping.naver.com/pet/stores/100114909
		'''
		split_list = site_home.split('/stores/')
		self.STORE_ID = split_list[1].strip()
		
	
	def get_url_product_list(self, page, category_id ) :
		
		URL = 'https://shopping.naver.com/v1/products?_nc_=1589986800000&subVertical=PET&page=%d&pageSize=10&sort=RECENT&displayType=CATEGORY_HOME&includeZzim=true&includeViewCount=false&includeStoreCardInfo=false&includeStockQuantity=false&includeBrandInfo=false&includeBrandLogoImage=false&includeRepresentativeReview=false&includeListCardAttribute=false&includeRanking=false&includeRankingByMenus=false&includeStoreCategoryName=false&includeIngredient=false&storeId=%s&categoryId=%s&standardSizeKeys[]=&standardColorKeys[]=&optionFilters[]=&attributeValueIds[]=&attributeValueIdsAll[]=&certifications[]=' % ( page, self.STORE_ID, category_id)
		
		return URL
		
	def get_url_product_detail(self, product_id ) :
		
		URL = 'https://shopping.naver.com/v1/products/%s?_nc_=1589986800000' % ( product_id)
		
		return URL
	
	def get_url_product_detail_content(self, product_id , product_no ) :
		
		URL = 'https://shopping.naver.com/v1/products/%s/contents/%s/PC?_nc_=1589986800000' % ( product_id , product_no)
		
		return URL

	
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
	
		header = { 'Accept': 'application/json, text/plain, */*' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Referer': category_url , \
			'Sec-Fetch-Dest': 'empty' , \
			'Sec-Fetch-Mode': 'cors' , \
			'Sec-Fetch-Site': 'same-origin' , \
			'User-Agent': self.USER_AGENT } 

		return header
		
		
	def get_header_product_detail(self, product_url):
	
		header = { 'Accept': 'application/json, text/plain, */*' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Referer': product_url , \
			'Sec-Fetch-Dest': 'empty' , \
			'Sec-Fetch-Mode': 'cors' , \
			'Sec-Fetch-Site': 'same-origin' , \
			'User-Agent': self.USER_AGENT } 

		return header
		

	def get_header_product_detail_content(self):
		
		header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' , \
			'Accept-Encoding': 'gzip, deflate, br' , \
			'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6' , \
			'Cache-Control': 'no-cache' , \
			'Cookie': self.COOKIE_STR , \
			'Pragma': 'no-cache' , \
			'Sec-Fetch-Dest': 'document' , \
			'Sec-Fetch-Mode': 'navigate' , \
			'Sec-Fetch-Site': 'none' , \
			'Upgrade-Insecure-Requests': '1' , \
			'User-Agent': self.USER_AGENT }
			
		return header
		
		
	
	def get_json_category(self, json_data) :
		'''
		######################################################################
		# 카테고리 리스트를 갖고 오는 부분
		
		"storeCategories":{"A":{"categories":[{"id":null,"name":"전체","alias":"all","children":[]},{"id":"11023001","name":"강아지","alias":"DOG","children":[{"id":"11023001","name":"전체","alias":"","children":[]},{"id":"11023001006","name":"장난감","alias":"TOY","children":[]},{"id":"11023001007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023001008","name":"패션","alias":"FASHION","children":[]}]},{"id":"11023002","name":"고양이","alias":"CAT","children":[{"id":"11023002","name":"전체","alias":"","children":[]},{"id":"11023002006","name":"장난감","alias":"TOY","children":[]},{"id":"11023002007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023002008","name":"패션","alias":"FASHION","children":[]}]}],"selectedSubCategory":{"id":"11023001","name":"전체","alias":"","children":[]},"brandId":null,"storeId":"100146575","selectedCategory":{"id":"11023001","name":"강아지","alias":"DOG","children":[{"id":"11023001","name":"전체","alias":"","children":[]},{"id":"11023001006","name":"장난감","alias":"TOY","children":[]},{"id":"11023001007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023001008","name":"패션","alias":"FASHION","children":[]}]},"inquiryCategory":{"id":"11023001","name":"전체","alias":"","children":[]},"cacheParam":"{\"__actionType__\":\"\u002Fstore\u002Fgeneral\u002Fcategory\u002FFETCH\",\"__actionCreator__\":\"fetchCategories\",\"inquiryStoreId\":\"100146575\",\"queryParams\":{\"category\":\"11023001\"}}"}},
		
		######################################################################
		'''
		id = None
		name = ''
		alias = ''
		children_len = 0

		
		if('id' in json_data ) : id = json_data['id']
		if('name' in json_data ) : name = json_data['name'] 
		if('alias' in json_data ) : alias = json_data['alias']
		if('children' in json_data ) : children_len = len(json_data['children'] )

		
		
		if( 0 < children_len) :
			if(id != None):
				category_url = '%s?category=%s' % ( self.SITE_HOME , str(id))
				if(self.CATEGORY_URL_HASH.get(category_url , -1) == -1) and ( self.check_ignore_category_text(name) ) : 
					self.CATEGORY_URL_HASH[category_url] = str(id)
					__LOG__.Trace('-----------------------------------------------------------')
					__LOG__.Trace('카테고리명 : %s' % name )
					__LOG__.Trace('카테고리 Sel ID : %s ' % str(id ))
					


				
	def get_category_data(self, html):
		'''
		######################################################################
		# 카테고리 리스트를 갖고 오는 부분
		<script>window.__PRELOADED_STATE__={"addressBook": {"A":{"accountNo":null,"addressBookType":null,"addressInfo":null,"alias":null,"id":null,"possibleOversea":null,"modAuditInfo":null,"phoneNumber1":null,"phoneNumber2":null,"regAuditInfo":null,"regDate":null,"modDate":null}},
		"aiTems":{"A":{"titleTemplate":null,"tgAl":null,"themeIdx":null,"themeTitle":null,"themes":null,"products":null,"page":1,"pageSize":30,"windowProducts":[],"infiniteGridStatus":null}},
		"articleDetail":{"A":{"contentsBBSVO":{"id":null,"bbsCategoryType":null,"bbsTitle":null,"readCount":null,"regDate":null,"contentsDisplayStatusType":null},"editorDetailContentVO":{"contentId":null,"editorType":null,"textContent":null,"renderContent":null,"mobileRenderContent":null},"content":null,"cacheParam":null}},"autoComplete":{"isOpen":false,"isActive":true,"keyword":"","keywordQuery":[],"selected":-1,"totalCount":0,"data":{}},
		"beautyBrands":{"A":{"item":null}},"beautyHome":{"banners":[],"specialEvents":[],"bestProducts":[],"newProducts":[],"selectedNewProductChannel":null,"recentProductChannels":[],"departmentBrands":[],"departmentBrandProducts":[],"selectedDepartmentBrandId":null,"popularMenus":[],"selectedPopularMenuId":null,"tagReviews":[],"selectedTag":null},
		"beautyReviewTag":{"A":{"tags":null,"selectedTag":null,"selectedCategoryId":null}},
		"beautyReviewUgc":{"A":{"ugc":null,"otherUgcs":{"totalCount":0,"ugcs":[],"params":null},"tagReviews":[],"prevTag":null}},
		"beginnerSet":{"A":{"id":null,"waterType":null,"fishSpeciesInfos":[],"fishSpeciesInfo":null,"productAttributeValues":[],"productAttributeValue":null,"allFishingSets":[],"fishingSets":[],"fishingSetId":null,"fishingTackleId":null,"fishingTackles":[],"recommendProducts":[]}},"bestForVerticals":{"condition":{},"products":[]},
		"branch":{"A":{"_id":"","parentId":"","name":"","used":false,"order":0,"exposureText":"","alias":"","subVerticals":[],"type":null,"wholeIds":[],"createdAt":null,"updatedAt":null,"business":null,"images":[],"slogan":null,"branchList":[],"cacheParam":null}},
		"brandCards":{"A":{"brandCards":[],"hasMore":false,"pageCount":0,"page":0,"cacheParam":null}},
		"brandDays":{"A":null},
		"brandNews":{"A":{"contentId":null,"editorType":null,"textContent":null,"renderContent":null,"mobileRenderContent":null,"cacheParam":null}},
		"brandProfile":{"A":{"brand":null,"product":null}},
		"brands":{"A":{"brands":[],"hasMore":false,"pageCount":0,"page":0,"sort":"ABC"}},
		"breadcrumbs":{"A":{"cacheParam":"{\"__actionType__\":\"\u002Fbreadcrumb\u002FFETCH\",\"__actionCreator__\":\"getStoreBreadcrumbs\",\"storeId\":\"100146575\"}","breadcrumbs":[{"text":"네이버쇼핑","urlPc":"\u002Fhome\u002Fp\u002Findex.nhn","urlMobile":"\u002Fhome\u002Fm\u002Findex.nhn"},{"text":"펫윈도","urlPc":"https:\u002F\u002Fswindow.naver.com\u002Fpet\u002Fhome","urlMobile":"https:\u002F\u002Fm.swindow.naver.com\u002Fpet\u002Fhome"},{"text":"깜냥깜냥하우스","urlPc":"\u002Fpet\u002Fstores\u002F100146575","urlMobile":"\u002Fpet\u002Fstores\u002F100146575"}]}},"cartState":{"viewedCartProducts":[],"totalDeliveryFee":{}},
		"categoryProductList":{"A":{"layout":null,"loading":true,"error":false,"hasMore":false,"products":[],"productIndexes":[],"params":{"page":1,"pageSize":10,"sort":"PURCHASE"}}},
		"certification":{"A":{"resultCode":null,"resultMsg":null,"mtlCefNo":null,"bsmNm":null,"mtlNm":null,"matlBscMdlNm":null,"matlDerivMdlNm":null,"matlMfrNm":null,"dtlInfCdNm":null,"cvaPcsYmd":null,"matlEtcMtr":null,"cacheParam":null}},
		"channelProducts":{"A":null},"channelSearch":{"selectedBrands":[],"appliedBrands":[],"myBrands":[],"loading":true},"compositeList":{"layout":null,"compositeItems":[],"compositeParams":[{"type":"WINDOWPRODUCT","param":{"subVertical":"PET","page":1,"pageSize":10,"sort":"RECENT","filter":null,"displayType":"CATEGORY_HOME","includeZzim":true,"includeViewCount":false,"includeItemCount":null,"includeStoreCardInfo":false,"includeStockQuantity":false,"includeBrandInfo":false,"includeBrandLogoImage":false,"includeRepresentativeReview":false,"includeListCardAttribute":false,"includeRanking":false,"includeRankingByMenus":false,"includeStoreCategoryName":false,"filterSoldOut":null,"menuId":null,"storeId":"100146575","storeIds":null,"brandId":null,"brandIds":null,"categoryId":"11023001","productIds":null,"storeCategoryId":null,"standardSizeKeys":[],"standardColorKeys":[],"optionFilters":[],"naverShoppingCategory":null,"attributeValueIds":[],"attributeValueIdsAll":[],"tag":null,"first":null,"certifications":[],"averageReviewScore":null,"totalReviewCount":null},"hasMore":true,"usable":true},{"type":"NEWS","param":{"subVertical":"PET","page":1,"pageSize":2,"sort":"RECENT","filter":null,"contentType":null,"menuId":null,"storeId":"100146575","branchId":null,"showKeyContent":null,"showPageNumber":null,"showRelatedProducts":null,"includedTypes":null,"isBranchNews":null},"hasMore":true,"usable":true},{"type":"PREMIUMREVIEW","param":{"page":1,"pageSize":1,"storeId":"100146575","sellerNo":"510049017"},"hasMore":true,"usable":true}],"page":0,"hasMore":true,"itemCount":0,"isFetched":false,"shownGif":false,"cardKeysForNClick":[],"compositeIndex":[],"type":"list\u002FcompositeList\u002FINIT_COMPOSITE_PARAMS"},
		"compositeMenu":{"A":{"subVertical":null,"channelId":null,"storeCategoryId":null,"displayType":"COMPOSITE_CATEGORY_HOME","first":{},"second":{},"third":{}}},
		"contentRelatedProducts":{"A":{"hasMoreProducts":false,"products":[],"page":0,"itemCount":0,"storeId":null,"productIds":[],"newsId":null,"cacheParam":null,"param":null}},"coordiLayer":{"products":[],"relationProductType":"COORDI","showLayer":false},
		"coordiProducts":{"A":{"products":[],"selectedId":null}},
		"designerStoreContentTabs":{"A":{"storeId":null,"tabs":[],"cacheParam":null}},
		"designerStoreHasEvents":{"A":false},
		"events":{"A":{"events":[],"hasMore":false,"pageCount":0,"page":0,"cacheParam":null}},
		"expectPoint":{"A":null},
		"externalProducts":{"A":{"items":[],"params":{"page":1,"sort":"REL_DES","pageSize":40},"hasMore":false,"loading":false,"infiniteGridStatus":null,"restoredByHistory":false,"categories":[]}},
		"fishingHome":{"A":{"popularProducts":{"hasMoreProducts":false,"products":[]}}},"fishingMenu":{"genreMenuId":null,"parentMenuId":null,"displayableGenreMenuIds":[],"month":null,"area":null,"speciesMenus":[],"defaultFilters":[],"speciesId":"0","productCategoryMenuId":null,"productCategoryMenuName":null},"flipState":false,
		"generalReviewIds":{"A":{"reviewIds":[],"totalCount":0}},"globalPopupLayer":{"element":null,"executeFunctionAtClose":null,"classNames":null,"overElement":{"element":null,"executeFunctionAtClose":null,"classNames":null},"keepPopupOnPush":false,"isTransparent":null,"importantScrollPosition":false},"gnb":{"detailSearch":{"isOpen":false},"category":{"selected":"WEAR","activated":false}},
		"hasRelationProduct":{"A":false},"infiniteGridScrollTop":{"isInfiniteGridPage":false,"scrollTop":false},"isGifAnimation":true,
		"keepRelationProducts":{"A":{}},"keywords":{"keywords":[]},
		"listFilter":{"A":{"filter":"ALL","customFilter":"NONE","isOpened":false}},
		"listItems":{"A":{"items":[],"hasMore":{"base":true,"product":true,"relationProduct":true,"specialEvents":true},"param":null,"page":1,"layoutStatus":null,"shownGif":false}},
		"listSort":{"A":{"sort":"RECENT","isOpened":false}},"locationKept":false,
		"logeye":{"A":{"reqId":null,"status":null,"message":null,"rewards":null}},
		"mapList":{"A":{"translateY":800}},
		"mapSort":{"A":{"sort":"MAP_POPULARITY"}},
		"mapState":{"A":{"center":{"lat":0,"lng":0},"zoom":0,"translateY":0}},
		"mapStores":{"A":{"channels":[],"selectedChannel":null,"selectedOverlapChannels":[]}},
		"menu":{"A":{"subVertical":null,"channelId":null,"storeCategoryId":null,"displayType":"CATEGORY_HOME","first":{},"second":{},"third":{}}},"menuByIngredients":{"selectedMenuId":null,"menuAndProductsArr":[],"searchParam":null},
		"menuByKeyword":{"A":{"menu":[],"menuProductCategory":{},"month":"","productCategoryId":"","productCategory":null,"bannerLoad":false,"banner":null,"beforeCurrentAfterMonth":null,"firstHarvestBanner":null,"defaultBanner":null}},"menuByRegion":{"selectedMenuId":null,"menuAndProductsArr":[],"searchParam":null},
		"menuContent":{"A":{"content":null,"parentMenu":null}},
		"modifyReview":{"A":{"layoutType":"FORM","result":null,"hasResultUpdated":false}},"movingBanner":{"banners":[]},"myAddress":{"nid":"","baseAddress":""},
		"myCouponCounts":{"A":"-"},
		"myInfo":{"A":{"height":9999,"weight":9999,"shoe":9999,"tops":"","bottoms":9999,"agreeYn":false}},
		"myKeepProductsGroup":{"A":{"allGroup":null,"categoryGroups":[],"customerGroups":[]}},
		"myKeepStores":{"A":{"totalCount":0,"keepStoreGroup":[],"keepStores":[],"params":{"page":0,"categoryId":null,"limit":20},"hasMore":false,"infiniteGridStatus":null,"lastGroupKey":1}},"myLocation":{"latitude":0,"longitude":0,"clicked":false},
		"myOrderDeliveryCounts":{"A":"-"},
		"myPcKeepProducts":{"A":{"params":{"page":1,"limit":20,"categoryId":null,"customerGroupId":null},"products":[],"total":0,"lastAction":null}},
		"myPoints":{"A":"-"},
		"myPouchState":{"A":{"items":[],"hasMore":false,"params":{},"fetched":false,"gridStatus":null}},"naverMember":{"isLogin":false,"member":null},"naverMembership":{"isSubscribed":false,"betaTester":false,"payMembership":null},
		"necessityCurrentPromotion":{"A":null},
		"news":{"A":{"articles":[],"keyContent":null,"pageCount":0,"page":0,"hasMore":false,"contentType":null,"includedTypes":null,"storeId":null,"inquiryPageSize":0,"cacheParam":null}},
		"newsListState":{"A":{"newsState":{"articles":[],"hasMore":false},"page":1}},
		"optimizeBenefit":{"A":{"hasIssuableCoupon":false,"coupons":[]}},"optionFilter":{"options":[],"existsOption":false},
		"pagedMyReview":{"A":{"contents":[],"page":0,"size":0,"totalElements":0,"totalPages":0}},
		"pagedProductReview":{"A":{"contents":[],"page":0,"size":0,"totalElements":0,"totalPages":0,"originProductNo":null,"loaded":false}},
		"payMemberStatus":{"A":{"apiSuccess":false,"exceptionMessage":"","payMemberAgreeYn":false,"payMemberNo":0,"sudpendStatusYn":false,"leaveStatusYn":false,"gradeStatusCode":"NONE"}},
		"photoVideoReviewIds":{"A":{"reviewIds":[],"totalCount":0,"originProductNo":null}},
		"photoVideos":{"A":{"items":[]}},"planCategory":[],
		"planDetail":{"A":{"plnswSeq":null,"plnswNm":null,"benfExpsClCd":null,"lcatCatgId":null,"mcatCatgId":null,"lcatCatgNm":null,"mcatCatgNm":null,"plnswTpprtTtl":null,"plnswTpprtPrvncCont":null,"plnswTpprtImgUrl":null,"expsStrtYmdt":null,"expsEndYmdt":null,"tags":null,"sections":false,"channelNo":null,"videoInfo":null,"plnswTypeCd":null}},
		"popularBeautyBrand":{"A":{"storeCategoryId":null,"brandType":"DEPARTMENT_BRAND","brands":[],"productsByBrands":[],"brandDetails":null,"page":0,"hasMore":true}},
		"product":{"A":{"id":null,"isRestrictCart":false,"channelServiceType":null,"channelProductType":null,"channelProductSupplyType":null,"channelProductStatusType":null,"channelProductDisplayStatusType":null,"category":null,"name":null,"productUrl":null,"mobileProductUrl":null,"channel":null,"regDate":null,"modDate":null,"manufactureDate":null,"validDate":null,"storeKeepExclusiveProduct":false,"itselfProductionProductYn":false,"epInfo":{"matchingModelId":0,"naverShoppingRegistration":false,"enuriRegistration":false,"danawaRegistration":false,"syncNvMid":0},"best":false,"displayDate":null,"materialContent":null,"orderRequestUsable":false,"channelProductImages":null,"channelProductAttributes":[],"productNo":null,"salePrice":0,"stockQuantity":0,"saleType":null,"excludeAdminDiscount":false,"payExposure":false,"productStatusType":null,"statusType":null,"authenticationType":null,"productImages":null,"naverShoppingSearchInfo":null,"afterServiceInfo":null,"originAreaInfo":null,"seoInfo":null,"optionUsable":false,"supplementProductUsable":false,"purchaseReviewInfo":null,"taxType":null,"certification":false,"certificationTargetExcludeContent":null,"minorPurchasable":false,"productInfoProvidedNoticeView":null,"productAttributes":null,"productDeliveryInfo":null,"claimDeliveryInfo":null,"benefitsView":null,"benefitsPolicy":null,"mobileBenefitsPolicy":null,"saleAmount":null,"reviewAmount":null,"averageDeliveryLeadTime":null,"preOrder":null,"sellerTags":null,"bbsSeq":0,"galleryImages":null,"materialImages":null,"tagImages":null,"barcodeImages":null,"soldout":false,"viewAttributes":null,"detailAttributes":null,"additionalAttributes":null,"content":null,"commentCount":0,"discounts":null,"storeProducts":[],"categoryProducts":[],"banner":null,"hotdeal":null,"ssChannel":null,"windowProduct":null,"interestFreePlans":{"hasInterestFreePlans":false,"adminBurden":{},"sellerBurden":{}},"eCouponCategory":false,"cultureCategory":false,"mobileDiscountRatio":0,"channelProductNos":[],"togetherProducts":[],"coordiProducts":[],"togetherProductsWithCoordinates":[],"purchasePoint":0,"totalPoint":0,"reviewPoint":0,"textReviewPoint":0,"photoVideoReviewPoint":0,"afterUseTextReviewPoint":0,"afterUsePhotoVideoReviewPoint":0,"managerReviewPoint":0,"storeMemberReviewPoint":0,"displayCategory":null,"userNickname":null,"extensionType":null,"extensionKey":null,"isCultureCostIncomeDeduction":false,"proceedServiceCheck":{"showServiceCheckGuide":false},"channelProductVideos":[],"productVideos":[],"productVideoAuth":null,"todayDispatch":{"thisDayDispatchYn":false},"isPayRestrictCategory":false,"isCustomProduct":false,"isPointPlusMember":false,"points":null,"discountedSalePrice":0,"isExposureIngredient":false,"ingredientExposureAgreeDate":null,"ingredientMappingId":null}},
		"productBestReview":{"A":{"contents":[],"contentChunks":[],"originProductNo":null}},
		"productCategory":{"A":{"first":{"categories":[],"selectedId":null},"second":{"categories":[],"selectedId":null},"third":{"categories":[],"selectedId":null},"isLoading":false}},
		"productOption":{"A":{}},
		"productQna":{"A":{"contents":[],"page":0,"size":0,"totalElements":0,"totalPages":0,"filterAnswerStatus":"ALL","filterMyComment":false,"productId":null}},
		"productReviewEvent":{"A":{}},"productsBenefit":{"A":{}},"randomNo":79,
		"recentlyViewedProducts":{"A":{"originalSize":0,"list":[]}},
		"recommendReview":{"A":{"reviews":[],"hasMore":false,"cacheParam":null,"page":1}},
		"recommendedTag":{"A":{"tags":[],"selectedTag":null,"page":0,"hasMore":false,"totalCount":0,"params":{},"cacheParam":null}},
		"registerReview":{"A":{"layoutType":"FORM","orderNo":null,"reviewProducts":[],"selectedProductOrderNos":[],"currentReviewProduct":null,"nextReviewProduct":null,"mySizeTargets":[],"result":null,"errorMessage":null}},
		"relationProduct":{"A":{"relationProduct":null,"mappingProducts":null,"channelOtherRelationProducts":null,"channelBestProducts":null,"storeCategory":null}},
		"reviewDetails":{"A":[]},
		"reviewEvaluation":{"A":{"productReviewEvaluationVOs":[],"reviewTopicVOs":[],"originProductNo":null}},
		"reviewEvent":{"A":{}},
		"reviewForm":{"A":{"evaluationLength":null,"isValidated":false,"isChanged":false,"form":{"productOptionContentNoDisplay":false,"reviewType":"NORMAL","reviewScore":null,"reviewContent":"","reviewEvaluationValueSeqs":[],"reviewAttaches":[]},"uploadingAttaches":{"isChanged":false,"reviewAttaches":[],"inspectedReviewAttaches":[]},"reviewTags":[],"categoryId":null}},
		"reviewsFilter":{"A":{"selectedSort":"REVIEW_RANKING","selectedFeature":"ALL","selectedScore":"ALL","selectedTopic":null,"changedFilterByUser":false}},"scrollKept":false,
		"seViewerContent":{"A":{"isLoadedCompleted":{"content":false,"notice":false},"content":null,"notices":{"channelNoticeContent":null,"productNoticeContent":null}}},
		"selectedOptions":{"A":{"product":{},"coordi":{},"delivery":{},"textOptions":null,"simpleOptions":null,"combinationOptions":null,"standardOptions":null,"supplementProducts":null,"colorOptions":null,"sizeOptions":null,"hopeDeliveryOptions":{}}},"serverLocationPath":"\u002Fpet\u002Fstores\u002F100146575?category=11023001","serverReferer":true,"serverRendered":true,
		"shoppingLensState":{"A":{"imageUrlParam":null,"products":[],"loading":true,"selectedId":null}},
		"shoppingSearchPhotoVideoReviewIds":{"A":{"reviewIds":[],"cacheParam":null,"totalCount":0}},
		"shoppingSearchReview":{"A":{"pagedReviews":{"contents":[],"page":0,"size":0,"totalElements":0,"totalPages":0,"loaded":false},"reviewTopicVOs":[]}},
		"simpleList":{"A":{"items":[]}},
		"specialEventDetail":{"A":{"event":null,"collections":[],"recommendEvents":[]}},"standardOption":{"standardOptions":[],"existsStOption":false},
		"store":{"A":{"cacheParam":"{\"__actionType__\":\"\u002Fstore\u002FFETCH\",\"__actionCreator__\":\"fetchStore\",\"id\":\"100146575\"}","channel":{"id":"100146575","channelServiceType":"WINDOW","channelExternalStatusType":"NORMAL","sellerStatusReasonType":"ETC","channelName":"깜냥깜냥하우스","categoryId":"50000008","representImageInfoList":[{"imageUrl":"http:\u002F\u002Fshop1.phinf.naver.net\u002F20180303_129\u002Fkkamnyang_kkamnyang_15200420062861f1sP_JPEG\u002F43349185926116164_1891371260.jpg","imageName":"43349185926116164_1891371260.jpg","width":1399,"height":1082,"fileSize":182204,"sortOrder":1,"originalFileName":"43349185926116164_1891371260.jpg","representative":false,"imageClass":"STORE_REPRESENTATIVE"}],"additionalImageInfoList":[{"imageUrl":"https:\u002F\u002Fshop-phinf.pstatic.net\u002F20180404_38\u002Fkkamnyang_kkamnyang_1522816449870xtyWS_JPEG\u002F46123609488172794_655901639.jpg","imageName":"46123609488172794_655901639.jpg","width":711,"height":456,"fileSize":133561,"sortOrder":1,"originalFileName":"46123609488172794_655901639.jpg","representative":false,"imageClass":"STORE_MAIN_VIEW"}],"channelAdmissionDate":"2018-03-05T08:41:27.907+0000","channelValidProductCount":81,"siteChannelInterlockYn":false,"talkAccountId":"wc4dqy","talkExposureYn":true,"description":"깜냥은 자신의 힘을 다하여","detailIntroductionContent":"저희 깜냥깜냥 하우스에서는 반려동물을 위한 제품!\n주인과 반려동물이 함께 쓸 수 있는 제품!\n같은 공간에서 생활하는 우리의 반려동물 주인 또한 같은 공간에서 \n사용하는 제품이므로, 유해하지 않은 재료만 사용합니다.\n핸드메이드 제품입니다.","salesTimeInfo":{"weekDayBeginHour":"","weekDayBeginMin":"","weekDayFinishHour":"","weekDayFinishMin":"","weekEndBeginHour":"","weekEndBeginMin":"","weekEndFinishHour":"","weekEndFinishMin":"","useClosed":false,"weekDayString":"","weekEndString":"","dayOffString":"연중무휴"},"contactInfo":{"displayTelNo":true,"disabledDomesticTelNo":false,"telNo":{"countryCode":"KOR","phoneNo":"01049357842","formattedNumber":"010-4935-7842"},"overseaTelNo":{"countryCode":"KOR","phoneNo":"","formattedNumber":""},"onlineSales":false,"offlineSales":false,"offlineStoreAddressInfo":{"overseas":false,"fullAddressInfo":"","hasRoadNameAddress":false,"hasJibunAddress":true},"additionalChargePersons":[{"name":"김지연","phoneNumber":{"countryCode":"KOR","phoneNo":"01092063617","formattedNumber":"010-9206-3617"},"email":"kkamnyang_kkamnyang@naver.com"}]},"bestShopYn":false,"exhibitionYn":true,"representNo":100036825,"representType":"DOMESTIC_BUSINESS","identity":"740-32-00400","representName":"깜냥깜냥하우스","representativeName":"김지연","categoryItemName":"전자상거래,반려동물수공예제품","businessType":"SIMPLE","declaredToOnlineMarkettingNumber":"2017-부산사하-0281","isOverSeaProductSales":false,"nation":"KOR","businessAddressInfo":{"apiType":"NAVER","address":"경상남도 창원시 진해구 풍호동 83-3","basicAddress":"경상남도 창원시 진해구","jibunAddress":"풍호동 83-3","roadNameAddress":"충장로 575","massiveAddress":"우성아파트","detailAddress":"101동 409호","oldZipCode":"645320","newZipCode":"51653","overseas":false,"fullAddress":"경상남도 창원시 진해구 충장로 575 (우성아파트)","latitude":35.1384909,"longitude":128.7033094,"placeId":"03129144","naverMapCode":"03129144","roadGroupId":"481293331067","representAddressType":"jibun","fullAddressInfo":"(우 : 51653) 경상남도 창원시 진해구 충장로 575 (우성아파트) 101동 409호","hasRoadNameAddress":true,"zipCode":"51653","hasJibunAddress":true},"accountNo":100039148,"defaultChannelNo":100044433,"advertiser":true,"advertizerSubscriptionDate":"2017-08-25T05:04:15.796+0000","mallSeq":572976,"accountAddType":"JOIN","domesticTelephoneNumberReported":false,"storeExposureInfo":{"exposureInfo":{"INSTAGRAM":["kkamnyang_kkamnyang_house"]}},"accountAdmissionDate":"2017-08-10T02:41:21.970+0000","accountValidProductCount":173,"accountExternalStatusType":"NORMAL","naverPayExternalStatusType":"NORMAL","chrgrEmail":"kkamnyang_kkamnyang@naver.com","naverPayNo":100039017,"payReferenceKey":"510049017","payType":"NAVER_PAY","couponPublicationAgreeStatusType":"WAIT","couponPublicationAgreeDate":"2019-10-24T05:09:37.132+0000","deliveryPlaceModifyYn":false,"claimRepealYn":false,"creditScore":6,"actionGrade":"FOURTH","serviceSatisfactionGrade":false,"saleCount":42,"csResponseRatio":1,"in2DaysDeliveryCompleteRatio":0.43,"averageSaleSatificationScore":5,"cumulationSaleAmount":2725500,"cumulationSaleCount":106,"purchaseCustomerCountBy3Month":59,"windowSubVertical":"PET","windowCategoryId":"10106","windowCategoryName":"펫","naverPayUseYn":true,"inquiryUseYn":true,"productInspectionSkipYn":false,"additionalAttribute":{"handleBrandNames":[],"handleSpecificGoods":[]},"naSiteId":"sc_a608f9ee3384_dfe","thisDayDispatchBasisTime":"1400","fullUrl":"https:\u002F\u002Fshopping.naver.com\u002Foutlink\u002Fstorehome\u002F100146575","mobileUrl":"https:\u002F\u002Fm.shopping.naver.com\u002Foutlink\u002Fstorehome\u002F100146575","storeCategoryIds":["10106"],"logoImage":{"imageUrl":"http:\u002F\u002Fshop1.phinf.naver.net\u002F20180303_129\u002Fkkamnyang_kkamnyang_15200420062861f1sP_JPEG\u002F43349185926116164_1891371260.jpg","imageName":"43349185926116164_1891371260.jpg","width":1399,"height":1082,"fileSize":182204,"sortOrder":1,"originalFileName":"43349185926116164_1891371260.jpg","representative":false,"imageClass":"STORE_REPRESENTATIVE"}},"hasHighRatingReview":false}},
		"storeBenefits":{"A":{"user":null,"customerBenefits":null,"basicBenefits":[],"sortedHomeBenefits":[{"eventType":"NAVER_MEMBERSHIP_EVENT"}],"eventBenefits":[{"eventType":"NAVER_MEMBERSHIP_EVENT"}],"deliveryBenefit":null}},
		"storeBrandFilter":{"A":{"subVertical":null,"zzimsIds":[],"selectedId":null,"selectedType":null,"personalizedStoreBrand":null}},
		"storeBrands":{"A":{"brands":[],"selectedBrandId":null,"cacheParam":null}},
		"storeCategories":{"A":{"categories":[{"id":null,"name":"전체","alias":"all","children":[]},{"id":"11023001","name":"강아지","alias":"DOG","children":[{"id":"11023001","name":"전체","alias":"","children":[]},{"id":"11023001006","name":"장난감","alias":"TOY","children":[]},{"id":"11023001007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023001008","name":"패션","alias":"FASHION","children":[]}]},{"id":"11023002","name":"고양이","alias":"CAT","children":[{"id":"11023002","name":"전체","alias":"","children":[]},{"id":"11023002006","name":"장난감","alias":"TOY","children":[]},{"id":"11023002007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023002008","name":"패션","alias":"FASHION","children":[]}]}],"selectedSubCategory":{"id":"11023001","name":"전체","alias":"","children":[]},"brandId":null,"storeId":"100146575","selectedCategory":{"id":"11023001","name":"강아지","alias":"DOG","children":[{"id":"11023001","name":"전체","alias":"","children":[]},{"id":"11023001006","name":"장난감","alias":"TOY","children":[]},{"id":"11023001007","name":"리빙","alias":"LIVING","children":[]},{"id":"11023001008","name":"패션","alias":"FASHION","children":[]}]},"inquiryCategory":{"id":"11023001","name":"전체","alias":"","children":[]},"cacheParam":"{\"__actionType__\":\"\u002Fstore\u002Fgeneral\u002Fcategory\u002FFETCH\",\"__actionCreator__\":\"fetchCategories\",\"inquiryStoreId\":\"100146575\",\"queryParams\":{\"category\":\"11023001\"}}"}},
		"storeCategory":{"A":{"storeCategories":[],"selectedCategory":null,"params":{},"cacheParam":null}},
		"storeContentFilter":{"A":{"channelNo":null,"contentTypes":[],"contentType":null,"cacheParam":null}},
		"storeContentSort":{"A":{"sort":"RECENT"}},
		"storeGrades":{"A":{"exposureNotice":true,"gradePolicies":{}}},
		"storeKeep":{"A":{"zzimCount":554,"hasUserStoreZzim":false,"isOnNews":false,"shownNewsTooltip":false,"storeId":"100146575","params":{"storeId":"100146575"}}},
		"storeMenuState":{"A":{"storeMenus":[],"selectedMenu":null,"params":{}}},
		"storeProducts":{"A":{"hasMoreProducts":false,"products":[],"page":0,"itemCount":0}},
		"storeRelationProduct":{"A":{"vmdList":null,"cacheParam":null}},
		"storeTalktalk":{"A":{"hasBenefit":false,"talkPcUrl":"https:\u002F\u002Ftalk.naver.com\u002Fct\u002Fwc4dqy","friendCount":854,"talkMobileUrl":"https:\u002F\u002Ftalk.naver.com\u002Fct\u002Fwc4dqy#nafullscreen","benefitName":null,"isFriend":false}},
		"storeView":{"A":{"storeId":"100146575","viewCount":5}},
		"stores":{"A":{"channels":[],"page":0,"hasMore":false,"totalCount":0,"params":{}}},"subVerticalByPathname":"PET",
		"summaryCart":{"A":{"count":0,"price":0,"additionalPoint":0,"initCount":0,"initPrice":0,"initAdditionalPoint":0}},
		"tasteAitems":{"A":{"result":null,"params":null,"bgClassName":""}},
		"template":{"A":{"template":null,"templateData":null}},"windowBrand":{"selectedBrands":[],"appliedBrands":[],"myBrands":[],"loading":true},
		"windowProduct":{"A":null},
		"windowsBanners":{"A":{"artHomeBanners":null,"artArtistBanners":null,"categoryBanners":null,"weeklyArtistBanners":null,"eventBandBanner":null,"homeBanners":null,"localMarketBanners":null,"necessityPromotionBanners":null}},
		"writableReviews":{"A":{"writableReviews":[],"page":1,"totalCount":0}},
		"zzimProducts":{"A":{}}}</script>
		######################################################################
		'''
		rtn = False
		
		ignore_str = '<script>window.__PRELOADED_STATE__='
		ignore_pos = html.find(ignore_str) + len( ignore_str )
		last_pos = html[ignore_pos:].find('</script>')
		
		category_data = html[ignore_pos:ignore_pos+last_pos].strip()

		jsondata = json.loads(category_data)
		if('storeCategories' in jsondata) : 
			a_jsondata = jsondata['storeCategories']
			if('A' in a_jsondata) : 
				categories_jsondata = a_jsondata['A']
				if('categories' in categories_jsondata) : 
					category_list = categories_jsondata['categories']
					for category_json in category_list :
						self.get_json_category( category_json )


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
	# 상품 리스트 함수
	######################################################################
	'''
	def set_product_data(self, product_ctx ) :
	
		crw_post_url = 'https://shopping.naver.com/pet/stores/%s/products/%s' % ( self.STORE_ID, product_ctx['_id'] )
		
		if( self.PRODUCT_URL_HASH.get( crw_post_url , -1) == -1) : 
			product_data = ProductData()
			
			# 기본 정보
			self.set_product_data_sub( product_data, crw_post_url, product_ctx )
			
			#self.print_detail_page_info( product_data ) 	
			self.process_product_api(product_data)
			
			rtn = True
			
			
											
	def set_product_data_sub(self, product_data, crw_post_url, product_ctx ) :
		
		try :
			
			#for key in product_ctx.keys() :
			#	__LOG__.Trace('%s : %s' % (key, product_ctx[key]))
			
			# 상품번호
			crw_goods_code = ''
			if('_id' in product_ctx ) : crw_goods_code = product_ctx['_id']

			if( crw_goods_code != '' ) :
				# 기존 상품정보가 입력되어 있을때 UPDATE Action 으로 변경.
				if(self.PRODUCT_ITEM_HASH.get(crw_goods_code, -1) != -1) : 
					product_data.crw_action = __DEFINE__.__UPDATE_CRW__
					product_data.crw_id = self.PRODUCT_ITEM_HASH[crw_goods_code]
					__LOG__.Trace( '%s - %s' % (crw_goods_code , product_data.crw_action ) )
				
				if('name' in product_ctx ) : product_data.crw_name = product_ctx['name']

				if('brand' in product_ctx ) : product_data.crw_brand1 = product_ctx['brand']['name']

				
				if('naverShoppingCategory' in product_ctx ) : product_data.crw_category1 = product_ctx['naverShoppingCategory']['name']

				if('soldout' in product_ctx ) : 
					if( product_ctx['soldout'] ) : product_data.crw_is_soldout = 1

				
				if('salePrice' in product_ctx ) : product_data.crw_price = product_ctx['salePrice']

				if('pcDiscountPrice' in product_ctx ) : product_data.crw_price_sale = product_ctx['pcDiscountPrice']
				
				if( product_data.crw_price_sale == 0 ) :
					if('mobileDiscountPrice' in product_ctx ) : product_data.crw_price_sale = product_ctx['mobileDiscountPrice']

				if('images' in product_ctx ) : 
					img_list = product_ctx['images']
					for img_ctx in img_list :
						#if( img_ctx['representativeImage'] ) :
						if( 'imageUrl' in img_ctx ) :	
							product_data.product_img = img_ctx['imageUrl']
							break


				# 상품상세 페이지 조회시 필요함.
				if('productNo' in product_ctx ) : product_data.product_no = product_ctx['productNo']
				
				product_data.brd_id = self.BRD_ID
				
				product_data.crw_post_url = crw_post_url
				product_data.crw_goods_code  = crw_goods_code
					
				self.PRODUCT_URL_HASH[crw_post_url] = product_data
				self.PRODUCT_AVAIBLE_ITEM_HASH[product_data.crw_goods_code] = product_data.crw_id
			
		except Exception as ex:
			__LOG__.Error(ex)
			pass
			
	
	
	def get_product_data(self, jsondata):
		'''
		#
		# {"hasMoreProducts":true,
		# "products":[{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003017"],"menus":[],"standardSizes":[],"_id":"4938460895","attributes":[{"values":[{"_id":"10033019","name":"여름용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036482","name":"대형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10574774","name":"면"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10241290","name":"핑크"},{"_id":"10669048","name":"스카이블루"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.344Z","updatedAt":"2020-05-21T06:27:12.344Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b2","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b3","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"얇은 면소재로 여름 분위기에 잘 어울리는 마린룩 스타일의 수영복이에요. 다리부분에 끈이 있어 핏을 잡아주어 엉덩이 부분이 너무 귀여웠어요ㅋㅋ 프림, 이지는 XL 사이즈를 입고 있어요- 신축성은 적당한 편이며, 평소 입고 있는 정 사이즈로 선택해 주세요!! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-20T14:37:35.892Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"2567","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200520_290/1589985053641nHOcd_JPEG/27347387208337078_531030866.jpg","fileSize":508858,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_160/1589985053297h0fhQ_JPEG/27347386660798280_1820898407.jpg","fileSize":538677,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_48/1589985442177fSqjY_JPEG/27346180799976431_1338167481.jpg","fileSize":571458,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-21T02:14:16.377Z","mobileDiscountPrice":23900,"mobileDiscountRate":0,"modelNumber":"마린룩 수영복","name":"마린룩 수영복","naverShoppingCategory":{"_id":"50007160","wholeId":"50000008>50000155>50006728>50007160","wholeName":"생활/건강>반려동물>패션용품>수영복/구명조끼","name":"수영복/구명조끼"},"npay":true,"nvMid":82482985206,"pcDiscountPrice":23900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4922203761","recentSaleCount":0,"salePrice":23900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[{"_id":"194971","name":"강아지수영복","type":"MANUAL"}],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-21T02:14:15.845Z","reorderCount":0,"inspectedAt":"2020-05-21T02:14:15.836Z","standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4938454409","attributes":[{"values":[{"_id":"10033019","name":"여름용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031732","name":"네이비"},{"_id":"10241290","name":"핑크"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.345Z","updatedAt":"2020-05-21T06:27:12.346Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b4","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b5","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"얇은 소재로 여름 분위기에 잘 어울리는 마린룩 스타일의 끈나시에요. 프림, 이지는 XL 사이즈를 입고 있어요- 신축성은 적당한 편이며, 평소 입고 있는 정 사이즈로 선택해 주세요!! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-20T14:29:26.836Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200520_251/1589984575384d4Ej6_JPEG/27347963892128014_1005062828.jpg","fileSize":438159,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_201/1589984591464Sh5IT_JPEG/27347979971891567_288324615.jpg","fileSize":455971,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_175/1589984581462M0KIg_JPEG/27347969969290923_1622758708.jpg","fileSize":596571,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-21T02:12:46.781Z","mobileDiscountPrice":11900,"mobileDiscountRate":0,"modelNumber":"마린보이나시","name":"마린보이나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82482978720,"pcDiscountPrice":11900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4922197435","recentSaleCount":0,"salePrice":11900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-21T02:12:46.245Z","reorderCount":0,"inspectedAt":"2020-05-21T02:12:46.237Z","standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4938435480","attributes":[{"values":[{"_id":"10033019","name":"여름용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031742","name":"옐로우"},{"_id":"10241290","name":"핑크"},{"_id":"10533144","name":"그린"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.347Z","updatedAt":"2020-05-21T06:27:12.347Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b6","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b7","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"매우 얇은 소재로 여름 분위기에 잘 어울리는 톡톡 튀는 컬러감으로 시원하게 입을 수 있는 민소매 나시 에요. 등길이가 많이 짧은 크롭 스타일로 간편하게 걸칠 수 있고, 등뒤 가방에 배변봉투,간식 등을 넣어 산책을 좀더 편리하게 하실 수 있답니다. 프림, 이지는 XL 사이즈를 입고 있어요- 신축성은 적당한 편이며, 평소 입고 있는 정 사이즈로 선택해 주세요!! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-20T14:12:06.640Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200520_293/1589983702161lwAn4_JPEG/27344440784773622_407707675.jpg","fileSize":459598,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_127/15899837024076QfYE_JPEG/27344441032211725_1976401754.jpg","fileSize":444605,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_24/1589983702656ogIIp_JPEG/27344441278957442_293071585.jpg","fileSize":445317,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-21T02:12:28.559Z","mobileDiscountPrice":15900,"mobileDiscountRate":0,"modelNumber":"힙색나시","name":"힙색나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82482959791,"pcDiscountPrice":15900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4922178866","recentSaleCount":0,"salePrice":15900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-21T02:12:28.059Z","reorderCount":0,"inspectedAt":"2020-05-21T02:12:28.050Z","standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4938430586","attributes":[{"values":[{"_id":"10033019","name":"여름용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031736","name":"오렌지"},{"_id":"10241290","name":"핑크"},{"_id":"10533144","name":"그린"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.348Z","updatedAt":"2020-05-21T06:27:12.348Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b8","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138b9","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"매우 얇은 소재로 여름 분위기에 잘 어울리는 톡톡 튀는 컬러감과 과일 프린팅으로 귀엽게 입을 수 있는 민소매 나시에요. 등길이가 많이 짧은 크롭 스타일로 간편하게 걸칠 수 있답니다. 프림, 이지는 XL 사이즈를 입고 있어요- 신축성은 적당한 편이며, 평소 입고 있는 정 사이즈로 선택해 주세요!! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-20T14:06:53.132Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200520_233/1589983280359pqL2w_JPEG/27344822980352677_1502540283.jpg","fileSize":476379,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_232/1589983279591aMk3W_JPEG/27344822213744715_543379708.jpg","fileSize":472772,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200520_174/1589983279970ViQ74_JPEG/27344822554947468_2078453254.jpg","fileSize":386473,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-21T02:11:24.984Z","mobileDiscountPrice":13900,"mobileDiscountRate":0,"modelNumber":"선글크롭나시","name":"선글크롭나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82482954897,"pcDiscountPrice":13900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4922174108","recentSaleCount":0,"salePrice":13900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-21T02:11:24.949Z","reorderCount":0,"inspectedAt":"2020-05-21T02:11:24.938Z","standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4917864082","attributes":[{"values":[{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031738","name":"퍼플"},{"_id":"10040013","name":"그레이"},{"_id":"10241290","name":"핑크"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.349Z","updatedAt":"2020-05-21T06:27:12.349Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138ba","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138bb","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"얇은 소재로 가볍게 입기 좋은 끈 나시에요. 에어컨 작동으로 추워하는 아이들, 빡빡이 미용 후에 민감한 아이들을 위해 실내복으로 추천드립니다. 프림,이지는 XL사이즈를 입고 있어요- 신축성은 적당한 편이며, 평소 입고 있는 정 사이즈로 선택해 주세요! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-05T07:20:15.534Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200505_45/1588662828550BoR4K_JPEG/26023567176246706_50470033.jpg","fileSize":446986,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200505_235/1588662828846NyHbQ_JPEG/26023567473601020_2043675760.jpg","fileSize":398777,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200505_37/1588662829098OcRj6_JPEG/26023567725734006_2014263283.jpg","fileSize":391211,"sortOrder":2,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200505_129/1588662829437wtWtQ_JPEG/26023568055858894_1600774075.jpg","fileSize":941231,"sortOrder":3,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-06T01:59:55.499Z","mobileDiscountPrice":11900,"mobileDiscountRate":0,"modelNumber":"릴리끈나시","name":"릴리 끈나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82462387853,"pcDiscountPrice":11900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4901939463","recentSaleCount":0,"salePrice":11900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-06T01:59:54.963Z","reorderCount":0,"inspectedAt":"2020-05-06T01:59:54.955Z","popularScore":5.57,"standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003012"],"menus":[],"standardSizes":[],"_id":"4917130008","attributes":[{"values":[{"_id":"10033017","name":"사계절"},{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031731","name":"블루"},{"_id":"10031742","name":"옐로우"},{"_id":"10531869","name":"화이트"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.350Z","updatedAt":"2020-05-21T06:27:12.350Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138bc","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138bd","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"지금 부터 여름까지 소풍갈때 나들이룩으로 추천드리는 여리여리한 블라우스에요. 얇은 소재로 가볍게 입힐 수 있고, 앞으로 입는방식의 등뒤에 단추가 있어 편하게 착용이 가능합니다. 프림,이지는 XL사이즈를 입고 있어요- 신축성은 적은편이며, 평소 입고 있는 정 사이즈로 선택해주세요! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-04T11:56:35.394Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1804","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200504_24/1588593003040mk8NA_JPEG/25952837580522260_1092907023.jpg","fileSize":457704,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_73/15885930034112uOls_JPEG/25952837951003199_1144972972.jpg","fileSize":420379,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_96/1588593003759D5g2f_JPEG/25952838298869793_38286525.jpg","fileSize":457208,"sortOrder":2,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_212/1588592991195fdqtl_JPEG/25952825736308541_108069962.jpg","fileSize":437986,"sortOrder":3,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-06T01:48:55.813Z","mobileDiscountPrice":21900,"mobileDiscountRate":0,"modelNumber":"진주블라우스","name":"진주블라우스","naverShoppingCategory":{"_id":"50007155","wholeId":"50000008>50000155>50006728>50007155","wholeName":"생활/건강>반려동물>패션용품>셔츠/블라우스","name":"셔츠/블라우스"},"npay":true,"nvMid":82461653744,"pcDiscountPrice":21900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4901216849","recentSaleCount":0,"salePrice":21900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-06T01:48:55.279Z","reorderCount":0,"inspectedAt":"2020-05-06T01:48:55.269Z","popularScore":5.83,"standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4916937104","attributes":[{"values":[{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031742","name":"옐로우"},{"_id":"10241290","name":"핑크"},{"_id":"10533144","name":"그린"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.352Z","updatedAt":"2020-05-21T06:27:12.352Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138be","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138bf","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"지금 부터 여름까지 소풍갈때 나들이룩으로 추천드리는 면소재의 꿀벌 끈나시에요! 프림,이지는 XL사이즈를 입고 있어요- 신축성은 적당한편이며, 등길이는 살짝 짧게 나왔습니다. 평소 입고 있는 정 사이즈로 여유롭게 선택해주세요! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-04T09:14:42.852Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200504_121/15885834472078FIVo_JPEG/25943281627550324_1036611382.jpg","fileSize":409505,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_205/1588583446803irh2u_JPEG/25943281342212176_1208101651.jpg","fileSize":431100,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_84/1588583447504fb9pT_JPEG/25943282045047960_754407431.jpg","fileSize":426813,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectedAt":"2020-05-04T09:15:35.224Z","inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-04T09:15:36.650Z","mobileDiscountPrice":10900,"mobileDiscountRate":0,"modelNumber":"네온꿀벌나시","name":"네온꿀벌 끈나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82461460840,"pcDiscountPrice":10900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4901027793","recentSaleCount":0,"salePrice":10900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-04T09:15:36.311Z","reorderCount":0,"popularScore":5.39,"standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003010"],"menus":[],"standardSizes":[],"_id":"4916899222","attributes":[{"values":[{"_id":"10033017","name":"사계절"},{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10531869","name":"화이트"},{"_id":"10531885","name":"민트"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.353Z","updatedAt":"2020-05-21T06:27:12.353Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c0","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c1","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"시원한 지지미 소재로 통풍이 잘되어 여름에도 가볍게 입을 수 있는 플로럴 패턴의 원피스에요. 가슴 부분에는 '주름' 처리로 편하게 착용이 가능해요- 프림,이지는 XL사이즈를 착용하였어요. 신축성은 좋은편이며, 평소 입는 정 사이즈로 추천드립니다.","createdAt":"2020-05-04T08:46:23.270Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1695","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200504_52/1588581696831BizPs_JPEG/25943239452232023_7634943.jpg","fileSize":477121,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_214/1588581697227XI4Fi_JPEG/25943239848373666_1667551227.jpg","fileSize":463949,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_234/1588581697614nErQ0_JPEG/25943240226630467_1752334146.jpg","fileSize":1032662,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectedAt":"2020-05-04T08:50:40.717Z","inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-04T08:50:42.177Z","mobileDiscountPrice":17900,"mobileDiscountRate":5.79,"modelNumber":"플로럴 주름 원피스","name":"플로럴 주름 원피스","naverShoppingCategory":{"_id":"50007153","wholeId":"50000008>50000155>50006728>50007153","wholeName":"생활/건강>반려동물>패션용품>원피스/드레스","name":"원피스/드레스"},"npay":true,"nvMid":82461422958,"pcDiscountPrice":17900,"pcDiscountRate":5.79,"productDisplayCategoryId":"11023001008","productNo":"4900990611","recentSaleCount":0,"salePrice":19000,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-04T08:50:41.902Z","reorderCount":0,"popularScore":6.54,"standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003005"],"menus":[],"standardSizes":[],"_id":"4916884326","attributes":[{"values":[{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10031742","name":"옐로우"},{"_id":"10241290","name":"핑크"},{"_id":"10533144","name":"그린"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"},{"_id":"10566766","name":"고양이"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.354Z","updatedAt":"2020-05-21T06:27:12.354Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c2","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c3","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"여름날씨에 잘어울리는 컬러풀한 얇은 소재로 가볍게 입고 나갈 수 있는 나시에요. 프림,이지는 XL사이즈를 입고 있어요- 신축성은 좋은편이며, 등길이가 짧게 나온 크롭 스타일 나왔어요- 평소 입고 있는 정 사이즈로 선택해주세요!! 이지 7.9KG [목33,가슴47,등35] ㅣ 프림 7.4KG [목31,가슴46,등33]","createdAt":"2020-05-04T08:34:33.152Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1634","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200504_163/1588580945366LjIv3_JPEG/25943278875927141_1445068673.jpg","fileSize":465926,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_28/1588580944938dkhG0_JPEG/25943278507219673_1622581184.jpg","fileSize":448182,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_256/1588580945745VyRbh_JPEG/25943279311231099_1264450409.jpg","fileSize":424365,"sortOrder":2,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_206/1588580946119lnmNO_JPEG/25943279681912135_1100657942.jpg","fileSize":623826,"sortOrder":3,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_76/1588580946537nl3pf_JPEG/25943280098145358_799391451.jpg","fileSize":888022,"sortOrder":4,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectedAt":"2020-05-04T08:35:45.694Z","inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-04T08:35:47.345Z","mobileDiscountPrice":9900,"mobileDiscountRate":0,"modelNumber":"왕꽃나시","name":"왕꽃 나시","naverShoppingCategory":{"_id":"50006731","wholeId":"50000008>50000155>50006728>50006731","wholeName":"생활/건강>반려동물>패션용품>티셔츠/후드","name":"티셔츠/후드"},"npay":true,"nvMid":82461408062,"pcDiscountPrice":9900,"pcDiscountRate":0,"productDisplayCategoryId":"11023001008","productNo":"4900976016","recentSaleCount":0,"salePrice":9900,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-05-04T08:35:46.752Z","reorderCount":0,"popularScore":5.94,"standardColors":[],"isNewItem":true},{"displayCategory":["11023","11023001","11023001008","11023","11023002","11023002008"],"productCategory":["12027","12027003","12027003010"],"menus":[],"standardSizes":[],"_id":"4910264835","attributes":[{"values":[{"_id":"10033017","name":"사계절"},{"_id":"10033019","name":"여름용"},{"_id":"10033020","name":"봄,가을용"}],"_id":"10008107","name":"사용계절"},{"values":[{"_id":"10036480","name":"소형"},{"_id":"10036513","name":"중형"}],"_id":"10013135","name":"대상크기"},{"values":[{"_id":"10718495","name":"합성섬유"}],"_id":"10013157","name":"소재"},{"values":[{"_id":"10241290","name":"핑크"},{"_id":"10531869","name":"화이트"},{"_id":"10531885","name":"민트"}],"_id":"10013163","name":"색상계열"},{"values":[{"_id":"10419356","name":"강아지"}],"_id":"10013342","name":"대상"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-21T06:27:12.355Z","updatedAt":"2020-05-21T06:27:12.355Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100114909","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET","frontExposureName":"펫"}],"representBrands":[],"_id":"100114909","name":"바이담수미","representativeImage":{"width":1299,"height":209,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c4","imageUrl":"http://shop1.phinf.naver.net/20180322_121/damsoomi14_1521691050071X6SvV_JPEG/44997350699250467_1579647252.jpg","imageName":"44997350699250467_1579647252.jpg","fileSize":16041,"sortOrder":1,"originalFileName":"44997350699250467_1579647252.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":203,"representativeImage":false,"_id":"5ec61f40f8b2ae003d7138c5","imageUrl":"http://shop1.phinf.naver.net/20171231_222/damsoomi14_1514648420272kHE4c_JPEG/37955599915948661_-775830448.jpg","imageName":"37955599915948661_-775830448.jpg","fileSize":14768,"sortOrder":1,"originalFileName":"37955599915948661_-775830448.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc5lwg","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"]},"contentText":"부드러운 소재로 편안하게 착용이 가능한 원피스에요. 프림,이지는 XL사이즈를 착용하였어요. 신축성은 좋은편이며, 등길이가 조금 길게 나온 편이에요. 평소 입는 정 사이즈로 추천드립니다. 프림 7.4KG - XL사이즈 착용","createdAt":"2020-04-27T12:59:12.358Z","deliveryAttributeType":"NORMAL","exposure":true,"goods":"1695","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200427_50/1587992040296iy4gX_JPEG/25352778925533542_215709540.jpg","fileSize":422736,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200427_240/1587992039659tngOU_JPEG/25352778286450460_1607040048.jpg","fileSize":662193,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200427_105/1587992039973P1Fcz_JPEG/25352778600217477_449294279.jpg","fileSize":461673,"sortOrder":2,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200427_151/1587992040620KOnNh_JPEG/25352779249628882_736486704.jpg","fileSize":457663,"sortOrder":3,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectedAt":"2020-04-27T13:00:33.875Z","inspectionStatus":"COMPLETE","martUpdatedAt":"2020-04-27T13:00:35.639Z","mobileDiscountPrice":17900,"mobileDiscountRate":5.79,"modelNumber":"파자마원피스","name":"파자마 원피스","naverShoppingCategory":{"_id":"50007153","wholeId":"50000008>50000155>50006728>50007153","wholeName":"생활/건강>반려동물>패션용품>원피스/드레스","name":"원피스/드레스"},"npay":true,"nvMid":82454788529,"pcDiscountPrice":17900,"pcDiscountRate":5.79,"productDisplayCategoryId":"11023001008","productNo":"4894485798","recentSaleCount":0,"salePrice":19000,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[],"talkPay":false,"totalReviewCount":0,"totalSaleCount":0,"updatedAt":"2020-04-27T13:00:35.036Z","reorderCount":0,"popularScore":6.37,"standardColors":[],"isNewItem":true}]}
		#
		'''
		is_have_data = 'False'
		rtn = False	
		try :

			if('hasMoreProducts' in jsondata ) : is_have_data = str( jsondata['hasMoreProducts'] )
			if('products' in jsondata ) : 
				product_list = jsondata['products']

				for product_ctx in product_list :
					self.set_product_data(product_ctx )

		except Exception as ex:
			__LOG__.Error(ex)
			pass
		
		rtn_loop = False
		if( is_have_data == 'True') : rtn_loop = True
		
		return rtn , rtn_loop

				
		
	def process_product(self, category_url, category_id):
	
		rtn = False
		resptext = ''
		if( config.__DEBUG__ ) : __LOG__.Trace('category : %s' % ( category_url ) )
		
		page = 0
		
		while(True) :
			if(self.SHUTDOWN) : break
			try :
				page += 1
				time.sleep(self.WAIT_TIME*2)
				URL = self.get_url_product_list(page, category_id) 
				header = self.get_header_product_list(category_url)

				resp = None
				resp = requests.get( URL, headers=header )

				if( resp.status_code != 200 ) :
					__LOG__.Error(resp.status_code)
					break
				else :
					resptext = resp.text
					#__LOG__.Trace( resptext )
					jsondata = json.loads(resptext)
					rtn, rtn_loop = self.get_product_data( jsondata )
					if(rtn_loop == False) : break
					
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
			
		for category_url in self.CATEGORY_URL_HASH.keys() :
			if(self.SHUTDOWN) : break
			category_id = self.CATEGORY_URL_HASH[category_url]
			self.process_product( category_url, category_id )
		
		if(config.__DEBUG__) : __LOG__.Trace( '총 물품 수 : %d' % len(self.PRODUCT_URL_HASH))	
		__LOG__.Trace("*************************************************")	
		
		return rtn			
				
	'''
	######################################################################
	#
	# 상품 상세 페이지 : 사이트별 수정해야 함.
	#
	######################################################################
	'''
		
	def get_product_detail_data(self, product_data, jsondata):
		'''
		#
		# 상품 설명 정보 JSON 데이터 추출
		#
		#{"id":"4883445820","channelServiceType":"WINDOW","channelProductType":"SINGLE","channelProductSupplyType":"OWNER","channelProductStatusType":"NORMAL","channelProductDisplayStatusType":"ON","category":{"categoryId":"50006675","categoryName":"장난감/토이","category1Id":"50000008","category2Id":"50000155","category3Id":"50006673","category4Id":"50006675","category1Name":"생활/건강","category2Name":"반려동물","category3Name":"강아지 장난감/훈련","category4Name":"장난감/토이","wholeCategoryId":"50000008>50000155>50006673>50006675","wholeCategoryName":"생활/건강>반려동물>강아지 장난감/훈련>장난감/토이","categoryLevel":4,"lastLevel":true,"sortOrder":2,"validCategory":true,"receiptIssue":true,"exceptionalCategoryTypes":[]},"name":"칼리 라텍스 베어 장난감","productUrl":"https://shopping.naver.com/outlink/itemdetail/4883445820","mobileProductUrl":"https://m.shopping.naver.com/outlink/itemdetail/4883445820","channel":{"accountNo":500088471,"channelNo":"100045370","channelName":"아이펫케어","representName":"주식회사 아이펫","channelSiteFullUrl":"https://shopping.naver.com/outlink/storehome/100045370","channelSiteMobileUrl":"https://m.shopping.naver.com/outlink/storehome/100045370","accountId":"ipatcare","naverPaySellerNo":"500088471","sellerExternalStatusType":"NORMAL","logoWidth":1300,"logoHeight":1300,"logoUrl":"http://shop1.phinf.naver.net/20190111_64/ipatcare_1547187294854Axy0Y_JPEG/70494454471166863_1288590986.jpg","channelTypeCode":"WINDOW","verticalType":"PET","subVerticalType":"PET"},"regDate":"2020-04-08T10:53:43.888+0000","modDate":"2020-05-01T10:27:32.693+0000","storeKeepExclusiveProduct":false,"epInfo":{"naverShoppingRegistration":true,"enuriRegistration":false,"danawaRegistration":false,"syncNvMid":82427969291},"best":false,"displayDate":"2020-04-09T02:31:04.010+0000","orderRequestUsable":false,"channelProductAttributes":[],"productNo":"4868143905","salePrice":6500,"stockQuantity":3,"saleType":"NEW","excludeAdminDiscount":false,"payExposure":true,"productStatusType":"SALE","statusType":"SALE","authenticationType":"NORMAL","productImages":[{"order":1,"url":"https://shop-phinf.pstatic.net/20200408_266/1586342975386JBxQB_JPEG/23702809934705667_658754964.jpg","width":1000,"height":1000,"imageType":"REPRESENTATIVE"},{"order":1,"url":"https://shop-phinf.pstatic.net/20200408_293/15863429864824khE6_JPEG/23702821032331385_1943910107.jpg","width":1000,"height":1000,"imageType":"OPTIONAL"},{"order":2,"url":"https://shop-phinf.pstatic.net/20200408_57/1586342986687P8ekt_JPEG/23702821237292653_762877746.jpg","width":1000,"height":1000,"imageType":"OPTIONAL"}],"naverShoppingSearchInfo":{"manufacturerName":"칼리","brandName":"칼리","brandId":14111,"modelName":"칼리 라텍스 베어"},"itselfProductionProductYn":false,"afterServiceInfo":{"afterServiceTelephoneNumber":"010-6292-9574","afterServiceGuideContent":"아이펫케어 고객센터"},"originAreaInfo":{"originAreaType":"IMPORT","content":"독일산(씨씨펫)","originAreaCode":"0201005","wholeOriginAreaName":"수입산:유럽>독일","importer":"씨씨펫","plural":false},"seoInfo":{"sellerTags":[{"code":"179682","text":"강아지토이"},{"text":"반려동물장난감"},{"code":"714117","text":"강아지장난감인형"},{"text":"라텍스"},{"text":"라텍스토끼"},{"code":"9486","text":"반려동물"},{"code":"176521","text":"반려동물용품"},{"text":"신나는장난감"},{"text":"강아지용품"}]},"optionUsable":false,"supplementProductUsable":false,"purchaseReviewInfo":{"purchaseReviewExposure":true},"customMadeInfo":{"customMade":false},"taxType":"TAX","certification":false,"certificationTargetExcludeContent":{"kcCertifiedProductExclusionYn":true,"kcCertifiedProductExclusionType":"TRUE"},"minorPurchasable":true,"productInfoProvidedNoticeView":{"basic":{"품명 / 모델명":"상품상세 참조 / 상품상세 참조","법에 의한 인증, 허가 등을 받았음을 확인할 수 있는 경우 그에 대한 사항":"해당사항 없음","제조자":"칼리","제조국":"독일산(씨씨펫)","A/S 책임자":"상품상세 참조","A/S 전화번호":"010-6292-9574"},"additional":{"재화등의 배송방법에 관한 정보":"택배","주문 이후 예상되는 배송기간":"대금 지급일로부터 3일 이내에 발송","제품하자·오배송 등에 따른 청약철회 등의 경우 청약철회 등을 할 수 있는 기간 및 통신판매업자가 부담하는 반품비용 등에 관한 정보":"전자상거래등에서의소비자보호에관한법률 등에 의한 제품의 하자 또는 오배송 등으로 인한 청약철회의 경우에는 상품 수령 후 3개월 이내, 그 사실을 안 날 또는 알 수 있었던 날로부터 30일 이내에 청약철회를 할 수 있으며, 반품 비용은 통신판매업자가 부담합니다.","제품하자가 아닌 소비자의 단순변심, 착오구매에 따른 청약철회 시 소비자가 부담하는 반품비용 등에 관한 정보":"편도 2500원 (최초 배송비 무료인 경우 5000원 부과)","제품하자가 아닌 소비자의 단순변심, 착오구매에 따른 청약철회가 불가능한 경우 그 구체적 사유와 근거":"상품상세 참조","재화등의 교환·반품·보증 조건 및 품질보증기준":"상품상세 참조","재화등의 A/S 관련 전화번호":"010-6292-9574","대금을 환불받기 위한 방법과 환불이 지연될 경우 지연에 따른 배상금을 지급받을 수 있다는 사실 및 배상금 지급의 구체적 조건 및 절차":"상품상세 참조","소비자피해보상의 처리, 재화등에 대한 불만 처리 및 소비자와 사업자 사이의 분쟁처리에 관한 사항":"상품상세 참조","거래에 관한 약관의 내용 또는 확인할 수 있는 방법":"상품상세 페이지 및 페이지 하단의 이용약관 링크를 통해 확인할 수 있습니다."}},"productAttributes":[{"attributeValueSeq":10718505,"attributeSeq":10013134,"attributeName":"기능","attributeClassificationType":"MULTI_SELECT","minAttributeValue":"소리나는","minAttributeValueUnitText":"","maxAttributeValueUnitText":"","attributeRealValueUnitText":""},{"attributeValueSeq":10721460,"attributeSeq":10013134,"attributeName":"기능","attributeClassificationType":"MULTI_SELECT","minAttributeValue":"치석케어","minAttributeValueUnitText":"","maxAttributeValueUnitText":"","attributeRealValueUnitText":""},{"attributeValueSeq":10718509,"attributeSeq":10013134,"attributeName":"기능","attributeClassificationType":"MULTI_SELECT","minAttributeValue":"물에뜨는","minAttributeValueUnitText":"","maxAttributeValueUnitText":"","attributeRealValueUnitText":""},{"attributeValueSeq":10718494,"attributeSeq":10013156,"attributeName":"소재","attributeClassificationType":"SINGLE_SELECT","minAttributeValue":"고무/실리콘","minAttributeValueUnitText":"","maxAttributeValueUnitText":"","attributeRealValueUnitText":""}],"productDeliveryInfo":{"deliveryFeeType":"PAID","deliveryMethodTypes":["DELIVERY"],"baseFee":2500,"deliveryFeePayType":"PREPAID","installationFee":false,"deliveryBundleGroup":{"id":13224828,"deliveryFeeChargeMethodType":"MAX","deliveryAreaType":"AREA_2","area2ExtraFee":3000},"deliveryFeePolicyText":"제주,도서지역 추가 3,000원","deliveryAttributeType":"TODAY"},"claimDeliveryInfo":{"returnDeliveryCompanyPriority":"PRIMARY","deliveryCompanyName":"롯데택배","deliveryCompanyCode":"HYUNDAI","naverPayAppointment":false,"returnDeliveryFee":2500,"exchangeDeliveryFee":5000,"shippingAddressId":101433299,"returnAddressId":101433299,"shippingAddress":"(우 : 16926) 경기도 용인시 기흥구 이현로30번길 45 1층 아이펫케어","returnAddress":"(우 : 16926) 경기도 용인시 기흥구 이현로30번길 45 1층 아이펫케어","overseasShipping":false,"individualCustomUniqueCodeUsable":true},"isCultureCostIncomeDeduction":false,"isRestrictCart":false,"benefitsView":{"discountedSalePrice":6500,"mobileDiscountedSalePrice":6500,"sellerImmediateDiscountAmount":0,"mobileSellerImmediateDiscountAmount":0,"managerImmediateDiscountAmount":0,"mobileManagerImmediateDiscountAmount":0,"discountedRatio":0,"mobileDiscountedRatio":0,"sellerPurchasePoint":0,"mobileSellerPurchasePoint":0,"sellerCustomerManagementPoint":0,"mobileSellerCustomerManagementPoint":0,"managerPurchasePoint":65,"mobileManagerPurchasePoint":65,"generalPurchaseReviewPoint":0,"premiumPurchaseReviewPoint":0,"managerGeneralPurchaseReviewPoint":50,"managerPremiumPurchaseReviewPoint":150,"textReviewPoint":0,"photoVideoReviewPoint":0,"afterUseTextReviewPoint":0,"afterUsePhotoVideoReviewPoint":0,"storeMemberReviewPoint":0,"managerTextReviewPoint":50,"managerPhotoVideoReviewPoint":150,"managerAfterUseTextReviewPoint":0,"managerAfterUsePhotoVideoReviewPoint":0,"givePresent":true},"benefitsPolicy":{"managerPurchasePointPolicyNo":212823565,"managerPurchasePointValueUnit":"PERCENT","managerPurchasePointValue":1,"givePresent":true},"mobileBenefitsPolicy":{"managerPurchasePointPolicyNo":212823565,"managerPurchasePointValueUnit":"PERCENT","managerPurchasePointValue":1,"givePresent":true},"saleAmount":{"cumulationSaleCount":2,"recentSaleCount":0},"reviewAmount":{"totalReviewCount":0,"score1ReviewCount":0,"score2ReviewCount":0,"score3ReviewCount":0,"score4ReviewCount":0,"score5ReviewCount":0,"averageReviewScore":0,"productSatisfactionPercent":0,"premiumReviewHighlyRecommendationCount":0,"premiumReviewRecommendationCount":0,"premiumReviewNormalCount":0,"premiumReviewNotRecommendationCount":0,"generalReviewSatisfactionCount":0,"generalReviewNormalCount":0,"generalReviewDisSatisfactionCount":0,"premiumReviewCount":0},"sellerDeliveryLeadTimes":[{"rangeNumberText":"1","rangeText":"일 이내","leadTimeCount":815,"leadTimePercent":68},{"rangeNumberText":"2","rangeText":"일 이내","leadTimeCount":346,"leadTimePercent":29},{"rangeNumberText":"3","rangeText":"일 이내","leadTimeCount":32,"leadTimePercent":3},{"rangeNumberText":"4","rangeText":"일 이상","leadTimeCount":8,"leadTimePercent":1}],"averageDeliveryLeadTime":{"productAverageDeliveryLeadTime":0,"sellerAverageDeliveryLeadTime":1.2681099},"detailContents":{"detailContentText":"칼리 라텍스 베어Karlie Latex Bear오돌토돌 귀여운 동물 장난감 라텍스 베어는 안전한 라텍스 재질로 만들어져 강도와 탄력이 매우 좋습니다. 몸통을 누루면 삑삑♬ 소리가 나는 장난감 입니다. 이갈이를 하는 아이, 물고 뜯고 놀기 좋아하는 아이들에게 안성맞춤!제조사 칼리 Karlie / 독일 수입사 씨씨펫 원산지 중국 제품 사이즈Karlie독일 Bad Wunnenburg-Haaren 에 본사를 두고 있는 칼리는 디자인, 재료, 마무리 등 반려동물 과 반려인들의 편의를 충족해 주는 고품질의 제품을 추구합니다.","excessDetailContentText":false,"editorType":"SE3"},"representImage":{"order":1,"url":"https://shop-phinf.pstatic.net/20200408_266/1586342975386JBxQB_JPEG/23702809934705667_658754964.jpg","width":1000,"height":1000,"imageType":"REPRESENTATIVE"},"view360Image":[],"galleryImages":[{"order":1,"url":"https://shop-phinf.pstatic.net/20200408_266/1586342975386JBxQB_JPEG/23702809934705667_658754964.jpg","width":1000,"height":1000,"imageType":"REPRESENTATIVE"},{"order":1,"url":"https://shop-phinf.pstatic.net/20200408_293/15863429864824khE6_JPEG/23702821032331385_1943910107.jpg","width":1000,"height":1000,"imageType":"OPTIONAL"},{"order":2,"url":"https://shop-phinf.pstatic.net/20200408_57/1586342986687P8ekt_JPEG/23702821237292653_762877746.jpg","width":1000,"height":1000,"imageType":"OPTIONAL"}],"soldout":false,"viewAttributes":{"상품상태":"신상품","상품번호":"4883445820","제조사":"칼리","브랜드":"칼리","모델명":"칼리 라텍스 베어","원산지":"독일산(씨씨펫)"},"additionalAttributes":{"영수증발급":"신용카드전표, 현금영수증발급","A/S 안내":["010-6292-9574","아이펫케어 고객센터"]},"sellerTags":[{"code":"179682","text":"강아지토이"},{"text":"반려동물장난감"},{"code":"714117","text":"강아지장난감인형"},{"text":"라텍스"},{"text":"라텍스토끼"},{"code":"9486","text":"반려동물"},{"code":"176521","text":"반려동물용품"},{"text":"신나는장난감"},{"text":"강아지용품"}],"eCouponCategory":false,"cultureCategory":false,"deliveryText":"제주,도서지역 추가 3,000원","deliveryMethodType":{"code":1,"name":"택배","description":"택배","etc":null,"naverPayCode":"DELIVERY"},"deliveryPayType":"PREPAID","purchasePoint":65,"reviewPoint":150,"textReviewPoint":50,"photoVideoReviewPoint":150,"afterUseTextReviewPoint":0,"afterUsePhotoVideoReviewPoint":0,"managerReviewPoint":150,"storeMemberReviewPoint":0,"totalPoint":215,"discountedSalePrice":6500,"points":{"sellerPurchasePoint":0,"managerPurchasePoint":65,"sellerCustomerManagementPoint":0,"textReviewPoint":50,"photoVideoReviewPoint":150,"afterUseTextReviewPoint":0,"afterUsePhotoVideoReviewPoint":0,"storeMemberReviewPoint":0},"mobileDiscountRatio":0,"detailAttributes":{"기능":"소리나는, 치석케어, 물에뜨는","소재":"고무/실리콘"},"productVideoAuth":false,"commentCount":0,"discounts":[],"storeProducts":[{"discountPrice":0,"linkUrl":"/pet/stores/100045370/products/2290106958","salePrice":2450,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20161120_281/ipatcare_14796420631743q6rQ_JPEG/3906842513550247_438977738.jpg","productId":"2290106958","productName":"버박 C.E.T 미니 칫솔 1p","width":300,"height":300},{"discountPrice":0,"linkUrl":"/pet/stores/100045370/products/2138863336","salePrice":950,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190325_21/ipatcare_1553494125251qnHY3_JPEG/76801304884441462_1172135799.jpg","productId":"2138863336","productName":"로얄캐닌 캣 인스팅티브 그레이비 파우치 85g","width":640,"height":640},{"discountPrice":0,"linkUrl":"/pet/stores/100045370/products/2138863029","salePrice":950,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190325_87/ipatcare_1553494148662oxu8p_JPEG/76801328295408519_1040940542.jpg","productId":"2138863029","productName":"로얄캐닌 캣 울트라 라이트 그레이비 파우치 85g","width":640,"height":640},{"discountPrice":0,"linkUrl":"/pet/stores/100045370/products/2138863587","salePrice":950,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190325_296/ipatcare_1553494102734aKFVs_JPEG/76801282367267957_762694069.jpg","productId":"2138863587","productName":"로얄캐닌 캣 키튼 인스팅티브 그레이비 파우치 85g","width":640,"height":640},{"discountPrice":1000,"linkUrl":"/pet/stores/100045370/products/2138870339","salePrice":9700,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20181112_188/ipatcare_1542014263545BxKgF_JPEG/24733122393890451_269407681.jpg","productId":"2138870339","productName":"버박 프리벤티크 목걸이 진드기 모낭충 21년 2월 + 국내산 수제간식 1종","width":640,"height":640},{"discountPrice":700,"linkUrl":"/pet/stores/100045370/products/3327258225","salePrice":8600,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20180723_136/ipatcare_1532320854074XnIbi_JPEG/14952033729917117_912799563.jpg","productId":"3327258225","productName":"버박 C.E.T 바닐라민트맛 치약 70g","width":640,"height":640}],"categoryProducts":[{"discountPrice":23000,"linkUrl":"/pet/stores/100079196/products/2511370406","salePrice":42800,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20180214_277/attifriend_1518567309439wNtoU_JPEG/41873610063149337_142179057.jpg","productId":"2511370406","productName":"강아지 노즈워크 분리불안 훈련 담요 스너플매트","width":640,"height":640},{"discountPrice":1010,"linkUrl":"/pet/stores/100128675/products/2849445589","salePrice":3000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20160406_32/petforyou_14599113559830jQND_JPEG/21.jpg","productId":"2849445589","productName":"칼리 라텍스 스위티 장난감 삑삑이 만득이 장난감 천연라텍스 강아지장난감 wk 쥬쥬베 스위티 라텍스","width":500,"height":500},{"discountPrice":2900,"linkUrl":"/pet/stores/100150961/products/4823093160","salePrice":9900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200216_243/1581781491639smzSm_JPEG/19143825199919813_2109833787.jpg","productId":"4823093160","productName":"강아지노즈워크 지능개발 퍼즐이팅 토이 원형 장난감 놀이","width":640,"height":640},{"discountPrice":5100,"linkUrl":"/pet/stores/100109333/products/2482369609","salePrice":14000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190926_12/1569489048171mOeMh_JPEG/6852436713582477_499121472.jpg","productId":"2482369609","productName":"강아지 장난감 휴지뽑기 쁘띠토이 당근","width":640,"height":640},{"discountPrice":4800,"linkUrl":"/pet/stores/100159372/products/4915696406","salePrice":16000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200503_261/1588482499801q3qW3_JPEG/25844042427357056_2009895256.jpg","productId":"4915696406","productName":"대왕 오리 삑삑이 인형 강아지 장난감","width":1000,"height":1000},{"discountPrice":600,"linkUrl":"/pet/stores/100117587/products/3736289235","salePrice":2850,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20181031_222/wiipet_1540975630613Rfjz7_JPEG/23694489459318589_411075201.jpg","productId":"3736289235","productName":"컬러선택가능 칼리 라텍스 고무공 스위티 삑삑이 국민장난감 만득이공 6칼러","width":640,"height":640},{"discountPrice":0,"linkUrl":"/pet/stores/100125728/products/4174050930","salePrice":18900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190207_272/support@biteme.co.kr_1549527315548QPrRq_JPEG/32158495202716176_335657378.jpg","productId":"4174050930","productName":"바잇미 강아지 두부 할멍이 호두과자 장난감 (삑삑/노즈워크/바스락)","width":900,"height":900},{"discountPrice":0,"linkUrl":"/pet/stores/100125728/products/4464611471","salePrice":6000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190424_234/support@biteme.co.kr_1556070772810f9JAw_JPEG/79377073435664734_299686193.jpg","productId":"4464611471","productName":"바잇미 강아지 젤리곰 장난감 (삑삑)","width":800,"height":800},{"discountPrice":5600,"linkUrl":"/pet/stores/100159372/products/4672572669","salePrice":14000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190918_45/1568778422117nSXRd_JPEG/6139160749250291_1213265927.jpg","productId":"4672572669","productName":"오리 슬리핑 애착 삑삑이 인형 보들보들 강아지장난감","width":640,"height":640},{"discountPrice":1800,"linkUrl":"/pet/stores/100117587/products/2771121697","salePrice":7500,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20180419_241/wiipet_1524129593056cJu4F_JPEG/47436752670092857_551233464.jpg","productId":"2771121697","productName":"[KONG] 삑삑이 테니스볼 3개세트 미니/소/중/대 세나개장난감 콩장난감","width":640,"height":640},{"discountPrice":4100,"linkUrl":"/pet/stores/100132412/products/2523467022","salePrice":7000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20180208_135/ytown_1518075390960rVbnH_JPEG/706570614740382_-1835042358.jpg","productId":"2523467022","productName":"강아지 장난감 캐릭터 바스락 토이","width":640,"height":640},{"discountPrice":2100,"linkUrl":"/pet/stores/100132412/products/2523421789","salePrice":4000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20190401_126/ytown_1554099947029YOdRH_JPEG/36818805876824016_1138578535.jpg","productId":"2523421789","productName":"강아지 장난감 미키 토이","width":750,"height":750},{"discountPrice":1000,"linkUrl":"/pet/stores/100337919/products/4640675460","salePrice":13900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200318_239/1584521224337F63qL_JPEG/21881962967721307_699572086.jpg","productId":"4640675460","productName":"강아지 노즈워크 장난감 IQ 훈련 돌돌이","width":1000,"height":1000},{"discountPrice":500,"linkUrl":"/pet/stores/100337919/products/4863680315","salePrice":7900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200414_69/1586847130270VzIOy_JPEG/24206964817300696_1208690408.jpg","productId":"4863680315","productName":"강아지 고양이 노즈워크 오뚜기 장난감 스낵볼 우주볼 분리불안","width":1000,"height":1000},{"discountPrice":0,"linkUrl":"/pet/stores/100501517/products/4751481372","salePrice":970,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20191205_62/1575554197006jv3fG_JPEG/12917585545385544_367875949.jpg","productId":"4751481372","productName":"재이앤펫 강아지 고양이 풋프린팅 강아지벨 애견벨","width":850,"height":850},{"discountPrice":0,"linkUrl":"/pet/stores/100125728/products/4882456351","salePrice":9900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200408_161/1586311476764GDVJU_JPEG/23671311284945297_1243122995.jpg","productId":"4882456351","productName":"바잇미 강아지 농산물 장난감 - 군밤 (노즈워크/삑삑)","width":800,"height":800},{"discountPrice":0,"linkUrl":"/pet/stores/100125728/products/4922128722","salePrice":9900,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200508_215/1588925933078KYdcu_JPEG/26289321592193666_743920278.jpg","productId":"4922128722","productName":"바잇미 치카치카 치약 치실로프 장난감 (삑삑/치실)","width":800,"height":800},{"discountPrice":0,"linkUrl":"/pet/stores/100161745/products/4916297980","salePrice":11000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200504_42/1588552854728Bae2V_JPEG/25914397356309362_1975544317.jpg","productId":"4916297980","productName":"강아지 노즈워크 양배추 장난감","width":1000,"height":1000},{"discountPrice":4980,"linkUrl":"/pet/stores/100166499/products/3061949136","salePrice":9960,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20180618_157/2016dec_1529292677611hlEeL_JPEG/11923857267117046_165684041.jpg","productId":"3061949136","productName":"대형견 장난감 라텍스공","width":846,"height":727},{"discountPrice":2500,"linkUrl":"/pet/stores/100603670/products/4855977776","salePrice":25000,"soldOut":false,"imageUrl":"http://shop1.phinf.naver.net/20200316_198/1584329181483dxsCW_JPEG/21692569996160733_440236013.jpg","productId":"4855977776","productName":"베이컨박스 삼계탕 한 그릇 플레이키트 (헌팅/삑삑이)","width":1000,"height":1000}],"banner":{"id":"1000032726","title":"펫윈도_생필품 특가전","mobileUrl":{"linkType":"MAIN","url":"https://m.swindow.naver.com/pet/specialEvent/detail/56662"},"pcUrl":{"linkType":"MAIN","url":"https://swindow.naver.com/pet/specialEvent/detail/56662"},"mobileImage":"https://shop-phinf.pstatic.net/20200520_5/1589941805006eYUzo_JPEG/95263829256970758_-1043462837.jpg","pcImage":"https://shop-phinf.pstatic.net/20200520_20/1589941807563kB9H0_JPEG/126546737985703473_-777087820.jpg","bgColor":"e9e9e9"},"hotdeal":{"message":"상품 데이터가 없습니다.","result":"FAIL"},"ssChannel":{"id":"100045370","channelServiceType":"WINDOW","channelExternalStatusType":"NORMAL","sellerStatusReasonType":"ETC","channelName":"아이펫케어","categoryId":"50000008","representImageInfoList":[{"imageUrl":"http://shop1.phinf.naver.net/20190111_64/ipatcare_1547187294854Axy0Y_JPEG/70494454471166863_1288590986.jpg","imageName":"70494454471166863_1288590986.jpg","width":1300,"height":1300,"fileSize":201786,"sortOrder":1,"originalFileName":"70494454471166863_1288590986.jpg","representative":false,"imageClass":"STORE_REPRESENTATIVE"}],"additionalImageInfoList":[{"imageUrl":"http://shop1.phinf.naver.net/20171123_267/ipatcare_15114249346846bmdX_JPEG/34732094298109814_1302236260.jpg","imageName":"34732094298109814_1302236260.jpg","width":1586,"height":1005,"fileSize":459929,"sortOrder":1,"originalFileName":"34732094298109814_1302236260.jpg","representative":false,"imageClass":"STORE_MAIN_VIEW"}],"deliveryDelayException":false,"channelAdmissionDate":"2017-08-11T05:51:13.637+0000","channelValidProductCount":397,"siteChannelInterlockYn":true,"talkAccountId":"wc9u7r","talkExposureYn":true,"description":"아이펫케어입니다.","salesTimeInfo":{"useClosed":false,"weekDayString":"","weekEndString":"","dayOffString":"연중무휴"},"contactInfo":{"displayTelNo":true,"disabledDomesticTelNo":false,"telNo":{"countryCode":"KOR","phoneNo":"01062929574","formattedNumber":"010-6292-9574"},"overseaTelNo":{"countryCode":"KOR","phoneNo":"","formattedNumber":""},"onlineSales":false,"offlineSales":false,"offlineStoreAddressInfo":{"overseas":false,"fullAddressInfo":"","hasRoadNameAddress":false,"hasJibunAddress":true},"additionalChargePersons":[{"name":"","phoneNumber":{"countryCode":"KOR","phoneNo":"","formattedNumber":""},"email":""}]},"bestShopYn":false,"exhibitionYn":true,"representNo":500088471,"representType":"DOMESTIC_BUSINESS","identity":"686-87-00538","identityAuthType":"NA","representName":"주식회사 아이펫","representativeName":"윤영성","representativeBirthDay":"1989-11-08T15:00:00.000+0000","categoryItemName":"전자상거래","businessType":"CORPORATION","declaredToOnlineMarkettingNumber":"2017-수원영통-0202","isOverSeaProductSales":true,"realNameCertificatedDate":"2017-03-28T07:59:26.973+0000","nation":"KOR","businessAddressInfo":{"address":"16512 경기도 수원시 영통구 광교중앙로 254 (하동, 드림타워3) 205호","basicAddress":"경기도 수원시 영통구 광교중앙로 254 (하동, ","jibunAddress":"경기도 수원시 영통구 하동","roadNameAddress":"드림타워3)","detailAddress":"205호","newZipCode":"16512","overseas":false,"fullAddressInfo":"(우 : 16512) 경기도 수원시 영통구 광교중앙로 254 (하동,  드림타워3) 205호","hasRoadNameAddress":true,"zipCode":"16512","hasJibunAddress":true},"accountNo":500088471,"defaultChannelNo":500088471,"productDeliveryType":"DELIVER","importType":"FORMALITY","advertiser":true,"advertizerSubscriptionDate":"2015-04-10T01:40:56.000+0000","mallSeq":280135,"accountAddType":"JOIN","domesticTelephoneNumberReported":false,"storeExposureInfo":{"exposureInfo":{"NAVERBLOG":["ipatcare"],"INSTAGRAM":["ipatcare"]}},"accountAdmissionDate":"2015-04-10T01:40:56.239+0000","accountValidProductCount":980,"accountExternalStatusType":"NORMAL","naverPayExternalStatusType":"NORMAL","chrgrEmail":"ipatcare@naver.com","naverPayNo":500088471,"payReferenceKey":"500088471","payType":"NAVER_PAY","couponPublicationAgreeStatusType":"COMPLETION","couponPublicationAgreeDate":"2017-12-17T17:23:57.765+0000","socialSecurityNumberGathering":false,"deliveryPlaceModifyYn":true,"claimRepealYn":true,"creditScore":6,"actionGrade":"SECOND","serviceSatisfactionGrade":false,"saleCount":5257,"csResponseRatio":0.84,"in2DaysDeliveryCompleteRatio":0.97,"averageSaleSatificationScore":4.78,"cumulationSaleAmount":440239620,"cumulationSaleCount":16137,"purchaseCustomerCountBy3Month":11701,"windowSubVertical":"PET","windowCategoryId":"10106","windowCategoryName":"펫","naverPayUseYn":true,"inquiryUseYn":true,"productInspectionSkipYn":false,"additionalAttribute":{"channelAlias":"","handleBrandNames":[]},"naSiteId":"sc_32148008820823941_ghd","thisDayDispatchBasisTime":"1800","fullUrl":"https://shopping.naver.com/outlink/storehome/100045370","mobileUrl":"https://m.shopping.naver.com/outlink/storehome/100045370","storeCategoryIds":["10106"],"logoImage":{"imageUrl":"http://shop1.phinf.naver.net/20190111_64/ipatcare_1547187294854Axy0Y_JPEG/70494454471166863_1288590986.jpg","imageName":"70494454471166863_1288590986.jpg","width":1300,"height":1300,"fileSize":201786,"sortOrder":1,"originalFileName":"70494454471166863_1288590986.jpg","representative":false,"imageClass":"STORE_REPRESENTATIVE"}},"windowProduct":{"brand":{"_id":"14111","name":"칼리"},"displayCategory":["11023","11023001","11023001006"],"productCategory":["12027","12027001","12027001010","12027001010002"],"menus":[],"standardSizes":[],"_id":"4883445820","attributes":[{"values":[{"_id":"10718505","name":"소리나는"},{"_id":"10718509","name":"물에뜨는"},{"_id":"10721460","name":"치석케어"}],"_id":"10013134","name":"기능"},{"values":[{"_id":"10718494","name":"고무/실리콘"}],"_id":"10013156","name":"소재"}],"averageReviewScore":0,"best":false,"channel":{"talkExposedYn":true,"bestShopYn":false,"inspectionBypassYn":false,"inquiryUseYn":true,"handleBrandNames":[],"testPayYn":false,"initialWords":[],"initialTypes":[],"initialIndexTypes":[],"hasHighRatingReview":false,"additionalImages":[],"createdAt":"2020-05-27T05:11:07.704Z","updatedAt":"2020-05-27T05:11:07.704Z","storeCategoryRelations":[{"storeCategory":["10106"],"channelId":"100045370","subVertical":"PET","inspectionStatus":"COMPLETE","vertical":"PET"}],"representBrands":[],"_id":"100045370","name":"아이펫케어","representativeImage":{"width":1586,"height":1005,"representativeImage":false,"_id":"5ecdf66bfbc3eb0027e0c768","imageUrl":"http://shop1.phinf.naver.net/20171123_267/ipatcare_15114249346846bmdX_JPEG/34732094298109814_1302236260.jpg","imageName":"34732094298109814_1302236260.jpg","fileSize":459929,"sortOrder":1,"originalFileName":"34732094298109814_1302236260.jpg","imageClassType":"BELONG_STORE_REPRESENTATIVE"},"logoImage":{"width":1300,"height":1300,"representativeImage":false,"_id":"5ecdf66bfbc3eb0027e0c769","imageUrl":"http://shop1.phinf.naver.net/20190111_64/ipatcare_1547187294854Axy0Y_JPEG/70494454471166863_1288590986.jpg","imageName":"70494454471166863_1288590986.jpg","fileSize":201786,"sortOrder":1,"originalFileName":"70494454471166863_1288590986.jpg","imageClassType":"BELONG_STORE_LOGO"},"talkAccountId":"wc9u7r","vertical":"PET","subVertical":"PET","inspectionStatus":"COMPLETE","storeCategory":["10106"],"alias":""},"contentText":"칼리 라텍스 베어Karlie Latex Bear오돌토돌 귀여운 동물 장난감 라텍스 베어는 안전한 라텍스 재질로 만들어져 강도와 탄력이 매우 좋습니다. 몸통을 누루면 삑삑♬ 소리가 나는 장난감 입니다. 이갈이를 하는 아이, 물고 뜯고 놀기 좋아하는 아이들에게 안성맞춤!제조사 칼리 Karlie / 독일 수입사 씨씨펫 원산지 중국 제품 사이즈Karlie독일 Bad Wunnenburg-Haaren 에 본사를 두고 있는 칼리는 디자인, 재료, 마무리 등 반려동물 과 반려인들의 편의를 충족해 주는 고품질의 제품을 추구합니다.","createdAt":"2020-04-08T10:53:43.888Z","deliveryAttributeType":"TODAY","exposure":true,"goods":"3295","images":[{"width":1000,"height":1000,"representativeImage":true,"imageUrl":"http://shop1.phinf.naver.net/20200408_266/1586342975386JBxQB_JPEG/23702809934705667_658754964.jpg","fileSize":134990,"sortOrder":0,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200408_293/15863429864824khE6_JPEG/23702821032331385_1943910107.jpg","fileSize":115131,"sortOrder":1,"imageClassType":"PRODUCT"},{"width":1000,"height":1000,"representativeImage":false,"imageUrl":"http://shop1.phinf.naver.net/20200408_57/1586342986687P8ekt_JPEG/23702821237292653_762877746.jpg","fileSize":126861,"sortOrder":2,"imageClassType":"PRODUCT"}],"ingredientExposure":null,"ingredientExposureAgreeDate":null,"inspectionStatus":"COMPLETE","martUpdatedAt":"2020-05-24T02:08:46.956Z","mobileDiscountPrice":6500,"mobileDiscountRate":0,"modelNumber":"칼리 라텍스 베어","name":"칼리 라텍스 베어 장난감","naverShoppingCategory":{"_id":"50006675","wholeId":"50000008>50000155>50006673>50006675","wholeName":"생활/건강>반려동물>강아지 장난감/훈련>장난감/토이","name":"장난감/토이"},"npay":true,"nvMid":82427969291,"pcDiscountPrice":6500,"pcDiscountRate":0,"productDisplayCategoryId":"11023001006","productNo":"4868143905","recentSaleCount":0,"salePrice":6500,"satisfactionPercent":0,"soldout":false,"storeKeepExclusiveProduct":false,"tags":[{"_id":"9486","name":"반려동물","type":"MANUAL"},{"_id":"176521","name":"반려동물용품","type":"MANUAL"},{"_id":"179682","name":"강아지토이","type":"MANUAL"},{"_id":"714117","name":"강아지장난감인형","type":"MANUAL"}],"talkPay":false,"totalReviewCount":0,"totalSaleCount":2,"updatedAt":"2020-05-01T10:27:32.693Z","reorderCount":0,"inspectedAt":"2020-04-09T02:31:04.004Z","popularScore":4.33,"deliveryFeeType":"PAID","standardColors":[]},"channelProductNos":["4883445819","4883445820"],"interestFreePlans":{"hasInterestFreePlans":true,"sellerBurden":{},"adminBurden":{"국민":[{"cardCorpName":"국민","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_KBbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000},{"cardCorpName":"국민","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_KBbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"10","minPayAmount":50000,"customerBurdenMonth":"1,2,3"}],"삼성":[{"cardCorpName":"삼성","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_samsung.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000},{"cardCorpName":"삼성","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_samsung.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"12","minPayAmount":50000,"customerBurdenMonth":"1,2,3,4,5"},{"cardCorpName":"삼성","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_samsung.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"10","minPayAmount":50000,"customerBurdenMonth":"1,2,3,4"},{"cardCorpName":"삼성","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_samsung.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"12","minPayAmount":50000,"customerBurdenMonth":"1,2,3,4,5\t"}],"NH":[{"cardCorpName":"NH","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_NH.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000}],"현대":[{"cardCorpName":"현대","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_hyundaicard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":10000},{"cardCorpName":"현대","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_hyundaicard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"7","minPayAmount":10000},{"cardCorpName":"현대","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_hyundaicard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"10","minPayAmount":300000}],"외환":[{"cardCorpName":"외환","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_hanacard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000}],"신한카드":[{"cardCorpName":"신한카드","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_shinhanbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000},{"cardCorpName":"신한카드","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_shinhanbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"10","minPayAmount":300000},{"cardCorpName":"신한카드","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_shinhanbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"12","minPayAmount":50000,"customerBurdenMonth":"1,2,3,4"}],"시티":[{"cardCorpName":"시티","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_citibank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000}],"하나":[{"cardCorpName":"하나","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_hanacard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000}],"BC카드":[{"cardCorpName":"BC카드","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_BCcard.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3,4,5,6","minPayAmount":50000}],"광주":[{"cardCorpName":"광주","cardCorpImageUrl":"https://ssl.pstatic.net/static.pay/u/card/logocard_KJbank.gif","managerFreeInterestBurdenType":"PG","freeInterestMonth":"2,3","minPayAmount":50000}]}},"displayCategory":{"id":"11023001006","name":"장난감","wholeId":"|11023|11023001|11023001006","categoryLevel":2,"wholeName":"|펫/상품별|강아지|장난감"},"proceedServiceCheck":{"showServiceCheckGuide":false},"matchedOtherProducts":[],"todayDispatch":{"thisDayDispatchYn":true,"thisDayDispatchBasisTime":"1800","possibleDispatchDays":["20200527","20200528"]},"hopeDelivery":false,"subVerticalAttributes":[],"togetherProducts":[],"coordiProducts":[],"similarProducts":[],"togetherProductsWithCoordinates":[]}
		#
		'''
		rtn = False

		try :
		
			for key in jsondata :
				rtn = True
				json_value = jsondata[key]
				
				if(key == 'viewAttributes') : # 상품정보
					sub_jsondata = jsondata['viewAttributes']
					for sub_key in sub_jsondata :
						if(sub_key == '제조사') : product_data.d_crw_brand2 = sub_jsondata[sub_key]
						elif(sub_key == '브랜드') : product_data.d_crw_brand1 = sub_jsondata[sub_key]
						elif(sub_key == '원산지') : product_data.d_crw_brand3 = sub_jsondata[sub_key]
						

				elif(key == 'productInfoProvidedNoticeView') : # 상품정보 제공공시
					sub_jsondata = jsondata['productInfoProvidedNoticeView']['basic']
					for sub_key in sub_jsondata :
						rtn_json = sub_jsondata[sub_key]
						for rtn_key in rtn_json :
							if(rtn_key == '제조자') or (rtn_key == '제조국') or (rtn_key == '생산자') : 
								if(rtn_json[rtn_key].find('상품상세') < 0 ) :
									if(rtn_key == '제조자') : 
										if( product_data.crw_brand2 == '') : product_data.d_crw_brand2 = rtn_json[rtn_key]
									elif(rtn_key == '제조국') : 
										if( product_data.crw_brand3 == '') : product_data.d_crw_brand3 = rtn_json[rtn_key]
									elif(rtn_key == '생산자') : 
										if( product_data.crw_brand4 == '') : product_data.d_crw_brand4 = rtn_json[rtn_key]
			
				
		except Exception as ex:
			__LOG__.Error('에러 : get_product_detail_data')
			__LOG__.Error(ex)
			pass
		
		return rtn
		
	
		
		
	def get_product_detail_content_data(self, product_data, jsondata):
		'''
		#
		# 
		# {"contentId":4883445820,"editorType":"SE3","textContent":"칼리 라텍스 베어Karlie Latex Bear오돌토돌 귀여운 동물 장난감 라텍스 베어는 안전한 라텍스 재질로 만들어져 강도와 탄력이 매우 좋습니다. 몸통을 누루면 삑삑♬ 소리가 나는 장난감 입니다.  이갈이를 하는 아이, 물고 뜯고 놀기 좋아하는  아이들에게 안성맞춤!제조사 칼리 Karlie / 독일 수입사 씨씨펫 원산지 중국 제품 사이즈Karlie독일 Bad Wunnenburg-Haaren 에 본사를 두고 있는 칼리는 디자인, 재료, 마무리 등 반려동물 과 반려인들의 편의를 충족해 주는 고품질의 제품을 추구합니다.","renderContent":"<div id=\"SEDOC-1586343210268--662962444\" class=\"se_doc_viewer se_body_wrap se_theme_transparent \" data-docversion=\"1.0\">\n<div class=\"se_doc_header_start\" id=\"SEDOC-1586343210268--662962444_se_doc_header_start\"></div>\n<!-- SE_DOC_HEADER_START -->\n<div id=\"SEDOC-1586343210268--662962444_viewer_head\" class=\"se_viewer_head\"></div>\n<div class=\"se_component_wrap\">\n</div>\n\n<!-- SE_DOC_HEADER_END -->\n<div class=\"se_doc_header_end\" id=\"SEDOC-1586343210268--662962444_se_doc_header_end\"></div>\n<div class=\"se_doc_contents_start\" id=\"SEDOC-1586343210268--662962444_se_doc_contents_start\"></div>\n<!-- SE_DOC_CONTENTS_START -->\n<div class=\"se_component_wrap sect_dsc __se_component_area\">\n    \n\n\n\n\n\n\n\n\n\n\n\n<div class=\"se_component se_sectionTitle \">\n    <div class=\"se_sectionArea se_align-center\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_H2 se_fw_bold\" style=\"color: ;\n                        text-decoration: inherit;\n                        font-style: inherit;\n                        \">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <h5 class=\"se_textarea\"><!-- SE3-TEXT { -->칼리 라텍스 베어<!-- } SE3-TEXT --></h5>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n\n\n\n<div class=\"se_component se_sectionTitle \">\n    <div class=\"se_sectionArea se_align-center\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_H2 \" style=\"color: ;\n                        text-decoration: inherit;\n                        font-style: inherit;\n                        \">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <h5 class=\"se_textarea\"><!-- SE3-TEXT { -->Karlie Latex Bear<!-- } SE3-TEXT --></h5>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:300px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_0_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20200408_55/1586343011348VDw0s_JPEG/%B8%DE%C0%CE_%B4%A9%B3%A2.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_0_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20200408_55/1586343011348VDw0s_JPEG/%B8%DE%C0%CE_%B4%A9%B3%A2.jpg\" width=\"300\" height=\"651\" data-attachment-id=\"Idokc3KIZeiyHrifzhq2NbtLAxQg\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n<div class=\"se_component se_horizontalLine line5\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"viewArea\">\n                <div class=\"se_horizontalLineView\">\n                    <div class=\"se_hr\"><hr></div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><b>오돌토돌 귀여운 동물 장난감</b><br><br><span>라텍스 베어는 안전한 라텍스 재질로 만들어져 강도와 탄력이 매우 좋습니다.<br></span><span>몸통을 누루면 삑삑♬ 소리가 나는 장난감 입니다.&nbsp;<br></span><span>이갈이를 하는 아이, 물고 뜯고 놀기 좋아하는&nbsp;<br></span><span>아이들에게 안성맞춤! </span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n<div class=\"se_component se_horizontalLine line5\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"viewArea\">\n                <div class=\"se_horizontalLineView\">\n                    <div class=\"se_hr\"><hr></div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:300px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_1_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20200408_149/1586343112251xDHxc_JPEG/%B5%DE%B8%E9_%B4%A9%B3%A2.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_1_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20200408_149/1586343112251xDHxc_JPEG/%B5%DE%B8%E9_%B4%A9%B3%A2.jpg\" width=\"300\" height=\"627\" data-attachment-id=\"ILAPLpu2AdWsoCSEsuYDHN-zwkCk\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><br></span><span></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:500px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_2_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20200408_120/1586343126205Rtrzz_JPEG/%BF%B7%B8%E9_%B4%A9%B3%A2.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_2_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20200408_120/1586343126205Rtrzz_JPEG/%BF%B7%B8%E9_%B4%A9%B3%A2.jpg\" width=\"500\" height=\"545\" data-attachment-id=\"IwPPCywx2aB366MgxJLJQenbJcSg\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><br></span><span><br></span><span><br></span><span></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-justify\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_3_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20181112_109/500088471_1542019587145N15N4_PNG/%BD%BA%C5%A9%B8%B0%BC%A6_2018-11-09_%BF%C0%C8%C4_8.31.16.png&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_3_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20181112_109/500088471_1542019587145N15N4_PNG/%BD%BA%C5%A9%B8%B0%BC%A6_2018-11-09_%BF%C0%C8%C4_8.31.16.png\" width=\"1714\" height=\"426\" data-attachment-id=\"IYQy8lzMuPLzqkrz1ti39tPZLRv8\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><br></span><span><br></span><span><br></span><span><b>제조사</b><br></span><span>칼리 Karlie / 독일</span><span><b></b><br></span><span><b></b><br></span><span><b>수입사</b><br></span><span>씨씨펫</span><span><b></b><br></span><span><b></b><br></span><span><b>원산지</b><br></span><span>중국</span><span><b></b><br></span><span><b></b><br></span><span><b>제품 사이즈</b><br></span><span><b></b></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:489px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_4_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20200408_276/1586343204274bOEc6_JPEG/%BB%E7%C0%CC%C1%EE.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_4_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20200408_276/1586343204274bOEc6_JPEG/%BB%E7%C0%CC%C1%EE.jpg\" width=\"489\" height=\"379\" data-attachment-id=\"IIhHRNYcV8SyJoTNv8wx_lwicTWo\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><br></span><span><b></b><br></span><span><b></b></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-justify\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_5_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20181109_291/500088471_15417582124992e08K_PNG/%BD%BA%C5%A9%B8%B0%BC%A6_2018-11-09_%BF%C0%C8%C4_6.31.04.png&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_5_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20181109_291/500088471_15417582124992e08K_PNG/%BD%BA%C5%A9%B8%B0%BC%A6_2018-11-09_%BF%C0%C8%C4_6.31.04.png\" width=\"1716\" height=\"884\" data-attachment-id=\"IHwo2Qp8UyEEuleQu0k5szkOptRk\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n\n\n\n<div class=\"se_component se_sectionTitle \">\n    <div class=\"se_sectionArea se_align-center\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_H2 se_fw_bold\" style=\"color: ;\n                        text-decoration: inherit;\n                        font-style: inherit;\n                        \">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <h5 class=\"se_textarea\"><!-- SE3-TEXT { -->Karlie<!-- } SE3-TEXT --></h5>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><b></b><br></span><span><b>독일 Bad Wunnenburg-Haaren 에 본사를 두고 있는</b><br></span><span><b>칼리는 디자인, 재료, 마무리 등 반려동물 과 반려인들의 편의를 충족해 주는 고품질의 제품을 추구합니다.</b><br></span><span><b></b><br></span><span><br></span><span></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\t\t<div class=\"se_component se_image default\">\n\t\t\t<div class=\"se_sectionArea se_align-center\">\n\t\t\t\t<div class=\"se_editArea\">\n\t\t\t\t\t<div class=\"se_viewArea\" style=\"max-width:400px\">\n        <a onclick=\"return false;\" class=\"se_mediaArea __se_image_link __se_link\" data-linktype=\"img\" data-linkdata=\"{&quot;imgId&quot;:&quot;SEDOC-1586343210268--662962444_image_6_img&quot;,&quot;src&quot;:&quot;http://bshop.phinf.naver.net/20181109_52/500088471_1541758360679CCdfB_JPEG/%B7%CE%B0%ED.jpg&quot;,&quot;linkUse&quot;:&quot;false&quot;,&quot;link&quot;:&quot;&quot;}\">\n                            <img id=\"SEDOC-1586343210268--662962444_image_6_img\" class=\"se_mediaImage __se_img_el\" src=\"http://bshop.phinf.naver.net/20181109_52/500088471_1541758360679CCdfB_JPEG/%B7%CE%B0%ED.jpg\" width=\"400\" height=\"116\" data-attachment-id=\"I-6eHJGvGv9tkT7a32oA3oJoCeY0\" alt=\"\">\n        \n        </a>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n    \n\n\n\n\n\n\n\n\n<div class=\"se_component se_paragraph default\">\n    <div class=\"se_sectionArea\">\n        <div class=\"se_editArea\">\n            <div class=\"se_viewArea se_ff_nanumgothic se_fs_T3 se_align-center\">\n                <div class=\"se_editView\">\n                    <div class=\"se_textView\">\n                        <p class=\"se_textarea\"><!-- SE3-TEXT { --><span><br></span><span><b></b><br></span><span><b></b></span><!-- } SE3-TEXT --></p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n</div>\n<!-- SE_DOC_CONTENTS_END -->\n<div class=\"__se_doc_title_end\" id=\"se_doc_contents_end\"></div>\n<div id=\"SEDOC-1586343210268--662962444_se_doc_footer\" class=\"se_doc_footer\"></div>\n</div>\n"}
		#
		'''
		rtn = False
		try :
			detail_page_txt = []
			detail_page_img = []
				
			if('textContent' in jsondata ) : detail_page_txt.append( jsondata['textContent'].strip() ) 
			
			if('renderContent' in jsondata ) : 
				inner_str = jsondata['renderContent']
				inner_html = inner_str.replace('\\n"','' ).replace('\\n','\n' ).replace('\\"','"' ).replace('\\/','/' ).replace('\\t','' ).replace('&quot;',' ' ).replace('\\xa0!',' ').replace('\\x3C!','<!').replace('\\>','>').strip()
				html = '''<html lang="ko"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
						<body>''' + inner_html + '''</body></html>'''
				soup = bs4.BeautifulSoup(html, 'lxml')
				
				# 순수한 이미지 요소 추출
				img_list = soup.find_all('img')
				for img_ctx in img_list :
					if('src' in img_ctx.attrs) : 
						img_src = img_ctx.attrs['src']
						img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
						if(0 != img_link.find('https://proxy.smartstore.naver.com/') ) : detail_page_img.append( self.get_hangul_url_convert( img_link )  )
						
			
				# 링크와 같이 있는 이미지 요소 추출
				img_list = soup.find_all('a', {'data-linktype':'img'})
				for img_ctx in img_list :
					if('data-linkdata' in img_ctx.attrs) : 
						img_text = img_ctx.attrs['data-linkdata']
						img_text_list = img_text.split(', src :')
						if(len(img_text_list) == 2) :
							tmp_img_list = img_text_list[1].strip().split(',')
							img_src = tmp_img_list[0].strip()
							img_link = self.set_img_url( self.BASIC_IMAGE_URL, img_src )
							if(0 != img_link.find('https://proxy.smartstore.naver.com/') ) : detail_page_img.append( self.get_hangul_url_convert( img_link )  )
								
			self.set_detail_page( product_data, detail_page_txt, detail_page_img)
			
				
		except Exception as ex:
			__LOG__.Error('에러 : get_product_detail_content_data')
			__LOG__.Error(ex)
			pass
		
		return rtn


		
	def process_product_detail(self, product_url , product_data ):
	
		rtn = False
		resptext = ''
		rtn_productNo = ''
		
		try :

			crw_goods_code = product_data.crw_goods_code
			__LOG__.Trace("-----------------------------------------------------")
			if( config.__DEBUG__ ) : __LOG__.Trace('product : %s' % ( product_url ) )

			
			time.sleep(self.WAIT_TIME*2)
			URL = self.get_url_product_detail(crw_goods_code)
			header = self.get_header_product_detail(product_url)
			
			resp = None
			resp = requests.get( URL, headers=header )

			if( resp.status_code != 200 ) :
				__LOG__.Error(' %d :  %s ' % ( resp.status_code, URL) )
			else :
				resptext = resp.text
				#__LOG__.Trace( resptext )
				jsondata = json.loads(resptext)
				self.get_product_detail_data( product_data, jsondata )
				
			# 상세페이지의 텍스트와 이미지 정보를 추가적으로 갖고 오는 질의를 한번 더 함.
			if(product_data.product_no != '') :
				time.sleep(self.WAIT_TIME*2)
				URL = self.get_url_product_detail_content( crw_goods_code , product_data.product_no )
				header = self.get_header_product_detail_content()

				resp_sub = None
				resp_sub = requests.get( URL, headers=header )

				if( resp_sub.status_code != 200 ) :
					__LOG__.Error(' %d :  %s ' % ( resp.status_code, URL) )
				else :
					resptext = resp_sub.text
					#__LOG__.Trace( resptext )
					jsondata = json.loads(resptext)
					rtn = self.get_product_detail_content_data( product_data, jsondata )
					
					self.process_product_detail_api(product_data)
			
		except Exception as ex:
			__LOG__.Error( "process_product_detail Error 발생 " )
			__LOG__.Error( ex )
			pass
		

		self.PRODUCT_URL_HASH[product_url] = product_data
		
		return rtn	
		
	
		
		
	

				
	'''
	######################################################################
	# 메인 함수
	######################################################################
	''' 
		
	def main(self, site_home, brd_id):

		__LOG__.Trace("***********************************************************")
		__LOG__.Trace("Start %s ....." % ( site_home) )
		__LOG__.Trace("***********************************************************")
		
		try :
			
			
			self.set_site_home( site_home )
			self.set_store_id( site_home )
			
			self.init_mall(brd_id)
			
			# 카테고리 리스트 갖고 오기
			self.process_category_list()
			
			#페이지 URL 갖고 오기 - 무시
			################ self.process_page_list()
			
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
		

	
if __name__ == '__main__':
	
	LOG_NAME = "%s/%s.log" % (config.LOG_PATH , os.path.basename(sys.argv[0]))
	Log.Init(Log.CRotatingLog(LOG_NAME, 10000000, 10))

	BRD_ID_HASH = __API__.get_storelist('shopping.naver.com')		
	app = shopnaver()
	
	for app_url in BRD_ID_HASH.keys() :
		if(app.SHUTDOWN) : break
		brd_id = BRD_ID_HASH[app_url]
		app.main(app_url, brd_id)
		
	
	
	